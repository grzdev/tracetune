import json
from pathlib import Path
from typing import List
from src.engine.event_log import EventLog
from src.config import DATASET_DIR

def export_trajectories_jsonl(trajectories: List[EventLog], file_path: Path = None) -> Path:
    """Exports trajectories into AgentTune-ready EventLog JSONL file."""
    if file_path is None:
        file_path = DATASET_DIR / "tracetune_trajectories.jsonl"

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        for t in trajectories:
            f.write(json.dumps(t.to_dict()) + "\n")

    return file_path

def export_sft_dataset(trajectories: List[EventLog], file_path: Path = None) -> Path:
    """Exports trajectories into conversational SFT format JSONL for direct fine-tuning."""
    if file_path is None:
        file_path = DATASET_DIR / "tracetune_sft.jsonl"

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        for t in trajectories:
            f.write(json.dumps(t.to_sft_format()) + "\n")

    return file_path
