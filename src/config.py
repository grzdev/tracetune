from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
SANDBOX_DIR = SRC_DIR / "tools" / "sandbox"
DATASET_DIR = BASE_DIR / "data"
EVAL_DIR = BASE_DIR / "eval_results"

# Ensure data directories exist
DATASET_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL_NAME = "CohereLabs/tiny-aya-fire"
MAX_STEPS_PER_RUN = 7
MAX_SNIPPET_LINES = 100
