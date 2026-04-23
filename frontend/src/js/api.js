const API_BASE_URL = globalThis.TASK_API_BASE_URL || "http://localhost:5000";

async function request(path, options = {}) {
  const headers = Object.assign(
    {
      "Content-Type": "application/json",
    },
    options.headers
  );

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const message = body?.error ?? "Unexpected API error.";
    throw new Error(message);
  }

  return body;
}

const taskApi = {
  getBaseUrl() {
    return API_BASE_URL;
  },
  listTasks() {
    return request("/tasks");
  },
  createTask(task) {
    return request("/tasks", {
      method: "POST",
      body: JSON.stringify(task),
    });
  },
  updateTask(taskId, task) {
    return request(`/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(task),
    });
  },
  updateTaskStatus(taskId, status) {
    return request(`/tasks/${taskId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
  },
  deleteTask(taskId) {
    return request(`/tasks/${taskId}`, {
      method: "DELETE",
    });
  },
};

globalThis.taskApi = taskApi;