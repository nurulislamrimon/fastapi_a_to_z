# Simple FastAPI Application

A lightweight, asynchronous REST API built with FastAPI and managed using Poetry.

## Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.10 or higher
- [Poetry](https://python-poetry.org) package manager

## Getting Started

Follow these steps to set up and run the project locally.

### 1. Clone the Project

Navigate to your project directory where your files are located:

```bash
cd path/to/your/project
```

### 2. Install Dependencies

Use Poetry to create a isolated virtual environment and install FastAPI, Uvicorn, and all required sub-dependencies:

```bash
poetry install
```

### 3. Run the Development Server

Start the Uvicorn server inside the Poetry environment. The `--reload` flag enables auto-reloading whenever you make changes to your code:

```bash
poetry run uvicorn main:app --reload
```

The application will start running at `http://127.0.0.1:8000`.

## API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, you can access the docs in your browser:

- **Interactive Swagger UI:** [http://127.0.0](http://127.0.0) (Allows you to test endpoints directly from the browser)
- **Alternative ReDoc UI:** [http://127.0.0](http://127.0.0)

## Project Structure

```text
├── pyproject.toml    # Poetry configuration and top-level dependencies
├── poetry.lock       # Locked versions of all dependencies
├── README.md         # Project documentation
└── main.py           # FastAPI application entry point
```
