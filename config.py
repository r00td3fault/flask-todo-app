import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent
    TASKS_FILE = Path(os.getenv("TASKS_FILE", BASE_DIR / "tareas.json"))
