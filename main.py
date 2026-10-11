
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil

app = FastAPI(title="REBA AI VIDEO ENGINE")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
def home():
    return {
        "engine": "REBA AI VIDEO ENGINE",
        "status": "running",
        "message": "REBA video engine API is ready"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        return JSONResponse(
            status_code=400,
            content={"error": "Please upload an image file"}
        )

    filename = Path(file.filename or "photo.jpg").name
    destination = UPLOAD_DIR / filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Photo uploaded successfully",
        "filename": filename
}
