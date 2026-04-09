from flask import Blueprint, current_app, render_template

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def home():
    tareas = current_app.config["TASK_SERVICE"].listar_para_vista()
    return render_template("index.html", tareas=tareas)
