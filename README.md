
# Stability AI FastAPI Backend

A deploy-ready FastAPI server that connects to Stability AI's image generation API.

## Endpoints
- `POST /generate`: Accepts prompts, settings, and optionally an image.

## Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Deploy to Railway
- Add env var `STABILITY_API_KEY`
