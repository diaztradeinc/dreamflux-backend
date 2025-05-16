
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
import base64
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For debug purposes; replace with specific domain later
    allow_methods=["*"],
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
        files={"none": ''},
        data=data
    )

    if response.status_code == 200:
        encoded = base64.b64encode(response.content).decode("utf-8")
        return {"image_base64": f"data:image/{req.output_format};base64,{encoded}"}
    else:
        return {"error": response.json()}
