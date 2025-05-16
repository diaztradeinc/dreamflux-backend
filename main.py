
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
import base64
import os

app = FastAPI()

# Allow frontend on Netlify
origins = ["https://magenta-fenglisu-2f0aec.netlify.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY") or "your-api-key-here"
API_URL = "https://api.stability.ai/v1/generation/{model}/text-to-image"

@app.post("/generate")
async def generate(
    prompt: str = Form(...),
    negative_prompt: Optional[str] = Form(""),
    steps: int = Form(30),
    cfg_scale: float = Form(7.0),
    width: int = Form(768),
    height: int = Form(768),
    sampler: Optional[str] = Form("auto"),
    seed: Optional[int] = Form(-1),
    model: str = Form("stable-diffusion-xl-1024-v1-0"),
    style_preset: Optional[str] = Form(""),
    clip_guidance_preset: Optional[str] = Form("NONE"),
    image_strength: Optional[float] = Form(0.5),
    init_image: Optional[UploadFile] = File(None)
):
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "application/json"
    }

    if init_image:
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
    else:
        endpoint = API_URL.format(model=model)
        payload = {
            "text_prompts[0][text]": prompt,
            "text_prompts[1][text]": negative_prompt,
            "cfg_scale": cfg_scale,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": steps,
            "seed": seed,
            "style_preset": style_preset,
        }
        response = requests.post(endpoint, headers=headers, data=payload)

    if response.status_code != 200:
        return {"error": response.text}

    data = response.json()
    if "artifacts" in data and len(data["artifacts"]) > 0:
        image_data = data["artifacts"][0]["base64"]
        return {"image_base64": f"data:image/png;base64,{image_data}"}
    else:
        return {"error": "No image returned"}
