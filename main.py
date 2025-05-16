
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
import base64
import os

app = FastAPI()

origins = ["https://magenta-fenglisu-2f0aec.netlify.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY") or "your-api-key-here"

class TextRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    steps: int = 30
    cfg_scale: float = 7.0
    width: int = 768
    height: int = 768
    sampler: Optional[str] = "auto"
    seed: Optional[int] = -1
    model: str = "stable-diffusion-xl-1024-v1-0"
    style_preset: Optional[str] = ""
    clip_guidance_preset: Optional[str] = "NONE"

@app.post("/generate-text")
async def generate_text(req: TextRequest):
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "text_prompts": [
            {"text": req.prompt, "weight": 1.0},
            {"text": req.negative_prompt, "weight": -1.0}
        ],
        "cfg_scale": req.cfg_scale,
        "height": req.height,
        "width": req.width,
        "samples": 1,
        "steps": req.steps,
        "seed": req.seed,
        "style_preset": req.style_preset
    }

    endpoint = f"https://api.stability.ai/v1/generation/{req.model}/text-to-image"
    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code != 200:
        return {"error": response.text}

    data = response.json()
    if "artifacts" in data and len(data["artifacts"]) > 0:
        image_data = data["artifacts"][0]["base64"]
        return {"image_base64": f"data:image/png;base64,{image_data}"}
    else:
        return {"error": "No image returned"}

@app.post("/generate-image")
async def generate_image(
    prompt: str = Form(...),
    negative_prompt: Optional[str] = Form(""),
    steps: int = Form(30),
    cfg_scale: float = Form(7.0),
    width: int = Form(768),
    height: int = Form(768),
    seed: Optional[int] = Form(-1),
    model: str = Form("stable-diffusion-xl-1024-v1-0"),
    style_preset: Optional[str] = Form(""),
    image_strength: Optional[float] = Form(0.5),
    init_image: UploadFile = File(...)
):
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "application/json"
    }

    image_bytes = await init_image.read()
    endpoint = f"https://api.stability.ai/v1/generation/{model}/image-to-image"
    files = {"init_image": image_bytes}
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "width": width,
        "height": height,
        "seed": seed,
        "style_preset": style_preset,
        "image_strength": image_strength
    }

    response = requests.post(endpoint, headers=headers, files=files, data=payload)

    if response.status_code != 200:
        return {"error": response.text}

    data = response.json()
    if "artifacts" in data and len(data["artifacts"]) > 0:
        image_data = data["artifacts"][0]["base64"]
        return {"image_base64": f"data:image/png;base64,{image_data}"}
    else:
        return {"error": "No image returned"}


from fastapi.responses import JSONResponse

@app.options("/generate-text")
async def options_generate_text():
    return JSONResponse(content={"status": "ok"}, headers={
        "Access-Control-Allow-Origin": "https://magenta-fenglisu-2f0aec.netlify.app",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    })
