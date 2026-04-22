# Task Management App

Task Management App is a full-stack web application for managing tasks with a Kanban-style flow. The project is intentionally split into a standalone frontend and backend so each layer can be built, tested and deployed independently in CI/CD pipelines.

## Project Overview

- `frontend/`: static client built with HTML, CSS and vanilla JavaScript.
- `backend/`: REST API built with Python and Flask.
- The frontend communicates with the backend through HTTP requests using `fetch`.

## Requirements

- Python 3.x
- `pip`

## First Run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

This starts both layers automatically:

- Backend API: `http://localhost:5000`
- Frontend app: `http://localhost:8000`

If port `5000` or `8000` is already in use, `run.py` automatically picks the next available port and prints the final URLs in the terminal. The frontend is configured automatically to use the selected backend API URL.

## Subsequent Runs

```bash
source venv/bin/activate
python run.py
```

## Run Layers Separately

If you want to keep both services fully independent during development:

```bash
python backend/app/main.py
python frontend/serve_frontend.py
```

The frontend server rebuilds `frontend/dist/` automatically before serving it.

## How To Run Tests

Before running tests, activate the virtual environment and make sure dependencies are installed:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Run only the backend tests:

```bash
pytest backend/tests
```

Run only the frontend tests:

```bash
pytest frontend/tests
```

Run the entire test suite from the project root:

```bash
pytest
```

Optional test flow for local verification:

```bash
python frontend/build_frontend.py
pytest
```

For a more detailed testing walkthrough, see [TESTING.md](/Users/camilo/todoapp/TESTING.md).

## Build Frontend

```bash
python frontend/build_frontend.py
```

## Serve Frontend

```bash
python frontend/serve_frontend.py
```

## API Endpoints

- `POST /tasks`: create a task
- `GET /tasks`: list tasks
- `GET /tasks/<id>`: get one task
- `PUT /tasks/<id>`: update a task
- `PATCH /tasks/<id>/status`: update only the task status
- `DELETE /tasks/<id>`: delete a task

Each task uses this structure:

```json
{
  "id": 1,
  "title": "Task example",
  "description": "Description example",
  "status": "pending"
}
```

## Project Structure

```bash
task-management-app/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   └── tasks.py
│   │   ├── services/
│   │   │   └── task_service.py
│   │   ├── models/
│   │   │   └── task_model.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── Dockerfile
│   └── tests/
│       ├── conftest.py
│       ├── test_routes.py
│       └── test_services.py
├── frontend/
│   ├── src/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   ├── api.js
│   │   │   └── app.js
│   │   └── index.html
│   ├── dist/
│   ├── tests/
│   │   ├── test_frontend_content.py
│   │   └── test_frontend_structure.py
│   ├── build_frontend.py
│   ├── serve_frontend.py
│   └── Dockerfile
├── run.py
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── README.md
└── .gitignore
```

## Folder Details

- `backend/app/routes/`: API endpoints and request handling.
- `backend/app/services/`: task business rules, validation and in-memory persistence.
- `backend/app/models/`: task model definitions and shared constants.
- `backend/tests/`: route tests, service tests and reusable fixtures.
- `frontend/src/`: source files for the static frontend.
- `frontend/dist/`: build output used as deployable frontend artifact.
- `frontend/tests/`: structure, content and build validations for CI.
- `frontend/serve_frontend.py`: local static server for the built frontend.
- `run.py`: convenience runner that starts backend and frontend together.

## CI/CD Readiness

This project is prepared for pipeline automation with independent stages for:

1. Installing dependencies from the root `requirements.txt`
2. Building the frontend artifact
3. Running backend unit tests
4. Running frontend validation tests
5. Running the full project test suite

Example commands:

```bash
pip install -r requirements.txt
python frontend/build_frontend.py
pytest
```

## Docker Support

The repository includes container definitions for both layers and a `docker-compose.yml` file so it can be extended easily in local or CI environments.

- Backend container runs Flask on port `5000`
- Frontend container builds and serves `frontend/dist/` on port `8000`

## Notes

- Task data is stored in memory to keep the project simple and focused on architecture, testing and CI/CD workflows.
- Validation enforces a required title and valid status values: `pending`, `in_progress`, `done`.
