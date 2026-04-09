import json
import threading
from pathlib import Path

from app.models.task import Task


class JsonTaskRepository:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self._lock = threading.Lock()
        self._tasks_by_id = {}
        self._next_id = 1
        self._load()

    def _load(self):
        with self._lock:
            if not self.file_path.exists():
                self._tasks_by_id = {}
                self._next_id = 1
                return

            try:
                data = json.loads(self.file_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                data = []

            if not isinstance(data, list):
                data = []

            tasks = {}
            for item in data:
                if not isinstance(item, dict):
                    continue
                task_id = item.get("id")
                texto = item.get("texto")
                completada = item.get("completada", False)
                if isinstance(task_id, int) and isinstance(texto, str) and isinstance(completada, bool):
                    tasks[task_id] = Task(id=task_id, texto=texto, completada=completada)

            self._tasks_by_id = tasks
            self._next_id = (max(tasks.keys()) + 1) if tasks else 1

    def _save(self):
        payload = [task.to_dict() for task in self.list_tasks()]
        tmp_path = self.file_path.with_suffix(".tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp_path.replace(self.file_path)

    def list_tasks(self):
        return [self._tasks_by_id[task_id] for task_id in sorted(self._tasks_by_id.keys())]

    def get_task(self, task_id):
        return self._tasks_by_id.get(task_id)

    def add_task(self, texto):
        with self._lock:
            task = Task(id=self._next_id, texto=texto, completada=False)
            self._tasks_by_id[task.id] = task
            self._next_id += 1
            self._save()
            return task

    def update_task(self, task_id, texto=None, completada=None):
        with self._lock:
            task = self._tasks_by_id.get(task_id)
            if not task:
                return None

            if texto is not None:
                task.texto = texto
            if completada is not None:
                task.completada = completada

            self._save()
            return task

    def complete_task(self, task_id):
        with self._lock:
            task = self._tasks_by_id.get(task_id)
            if not task:
                return None

            task.completada = True
            self._save()
            return task

    def delete_task(self, task_id):
        with self._lock:
            task = self._tasks_by_id.pop(task_id, None)
            if not task:
                return False
            self._save()
            return True
