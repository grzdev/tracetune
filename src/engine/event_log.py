import json
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ToolEvent(BaseModel):
    """Tier 2: Granular tool invocation event."""
    step: int
    tool_name: str
    arguments: Dict[str, Any]
    output: Dict[str, Any]
    is_error: bool = False
    timestamp: float = Field(default_factory=time.time)

class StateTransitionEvent(BaseModel):
    """Tier 1: High-level agent state transition event."""
    step: int
    thought: str
    intent: str
    state_before: str
    state_after: str
    timestamp: float = Field(default_factory=time.time)

class EventLog(BaseModel):
    """
    Two-Tier EventLog Trajectory Substrate matching Lexsi AgentTune standards.
    Tier 1 captures semantic intent & plan transitions.
    Tier 2 captures granular tool execution tokens and feedback.
    """
    session_id: str
    task_prompt: str
    target_file: Optional[str] = None
    transitions: List[StateTransitionEvent] = Field(default_factory=list)
    tool_events: List[ToolEvent] = Field(default_factory=list)
    final_report: Optional[Dict[str, Any]] = None
    is_completed: bool = False
    total_steps: int = 0
    created_at: float = Field(default_factory=time.time)

    def log_transition(self, step: int, thought: str, intent: str, state_before: str, state_after: str):
        event = StateTransitionEvent(
            step=step,
            thought=thought,
            intent=intent,
            state_before=state_before,
            state_after=state_after
        )
        self.transitions.append(event)

    def log_tool_event(self, step: int, tool_name: str, arguments: Dict[str, Any], output: Dict[str, Any]):
        is_error = "error" in output or output.get("verified") is False
        event = ToolEvent(
            step=step,
            tool_name=tool_name,
            arguments=arguments,
            output=output,
            is_error=is_error
        )
        self.tool_events.append(event)
        self.total_steps = step

    def to_sft_format(self) -> Dict[str, Any]:
        """Projects trajectory into a conversational SFT format for fine-tuning."""
        messages = [
            {"role": "system", "content": "You are TraceTune, an autonomous code and security triage agent. Use the available tools to inspect repositories, verify evidence, and file verified security triage reports."},
            {"role": "user", "content": self.task_prompt}
        ]

        for step in range(1, self.total_steps + 1):
            t1 = next((t for t in self.transitions if t.step == step), None)
            t2 = next((e for e in self.tool_events if e.step == step), None)

            thought_text = t1.thought if t1 else ""
            if t2:
                assistant_content = f"{thought_text}\nAction: {t2.tool_name}({json.dumps(t2.arguments)})"
                messages.append({"role": "assistant", "content": assistant_content})
                tool_content = f"Observation: {json.dumps(t2.output)}"
                messages.append({"role": "user", "content": tool_content})

        if self.final_report:
            messages.append({
                "role": "assistant",
                "content": f"Final Report Filed:\n{json.dumps(self.final_report, indent=2)}"
            })

        return {"messages": messages, "session_id": self.session_id}

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
