import sys
from pathlib import Path

import pytest

# Asegura import estable del package `app` al correr pytest desde cualquier cwd.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app


@pytest.fixture
def tasks_file(tmp_path):
    return Path(tmp_path) / "tareas_test.json"


@pytest.fixture
def app(tasks_file):
    app = create_app({"TESTING": True, "TASKS_FILE": tasks_file})
    return app


@pytest.fixture
def client(app):
    return app.test_client()
