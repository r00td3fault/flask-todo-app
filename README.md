# Gestor de Tareas Flask

Aplicacion de tareas con CRUD, interfaz web y persistencia en archivo JSON.

## Requisitos

- Python 3.10+ (recomendado)

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar en desarrollo

```bash
python run.py
```

Tambien funciona:

```bash
python app.py
```

Abrir en navegador: `http://127.0.0.1:5000`

## Estructura

- `app/__init__.py`: factory Flask y registro de blueprints.
- `app/routes/web.py`: vistas HTML.
- `app/routes/tasks.py`: API REST de tareas.
- `app/services/task_service.py`: logica de negocio.
- `app/repositories/json_task_repository.py`: persistencia JSON (atomica y con lock).
- `templates/index.html`: UI.
- `static/js/app.js`: interacciones frontend sin recargar pagina.

## Variables de entorno

- `TASKS_FILE`: ruta del archivo JSON para persistencia (default: `tareas.json`).

Ejemplo:

```bash
TASKS_FILE=/tmp/mis_tareas.json python run.py
```

## Tests

```bash
pytest -q
```

## Flujos de la aplicacion

### Endpoints API

| Metodo | Ruta | Descripcion | Body esperado | Respuesta |
| --- | --- | --- | --- | --- |
| `GET` | `/` | Renderiza la vista principal HTML | - | `200` HTML |
| `GET` | `/tareas` | Lista todas las tareas | - | `200` JSON array |
| `GET` | `/tareas/{id}` | Obtiene una tarea por id | - | `200` JSON / `404` error |
| `POST` | `/tareas` | Crea una nueva tarea | `{"texto":"..."}` | `201` JSON / `400` error |
| `PATCH` | `/tareas/{id}` | Actualiza texto y/o estado | `{"texto":"..."}` o `{"completada":true}` | `200` JSON / `400` / `404` |
| `PUT` | `/tareas/{id}` | Actualiza texto y/o estado | `{"texto":"..."}` o `{"completada":true}` | `200` JSON / `400` / `404` |
| `PATCH` | `/tareas/{id}/completar` | Marca una tarea como completada | - | `200` JSON / `404` error |
| `DELETE` | `/tareas/{id}` | Elimina una tarea | - | `200` JSON / `404` error |

### Arquitectura general

```mermaid
flowchart LR
    Browser[Browser]
    JsClient[app.js]
    FlaskApp[Flask create_app]
    WebRoutes[web_bp routes]
    ApiRoutes[tasks_bp routes]
    TaskService[TaskService]
    JsonRepo[JsonTaskRepository]
    TasksJson[tareas.json]

    Browser --> JsClient
    Browser --> FlaskApp
    FlaskApp --> WebRoutes
    FlaskApp --> ApiRoutes
    WebRoutes --> TaskService
    ApiRoutes --> TaskService
    TaskService --> JsonRepo
    JsonRepo --> TasksJson
    JsonRepo --> TaskService
    TaskService --> WebRoutes
    TaskService --> ApiRoutes
    WebRoutes --> Browser
    ApiRoutes --> JsClient
```

### Arranque de la app

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Entry as app.py_or_run.py
    participant Factory as create_app
    participant Config as Config
    participant Repo as JsonTaskRepository
    participant Service as TaskService
    participant Flask as FlaskApp

    Dev->>Entry: python app.py (o run.py)
    Entry->>Factory: create_app()
    Factory->>Config: load Config.TASKS_FILE
    Factory->>Repo: JsonTaskRepository(TASKS_FILE)
    Repo->>Repo: _load() desde tareas.json
    Factory->>Service: TaskService(repo)
    Factory->>Flask: register blueprints (web_bp, tasks_bp)
    Factory-->>Entry: app lista
    Entry->>Flask: app.run()
```

### Flujo de pagina inicial

```mermaid
sequenceDiagram
    participant Browser as Browser
    participant Flask as FlaskRouter
    participant Web as web_bp.home
    participant Service as TaskService
    participant Repo as JsonTaskRepository
    participant Template as index.html

    Browser->>Flask: GET /
    Flask->>Web: dispatch "/"
    Web->>Service: listar_para_vista()
    Service->>Service: listar()
    Service->>Repo: list_tasks()
    Repo-->>Service: List[Task]
    Service-->>Web: List[dict] ordenada por completada
    Web->>Template: render_template("index.html", tareas)
    Template-->>Browser: HTML response 200
```

### Crear tarea (POST /tareas)

```mermaid
sequenceDiagram
    participant User as Usuario
    participant Js as app.js
    participant Api as tasks_bp.crear_tarea
    participant Service as TaskService
    participant Repo as JsonTaskRepository
    participant File as tareas.json

    User->>Js: Submit formulario nueva tarea
    Js->>Api: POST /tareas {texto}
    Api->>Api: validar texto
    Api->>Service: agregar(texto)
    Service->>Repo: add_task(texto)
    Repo->>Repo: crear Task(id=next_id)
    Repo->>Repo: guardar en _tasks_by_id
    Repo->>Repo: _save() atomico
    Repo->>File: write tmp + replace
    Repo-->>Service: Task
    Service-->>Api: dict tarea
    Api-->>Js: 201 JSON tarea
    Js->>Js: renderTaskItem(task)
    Js->>Js: append al DOM sin reload
```

### Actualizar tarea (PATCH /tareas/{id})

```mermaid
sequenceDiagram
    participant User as Usuario
    participant Js as app.js
    participant Api as tasks_bp.actualizar_tarea
    participant Service as TaskService
    participant Repo as JsonTaskRepository
    participant File as tareas.json

    User->>Js: Click Editar + nuevo texto
    Js->>Api: PATCH /tareas/id {texto}
    Api->>Service: obtener(id)
    Service->>Repo: get_task(id)
    Repo-->>Service: Task_or_None
    Service-->>Api: dict_or_None
    Api->>Api: validar payload
    Api->>Service: actualizar(id, texto, completada)
    Service->>Repo: update_task(...)
    Repo->>Repo: mutar Task en dict indexado
    Repo->>Repo: _save() atomico
    Repo->>File: replace
    Repo-->>Service: Task
    Service-->>Api: dict actualizado
    Api-->>Js: 200 JSON
    Js->>Js: replace del li en DOM
```

### Completar tarea (PATCH /tareas/{id}/completar)

```mermaid
sequenceDiagram
    participant User as Usuario
    participant Js as app.js
    participant Api as tasks_bp.completar_tarea
    participant Service as TaskService
    participant Repo as JsonTaskRepository
    participant File as tareas.json

    User->>Js: Click Completar
    Js->>Api: PATCH /tareas/id/completar
    Api->>Service: completar(id)
    Service->>Repo: complete_task(id)
    Repo->>Repo: task.completada = True
    Repo->>Repo: _save() atomico
    Repo->>File: replace
    Repo-->>Service: Task
    Service-->>Api: dict
    Api-->>Js: 200 JSON
    Js->>Js: replace del li con estado completada
```

### Eliminar tarea (DELETE /tareas/{id})

```mermaid
sequenceDiagram
    participant User as Usuario
    participant Js as app.js
    participant Api as tasks_bp.eliminar_tarea
    participant Service as TaskService
    participant Repo as JsonTaskRepository
    participant File as tareas.json

    User->>Js: Click Eliminar + confirm
    Js->>Api: DELETE /tareas/id
    Api->>Service: eliminar(id)
    Service->>Repo: delete_task(id)
    Repo->>Repo: pop(id) de _tasks_by_id
    Repo->>Repo: _save() atomico
    Repo->>File: replace
    Repo-->>Service: bool
    Service-->>Api: bool
    Api-->>Js: 200 {"mensaje":"Tarea eliminada"}
    Js->>Js: remove li + updateEmptyState()
```
