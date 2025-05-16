
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import requests
import base64
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://magenta-fenglisu-2f0aec.netlify.app"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True
)

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY") or "your-api-key-here"

class V2PromptRequest(BaseModel):
    prompt: str
    output_format: Optional[str] = "webp"

@app.post("/generate-text")
async def generate_text(req: V2PromptRequest):
    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY}",
        "accept": "image/*"
    }

    data = {
        "prompt": req.prompt,
        "output_format": req.output_format
    }

    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/core",
        headers=headers,
        files={"none": ''},  # required dummy field for multipart/form-data
        data=data
    )

    if response.status_code == 200:
        encoded = base64.b64encode(response.content).decode("utf-8")
        return {"image_base64": f"data:image/{req.output_format};base64,{encoded}"}
    else:
        return {"error": response.json()}

@app.options("/generate-text")
async def options_generate_text():
    return JSONResponse(content={"status": "ok"}, headers={
        "Access-Control-Allow-Origin": "https://magenta-fenglisu-2f0aec.netlify.app",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    })
