import logging


class TaskService:
    def __init__(self, repository):
        self.repository = repository
        self.logger = logging.getLogger("task_service")

    def listar(self):
        return [task.to_dict() for task in self.repository.list_tasks()]

    def listar_para_vista(self):
        return sorted(self.listar(), key=lambda t: t["completada"])

    def obtener(self, task_id):
        task = self.repository.get_task(task_id)
        return task.to_dict() if task else None

    def agregar(self, texto):
        task = self.repository.add_task(texto).to_dict()
        self.logger.info("tarea_creada id=%s", task["id"])
        return task

    def actualizar(self, task_id, texto=None, completada=None):
        task = self.repository.update_task(task_id, texto=texto, completada=completada)
        if task:
            self.logger.info("tarea_actualizada id=%s", task_id)
        return task.to_dict() if task else None

    def completar(self, task_id):
        task = self.repository.complete_task(task_id)
        if task:
            self.logger.info("tarea_completada id=%s", task_id)
        return task.to_dict() if task else None

    def eliminar(self, task_id):
        ok = self.repository.delete_task(task_id)
        if ok:
            self.logger.info("tarea_eliminada id=%s", task_id)
        return ok
