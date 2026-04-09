from flask import Blueprint, current_app, jsonify, request

tasks_bp = Blueprint("tasks", __name__)


def _error(message, status_code, detalle=None):
    payload = {"error": message, "codigo": status_code}
    if detalle:
        payload["detalle"] = detalle
    return jsonify(payload), status_code


@tasks_bp.route("/tareas", methods=["GET"])
def listar_tareas():
    return jsonify(current_app.config["TASK_SERVICE"].listar()), 200


@tasks_bp.route("/tareas/<int:task_id>", methods=["GET"])
def obtener_tarea(task_id):
    tarea = current_app.config["TASK_SERVICE"].obtener(task_id)
    if not tarea:
        return _error("Tarea no encontrada", 404)
    return jsonify(tarea), 200


@tasks_bp.route("/tareas", methods=["POST"])
def crear_tarea():
    data = request.get_json(silent=True) or {}
    texto = (data.get("texto") or "").strip()
    if not texto:
        return _error("El campo 'texto' es obligatorio", 400)

    nueva_tarea = current_app.config["TASK_SERVICE"].agregar(texto)
    return jsonify(nueva_tarea), 201


@tasks_bp.route("/tareas/<int:task_id>", methods=["PUT", "PATCH"])
def actualizar_tarea(task_id):
    service = current_app.config["TASK_SERVICE"]
    if not service.obtener(task_id):
        return _error("Tarea no encontrada", 404)

    data = request.get_json(silent=True) or {}
    texto = None
    completada = None

    if "texto" in data:
        texto = (data.get("texto") or "").strip()
        if not texto:
            return _error("El campo 'texto' no puede estar vacio", 400)

    if "completada" in data:
        if not isinstance(data["completada"], bool):
            return _error("El campo 'completada' debe ser booleano", 400)
        completada = data["completada"]

    tarea = service.actualizar(task_id, texto=texto, completada=completada)
    return jsonify(tarea), 200


@tasks_bp.route("/tareas/<int:task_id>/completar", methods=["PATCH"])
def completar_tarea(task_id):
    tarea = current_app.config["TASK_SERVICE"].completar(task_id)
    if not tarea:
        return _error("Tarea no encontrada", 404)
    return jsonify(tarea), 200


@tasks_bp.route("/tareas/<int:task_id>", methods=["DELETE"])
def eliminar_tarea(task_id):
    eliminado = current_app.config["TASK_SERVICE"].eliminar(task_id)
    if not eliminado:
        return _error("Tarea no encontrada", 404)
    return jsonify({"mensaje": "Tarea eliminada"}), 200
