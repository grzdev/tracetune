import uuid
from typing import Dict, Any, Optional
from src.tools.executor import ToolExecutor
from src.engine.event_log import EventLog
from src.engine.simulator import ModelSimulator
from src.config import MAX_STEPS_PER_RUN

class AgentRuntime:
    """
    TraceTune unified agent runtime matching AgentTune orchestration lifecycle.
    Orchestrates tool dispatch, trajectory recording, and error recovery.
    """

    def __init__(self, mode: str = "tuned", root_dir=None):
        self.mode = mode
        self.executor = ToolExecutor(root_dir=root_dir) if root_dir else ToolExecutor()
        self.simulator = ModelSimulator(mode=mode)

    def run(self, task_prompt: str, target_file: Optional[str] = None, max_steps: int = MAX_STEPS_PER_RUN) -> EventLog:
        """
        Executes an autonomous investigation session and returns the complete EventLog.
        """
        session_id = f"tt-{uuid.uuid4().hex[:8]}"
        log = EventLog(
            session_id=session_id,
            task_prompt=task_prompt,
            target_file=target_file
        )

        history = []
        is_completed = False

        for step in range(1, max_steps + 1):
            # 1. Model policy generates thought, intent, and proposed tool action
            action = self.simulator.generate_next_action(
                task=task_prompt,
                target_file=target_file,
                history=history,
                step=step
            )

            thought = action.get("thought", "")
            intent = action.get("intent", "EXECUTE_TOOL")
            state_before = action.get("state_before", "ACTIVE")
            state_after = action.get("state_after", "EVALUATING")
            tool_name = action.get("tool_name")
            tool_args = action.get("arguments", {})

            # 2. Record Tier 1 State Transition
            log.log_transition(
                step=step,
                thought=thought,
                intent=intent,
                state_before=state_before,
                state_after=state_after
            )

            # 3. Execute tool via safe executor
            tool_output = self.executor.execute_tool(tool_name, tool_args)

            # 4. Record Tier 2 Tool Invocation
            log.log_tool_event(
                step=step,
                tool_name=tool_name,
                arguments=tool_args,
                output=tool_output
            )

            history.append({
                "step": step,
                "tool_name": tool_name,
                "arguments": tool_args,
                "output": tool_output
            })

            # Check for completion
            if tool_name == "submit_triage_report" and "report" in tool_output:
                log.final_report = tool_output["report"]
                log.is_completed = True
                is_completed = True
                break

        if not is_completed and log.tool_events:
            log.is_completed = False

        return log
