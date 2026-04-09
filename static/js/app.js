const form = document.getElementById("form-nueva-tarea");
const inputTexto = document.getElementById("texto");
const taskList = document.getElementById("task-list");
const emptyState = document.getElementById("empty-state");

function setButtonLoading(button, loading) {
  if (!button) return;
  button.disabled = loading;
  if (loading) {
    button.dataset.originalText = button.textContent;
    button.textContent = "Procesando...";
  } else if (button.dataset.originalText) {
    button.textContent = button.dataset.originalText;
    delete button.dataset.originalText;
  }
}

function updateEmptyState() {
  if (!emptyState || !taskList) return;
  const hasItems = taskList.children.length > 0;
  emptyState.classList.toggle("hidden", hasItems);
}

function renderTaskItem(task) {
  const li = document.createElement("li");
  li.dataset.taskId = String(task.id);
  if (task.completada) li.classList.add("task-done");

  const main = document.createElement("div");
  main.className = "task-main";

  const id = document.createElement("span");
  id.className = "task-id";
  id.textContent = `#${task.id}`;

  const text = document.createElement("span");
  text.className = "task-text";
  text.textContent = task.texto;

  main.append(id, text);

  if (task.completada) {
    const status = document.createElement("small");
    status.className = "task-status";
    status.textContent = "Completada";
    main.append(status);
  }

  const actions = document.createElement("div");
  actions.className = "task-actions";
  actions.innerHTML = `
    <button type="button" class="btn btn-soft btn-editar" data-id="${task.id}" data-texto="${task.texto}">Editar</button>
    ${
      task.completada
        ? ""
        : `<button type="button" class="btn btn-soft btn-completar" data-id="${task.id}">Completar</button>`
    }
    <button type="button" class="btn btn-danger btn-eliminar" data-id="${task.id}">Eliminar</button>
  `;

  li.append(main, actions);
  return li;
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Operacion fallida");
  }
  return data;
}

if (form && inputTexto && taskList) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const texto = inputTexto.value.trim();
    if (!texto) return;

    const submitBtn = form.querySelector("button[type='submit']");
    setButtonLoading(submitBtn, true);

    try {
      const task = await fetchJson("/tareas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto }),
      });
      taskList.appendChild(renderTaskItem(task));
      inputTexto.value = "";
      updateEmptyState();
    } catch (error) {
      alert(error.message || "No se pudo crear la tarea");
    } finally {
      setButtonLoading(submitBtn, false);
    }
  });
}

if (taskList) {
  taskList.addEventListener("click", async (event) => {
    const button = event.target.closest("button");
    if (!button) return;

    const taskId = button.dataset.id;
    if (!taskId) return;

    setButtonLoading(button, true);

    try {
      if (button.classList.contains("btn-completar")) {
        const task = await fetchJson(`/tareas/${taskId}/completar`, { method: "PATCH" });
        const li = button.closest("li");
        if (li) li.replaceWith(renderTaskItem(task));
      }

      if (button.classList.contains("btn-editar")) {
        const textoActual = button.dataset.texto || "";
        const nuevoTexto = window.prompt("Modificar tarea:", textoActual);
        if (nuevoTexto === null) return;

        const texto = nuevoTexto.trim();
        if (!texto) {
          alert("El texto no puede estar vacio");
          return;
        }

        const task = await fetchJson(`/tareas/${taskId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ texto }),
        });

        const li = button.closest("li");
        if (li) li.replaceWith(renderTaskItem(task));
      }

      if (button.classList.contains("btn-eliminar")) {
        const confirmacion = window.confirm("¿Seguro que deseas eliminar esta tarea?");
        if (!confirmacion) return;

        await fetchJson(`/tareas/${taskId}`, { method: "DELETE" });
        const li = button.closest("li");
        if (li) li.remove();
      }
      updateEmptyState();
    } catch (error) {
      alert(error.message || "No se pudo completar la operacion");
    } finally {
      setButtonLoading(button, false);
    }
  });
}
