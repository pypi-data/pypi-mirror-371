from pathlib import Path

from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage

from minitap.mobile_use.agents.orchestrator.types import OrchestratorOutput, OrchestratorStatus
from minitap.mobile_use.agents.planner.utils import (
    all_completed,
    complete_current_subgoal,
    fail_current_subgoal,
    get_current_subgoal,
    nothing_started,
    start_next_subgoal,
)
from minitap.mobile_use.context import MobileUseContext
from minitap.mobile_use.graph.state import State
from minitap.mobile_use.services.llm import get_llm
from minitap.mobile_use.utils.decorators import wrap_with_callbacks
from minitap.mobile_use.utils.logger import get_logger

logger = get_logger(__name__)


class OrchestratorNode:
    def __init__(self, ctx: MobileUseContext):
        self.ctx = ctx

    @wrap_with_callbacks(
        before=lambda: logger.info("Starting Orchestrator Agent..."),
        on_success=lambda _: logger.success("Orchestrator Agent"),
        on_failure=lambda _: logger.error("Orchestrator Agent"),
    )
    async def __call__(self, state: State):
        if nothing_started(state.subgoal_plan):
            state.subgoal_plan = start_next_subgoal(state.subgoal_plan)
            new_subgoal = get_current_subgoal(state.subgoal_plan)
            return state.sanitize_update(
                ctx=self.ctx,
                update={
                    "agents_thoughts": [f"Starting the first subgoal: {new_subgoal}"],
                    "subgoal_plan": state.subgoal_plan,
                },
            )

        current_subgoal = get_current_subgoal(state.subgoal_plan)

        if not current_subgoal:
            return state.sanitize_update(
                ctx=self.ctx,
                update={"agents_thoughts": ["No subgoal to go for."]},
            )

        system_message = Template(
            Path(__file__).parent.joinpath("orchestrator.md").read_text(encoding="utf-8")
        ).render(platform=self.ctx.device.mobile_platform.value)
        human_message = Template(
            Path(__file__).parent.joinpath("human.md").read_text(encoding="utf-8")
        ).render(
            initial_goal=state.initial_goal,
            subgoal_plan="\n".join(str(s) for s in state.subgoal_plan),
            current_subgoal=str(current_subgoal),
            agent_thoughts="\n".join(state.agents_thoughts),
        )
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=human_message),
        ]

        llm = get_llm(ctx=self.ctx, name="orchestrator", temperature=1)
        llm = llm.with_structured_output(OrchestratorOutput)
        response: OrchestratorOutput = await llm.ainvoke(messages)  # type: ignore

        if response.status == OrchestratorStatus.CONTINUE:
            state.subgoal_plan = complete_current_subgoal(state.subgoal_plan)
            thoughts = [response.reason]

            if all_completed(state.subgoal_plan):
                logger.success("All the subgoals have been completed successfully.")
                return state.sanitize_update(
                    ctx=self.ctx,
                    update={
                        "subgoal_plan": state.subgoal_plan,
                        "agents_thoughts": thoughts,
                    },
                )
            state.subgoal_plan = start_next_subgoal(state.subgoal_plan)
            new_subgoal = get_current_subgoal(state.subgoal_plan)
            thoughts.append(f"==== NEXT SUBGOAL: {new_subgoal} ====")
            return state.sanitize_update(
                ctx=self.ctx,
                update={
                    "agents_thoughts": thoughts,
                    "subgoal_plan": state.subgoal_plan,
                },
            )

        elif response.status == OrchestratorStatus.REPLAN:
            thoughts = [response.reason]
            state.subgoal_plan = fail_current_subgoal(state.subgoal_plan)
            thoughts.append("==== END OF PLAN, REPLANNING ====")
            return state.sanitize_update(
                ctx=self.ctx,
                update={
                    "agents_thoughts": thoughts,
                    "subgoal_plan": state.subgoal_plan,
                },
            )

        return state.sanitize_update(
            ctx=self.ctx,
            update={
                "agents_thoughts": [response.reason],
            },
        )
