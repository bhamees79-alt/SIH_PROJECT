
from fastapi import FastAPI, UploadFile, File
import os
import shutil
import uuid

app = FastAPI(title="BAS HAR Backend")

UPLOAD_DIR = "backend/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "BAS HAR Backend is running"
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    filename = f"{uuid.uuid4()}.mp4"

    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {
        "message": "Video uploaded successfully",
        "file_path": file_path
    }
