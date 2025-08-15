# MainGen

A simplified prototype of a family tree service. It provides minimal API endpoints for user authentication, tree management, person records, and relationships using FastAPI. This is an in-memory prototype derived from the MVP requirements.

## Setup

```bash
pip install -r requirements.txt
```

## Running the app

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000/ in a browser to use a minimal web interface for signing up, creating a tree, and adding persons.

## Running tests

```bash
pytest
```
