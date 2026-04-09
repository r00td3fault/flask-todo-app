import logging
import os
from pathlib import Path

from flask import Flask

from app.repositories.json_task_repository import JsonTaskRepository
from app.routes.tasks import tasks_bp
from app.routes.web import web_bp
from app.services.task_service import TaskService
from config import Config


def create_app(test_config=None):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    else:
        app.config["TASKS_FILE"] = Path(os.getenv("TASKS_FILE", app.config["TASKS_FILE"]))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    repository = JsonTaskRepository(app.config["TASKS_FILE"])
    app.config["TASK_SERVICE"] = TaskService(repository)

    app.register_blueprint(web_bp)
    app.register_blueprint(tasks_bp)
    return app
