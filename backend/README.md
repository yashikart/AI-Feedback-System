# Backend API

FastAPI backend for the AI Feedback System.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variable:
```bash
export OPENROUTER_API_KEY=your_api_key_here
```

Or create a `.env` file with:
```
OPENROUTER_API_KEY=your_api_key_here
```

## Run Locally

```bash
uvicorn main:app --reload --port 8000
```

API will be available at `http://localhost:8000`

API docs available at `http://localhost:8000/docs`

## Deployment

Deploy to Render, Railway, or similar platform. Set `OPENROUTER_API_KEY` as an environment variable.
