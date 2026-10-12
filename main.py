

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from uuid import uuid4
from io import BytesIO

from director import AutonomousDirector

app = FastAPI(
    title="REBA AI VIDEO ENGINE",
    description="Autonomous Director API",
    version="0.1.0",
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

director = AutonomousDirector()
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


@app.get("/")
def home():
    return {
        "engine": "REBA AI VIDEO ENGINE",
        "status": "running",
        "module": "Autonomous Director v1",
        "capability": "Automatic scene planning",
        "video_generation": "Not connected yet",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/director/plan")
async def create_director_plan(
    file: UploadFile = File(...),
    duration_seconds: int = Form(15),
):
    if duration_seconds < 5 or duration_seconds > 60:
        raise HTTPException(
            status_code=400,
            detail="Duration must be between 5 and 60 seconds.",
        )

    data = await file.read(MAX_IMAGE_SIZE + 1)
    await file.close()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Please upload an image.",
        )

    if len(data) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image is too large. Maximum size is 10 MB.",
        )

    try:
        with Image.open(BytesIO(data)) as image:
            image_format = image.format
            image.verify()

        if image_format not in {"JPEG", "PNG", "WEBP"}:
            raise HTTPException(
                status_code=400,
                detail="Use a JPG, PNG, or WEBP image.",
            )

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image.",
        )

    suffix = {
        "JPEG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
    }[image_format]

    image_path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"
    image_path.write_bytes(data)

    try:
        plan = director.create_plan(
            image_path=str(image_path),
            duration_seconds=duration_seconds,
        )
    except Exception:
        image_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="The Director could not create a scene plan.",
        )

    return JSONResponse(content={
        "status": "plan_created",
        "message": (
            "Autonomous Director created the scene plan. "
            "Real AI video generation is not connected yet."
        ),
        "plan": plan,
    })
