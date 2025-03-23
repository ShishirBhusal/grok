# GrokBeast

A FastAPI application for tracking problems and their impact.

## Features

- Store problems with pain level and reach metrics
- Simple REST API for interaction
- SQLite database for persistence

## Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python main.py`

## API Endpoints

- `GET /`: Health check
- `POST /add_problem`: Add a new problem with parameters:
  - `problem`: Description
  - `pain`: Impact level (integer)
  - `reach`: Scope of impact 