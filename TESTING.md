# Testing Guide

This document explains how to run the test suite for the Task Management App in detail.

## What Is Covered

The project includes tests for both layers of the application:

- `backend/tests/`: service and API route tests for the Flask backend
- `frontend/tests/`: structural and content tests for the static frontend

All tests are executed with `pytest`.

## Prerequisites

Make sure you have:

- Python 3 installed
- `pip` available

## 1. Create And Activate A Virtual Environment

From the project root:

```bash
python -m venv venv
source venv/bin/activate
```

If you already created it before, only activate it:

```bash
source venv/bin/activate
```

## 2. Install Dependencies

Install the required packages from the root of the project:

```bash
pip install -r requirements.txt
```

This installs:

- `Flask`
- `pytest`

## 3. Run Backend Tests

To execute only the backend tests:

```bash
pytest backend/tests
```

These tests validate:

- task creation
- task listing
- task retrieval by ID
- task updates
- task status changes
- task deletion
- validation errors
- `404` and `400` API responses

### Backend Test Files

- `backend/tests/conftest.py`: shared fixtures and Flask test client
- `backend/tests/test_services.py`: business logic tests
- `backend/tests/test_routes.py`: HTTP route tests

## 4. Run Frontend Tests

To execute only the frontend tests:

```bash
pytest frontend/tests
```

These tests validate:

- required frontend files exist
- `index.html` contains the expected structure
- `api.js` includes API helper functions
- `app.js` includes task-loading behavior
- the frontend build process creates `frontend/dist/`

### Frontend Test Files

- `frontend/tests/test_frontend_structure.py`: structure checks
- `frontend/tests/test_frontend_content.py`: content and build checks

## 5. Run All Tests

To execute the entire suite from the root of the project:

```bash
pytest
```

This uses the configuration defined in `pytest.ini`, which includes:

- `backend/tests`
- `frontend/tests`

## 6. Run The Frontend Build Before Testing

The frontend tests already validate the build flow, but you can also run the build manually before the full suite:

```bash
python frontend/build_frontend.py
pytest
```

This is useful when simulating a CI pipeline locally.

## 7. Recommended Local Validation Flow

For a clean local verification from scratch:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python frontend/build_frontend.py
pytest
```

## 8. Expected Result

If everything is working correctly, `pytest` should finish with all tests passing.

Example:

```bash
============================= test session starts ==============================
collected 28 items

backend/tests/test_routes.py ........
backend/tests/test_services.py .........
frontend/tests/test_frontend_content.py .....
frontend/tests/test_frontend_structure.py ......

============================== 28 passed in 0.14s ==============================
```

The exact timing may vary depending on your machine.

## 9. Troubleshooting

### `pytest: command not found`

Make sure the virtual environment is activated:

```bash
source venv/bin/activate
```

Then verify `pytest` is installed:

```bash
pip install -r requirements.txt
```

### `python: command not found`

Use `python3` instead:

```bash
python3 -m venv venv
source venv/bin/activate
python3 frontend/build_frontend.py
python3 -m pytest
```

### Import Errors During Tests

Run tests from the project root:

```bash
pytest
```

The repository includes `pytest.ini` configured for this layout.

### Build Output Missing

Re-run the frontend build manually:

```bash
python frontend/build_frontend.py
```

Then execute:

```bash
pytest frontend/tests
```

## 10. CI-Friendly Commands

Backend pipeline step:

```bash
pip install -r requirements.txt
pytest backend/tests
```

Frontend pipeline step:

```bash
pip install -r requirements.txt
python frontend/build_frontend.py
pytest frontend/tests
```

Full pipeline step:

```bash
pip install -r requirements.txt
python frontend/build_frontend.py
pytest
```
