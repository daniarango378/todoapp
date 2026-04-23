const STATUS_COLUMNS = ["pending", "in_progress", "done"];

const state = {
  editingTaskId: null,
  tasks: [],
};

const form = document.getElementById("task-form");
const titleInput = document.getElementById("title");
const descriptionInput = document.getElementById("description");
const statusInput = document.getElementById("status");
const taskIdInput = document.getElementById("task-id");
const feedback = document.getElementById("feedback");
const formTitle = document.getElementById("form-title");
const cancelEditBtn = document.getElementById("cancel-edit-btn");
const refreshBtn = document.getElementById("refresh-btn");
const apiBaseUrl = document.getElementById("api-base-url");

apiBaseUrl.textContent = globalThis.taskApi.getBaseUrl();

function setFeedback(message, isError = false) {
  feedback.textContent = message;
  feedback.style.color = isError ? "#8f1d1d" : "#8f3f1c";
}

function resetForm() {
  form.reset();
  state.editingTaskId = null;
  taskIdInput.value = "";
  statusInput.value = "pending";
  formTitle.textContent = "Create Task";
  cancelEditBtn.classList.add("hidden");
}

function populateForm(task) {
  state.editingTaskId = task.id;
  taskIdInput.value = String(task.id);
  titleInput.value = task.title;
  descriptionInput.value = task.description;
  statusInput.value = task.status;
  formTitle.textContent = `Edit Task #${task.id}`;
  cancelEditBtn.classList.remove("hidden");
  titleInput.focus();
}

function renderEmptyState(status) {
  return `<p class="empty-state">No tasks in ${status.replace("_", " ")}.</p>`;
}

function renderTaskCard(task) {
  return `
    <article class="task-card" data-status="${task.status}">
      <h4>${task.title}</h4>
      <p>${task.description || "No description provided."}</p>
      <div class="task-actions">
        <select class="status-select" data-action="status" data-id="${task.id}">
          <option value="pending" ${task.status === "pending" ? "selected" : ""}>Pending</option>
          <option value="in_progress" ${task.status === "in_progress" ? "selected" : ""}>In Progress</option>
          <option value="done" ${task.status === "done" ? "selected" : ""}>Done</option>
        </select>
        <button type="button" data-action="edit" data-id="${task.id}">Edit</button>
        <button type="button" data-action="delete" data-id="${task.id}">Delete</button>
      </div>
    </article>
  `;
}

function renderTasks(tasks) {
  STATUS_COLUMNS.forEach((status) => {
    const column = document.getElementById(`${status}-tasks`);
    const count = document.getElementById(`count-${status}`);
    const filtered = tasks.filter((task) => task.status === status);
    count.textContent = String(filtered.length);
    column.innerHTML = filtered.length
      ? filtered.map(renderTaskCard).join("")
      : renderEmptyState(status);
  });
}

async function loadTasks() {
  try {
    const tasks = await globalThis.taskApi.listTasks();
    state.tasks = tasks;
    renderTasks(tasks);
    setFeedback("Tasks loaded successfully.");
  } catch (error) {
    setFeedback(error.message, true);
  }
}

async function handleSubmit(event) {
  event.preventDefault();

  const payload = {
    title: titleInput.value,
    description: descriptionInput.value,
    status: statusInput.value,
  };

  try {
    if (state.editingTaskId) {
      await globalThis.taskApi.updateTask(state.editingTaskId, payload);
      setFeedback("Task updated successfully.");
    } else {
      await globalThis.taskApi.createTask(payload);
      setFeedback("Task created successfully.");
    }

    resetForm();
    await loadTasks();
  } catch (error) {
    setFeedback(error.message, true);
  }
}

async function handleBoardClick(event) {
  const target = event.target.closest("[data-action]");
  if (!target) {
    return;
  }

  const taskId = Number(target.dataset.id);
  const action = target.dataset.action;
  const task = state.tasks.find((item) => item.id === taskId);

  if (!task) {
    setFeedback("The selected task no longer exists.", true);
    await loadTasks();
    return;
  }

  if (action === "edit") {
    populateForm(task);
    return;
  }

  if (action === "delete") {
    try {
      await globalThis.taskApi.deleteTask(taskId);
      if (state.editingTaskId === taskId) {
        resetForm();
      }
      setFeedback("Task deleted successfully.");
      await loadTasks();
    } catch (error) {
      setFeedback(error.message, true);
    }
  }
}

async function handleStatusChange(event) {
  if (!event.target.matches('[data-action="status"]')) {
    return;
  }

  const taskId = Number(event.target.dataset.id);
  try {
    await globalThis.taskApi.updateTaskStatus(taskId, event.target.value);
    setFeedback("Task status updated successfully.");
    await loadTasks();
  } catch (error) {
    setFeedback(error.message, true);
  }
}

form.addEventListener("submit", handleSubmit);
cancelEditBtn.addEventListener("click", () => {
  resetForm();
  setFeedback("Edit cancelled.");
});
refreshBtn.addEventListener("click", loadTasks);
document.querySelector(".board").addEventListener("click", handleBoardClick);
document.querySelector(".board").addEventListener("change", handleStatusChange);

document.addEventListener("DOMContentLoaded", () => {
  resetForm();
  void loadTasks();
});