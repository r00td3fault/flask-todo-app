import json

from app.repositories.json_task_repository import JsonTaskRepository


def test_repository_crea_ids_incrementales(tmp_path):
    repo = JsonTaskRepository(tmp_path / "tareas.json")
    t1 = repo.add_task("Tarea 1")
    t2 = repo.add_task("Tarea 2")

    assert t1.id == 1
    assert t2.id == 2


def test_repository_persistencia_en_json(tmp_path):
    data_file = tmp_path / "tareas.json"
    repo = JsonTaskRepository(data_file)
    repo.add_task("Persistida")

    content = json.loads(data_file.read_text(encoding="utf-8"))
    assert isinstance(content, list)
    assert content[0]["texto"] == "Persistida"
