import io
import base64
import numpy as np
from PIL import Image
import easyocr
from fastapi import FastAPI, Request

app = FastAPI()

# Loaded once per cold start; reused across warm invocations
reader = easyocr.Reader(['en'])


@app.post("/api/ocr")
async def ocr(request: Request):
    data = await request.json()
    image_b64 = data['image']  # base64-encoded image string
    image_bytes = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image_np = np.array(image)

    result = reader.readtext(image_np, detail=0)
    return {"result": result}


@app.get("/api/ocr")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "ok"}
