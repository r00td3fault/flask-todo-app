def test_crud_basico(client):
    crear = client.post("/tareas", json={"texto": "Comprar cafe"})
    assert crear.status_code == 201
    task = crear.get_json()
    task_id = task["id"]

    listar = client.get("/tareas")
    assert listar.status_code == 200
    assert len(listar.get_json()) == 1

    actualizar = client.patch(f"/tareas/{task_id}", json={"texto": "Comprar cafe molido"})
    assert actualizar.status_code == 200
    assert actualizar.get_json()["texto"] == "Comprar cafe molido"

    completar = client.patch(f"/tareas/{task_id}/completar")
    assert completar.status_code == 200
    assert completar.get_json()["completada"] is True

    eliminar = client.delete(f"/tareas/{task_id}")
    assert eliminar.status_code == 200

    listado_final = client.get("/tareas")
    assert listado_final.get_json() == []


def test_validacion_payload(client):
    resp = client.post("/tareas", json={"texto": ""})
    assert resp.status_code == 400
    body = resp.get_json()
    assert "error" in body
    assert "codigo" in body
