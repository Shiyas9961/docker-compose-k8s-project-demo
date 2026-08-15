import { useCallback, useEffect, useState } from "react";
import { config } from "./config";

const API_BASE_URL = config.apiUrl;

function App() {
  const [tasks, setTasks] = useState([]);
  const [taskTitle, setTaskTitle] = useState("");
  const [handledBy, setHandledBy] = useState("Not connected");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setErrorMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/tasks`
      );

      if (!response.ok) {
        throw new Error(
          `Could not load tasks: ${response.status}`
        );
      }

      const data = await response.json();

      setTasks(data.tasks);
      setHandledBy(data.handled_by);
    } catch (error) {
      console.error(error);

      setErrorMessage(
        "Unable to connect to the backend service."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  async function createTask(event) {
    event.preventDefault();

    const cleanedTitle = taskTitle.trim();

    if (!cleanedTitle) {
      setErrorMessage("Please enter a task title.");
      return;
    }

    setSubmitting(true);
    setErrorMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/tasks`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            title: cleanedTitle
          })
        }
      );

      if (!response.ok) {
        throw new Error(
          `Could not create task: ${response.status}`
        );
      }

      const data = await response.json();

      setTasks((currentTasks) => [
        data.task,
        ...currentTasks
      ]);

      setHandledBy(data.handled_by);
      setTaskTitle("");
    } catch (error) {
      console.error(error);

      setErrorMessage("Could not create the task.");
    } finally {
      setSubmitting(false);
    }
  }

  async function toggleTask(task) {
    setErrorMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/tasks/${task.id}`,
        {
          method: "PATCH",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            completed: !task.completed
          })
        }
      );

      if (!response.ok) {
        throw new Error(
          `Could not update task: ${response.status}`
        );
      }

      const data = await response.json();

      setTasks((currentTasks) =>
        currentTasks.map((currentTask) =>
          currentTask.id === data.task.id
            ? data.task
            : currentTask
        )
      );

      setHandledBy(data.handled_by);
    } catch (error) {
      console.error(error);

      setErrorMessage("Could not update the task.");
    }
  }

  async function deleteTask(taskId) {
    setErrorMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/tasks/${taskId}`,
        {
          method: "DELETE"
        }
      );

      if (!response.ok) {
        throw new Error(
          `Could not delete task: ${response.status}`
        );
      }

      setTasks((currentTasks) =>
        currentTasks.filter(
          (task) => task.id !== taskId
        )
      );

      await fetchBackendInstance();
    } catch (error) {
      console.error(error);

      setErrorMessage("Could not delete the task.");
    }
  }

  async function fetchBackendInstance() {
    try {
      const response = await fetch(
        `${API_BASE_URL}/instance`
      );

      if (!response.ok) {
        return;
      }

      const data = await response.json();

      setHandledBy(data.handled_by);
    } catch (error) {
      console.error(error);
    }
  }

  const completedTaskCount = tasks.filter(
    (task) => task.completed
  ).length;

  return (
    <main className="application-shell">
      <section className="task-panel">
        <header className="application-header">
          <div>
            <p className="eyebrow">
              Docker three-tier application
            </p>

            <h1>Task Manager</h1>

            <p className="subtitle">
              React, FastAPI and PostgreSQL
            </p>
          </div>

          <button
            className="refresh-button"
            type="button"
            onClick={fetchTasks}
            disabled={loading}
          >
            {loading ? "Loading..." : "Refresh"}
          </button>
        </header>

        <section className="instance-card">
          <div>
            <span className="status-indicator" />
            Backend instance
          </div>

          <strong>{handledBy}</strong>
        </section>

        <form
          className="task-form"
          onSubmit={createTask}
        >
          <label htmlFor="task-title">
            Add a new task
          </label>

          <div className="task-input-row">
            <input
              id="task-title"
              type="text"
              value={taskTitle}
              onChange={(event) =>
                setTaskTitle(event.target.value)
              }
              placeholder="For example: Learn Docker networking"
              maxLength={255}
              disabled={submitting}
            />

            <button
              type="submit"
              disabled={submitting}
            >
              {submitting ? "Adding..." : "Add task"}
            </button>
          </div>
        </form>

        {errorMessage && (
          <div className="error-message">
            {errorMessage}
          </div>
        )}

        <section className="task-summary">
          <div>
            <span>Total tasks</span>
            <strong>{tasks.length}</strong>
          </div>

          <div>
            <span>Completed</span>
            <strong>{completedTaskCount}</strong>
          </div>

          <div>
            <span>Pending</span>
            <strong>
              {tasks.length - completedTaskCount}
            </strong>
          </div>
        </section>

        <section className="task-list-section">
          <h2>Your tasks</h2>

          {loading && (
            <p className="empty-message">
              Loading tasks...
            </p>
          )}

          {!loading && tasks.length === 0 && (
            <p className="empty-message">
              No tasks yet. Create your first task.
            </p>
          )}

          {!loading && tasks.length > 0 && (
            <ul className="task-list">
              {tasks.map((task) => (
                <li
                  className={
                    task.completed
                      ? "task-item task-completed"
                      : "task-item"
                  }
                  key={task.id}
                >
                  <label className="task-content">
                    <input
                      type="checkbox"
                      checked={task.completed}
                      onChange={() => toggleTask(task)}
                    />

                    <span>
                      <strong>{task.title}</strong>

                      <small>
                        Created{" "}
                        {new Date(
                          task.created_at
                        ).toLocaleString()}
                      </small>
                    </span>
                  </label>

                  <button
                    className="delete-button"
                    type="button"
                    onClick={() => deleteTask(task.id)}
                  >
                    Delete
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </section>
    </main>
  );
}

export default App;
