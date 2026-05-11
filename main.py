from typing import Annotated
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil
import os
from engines.standard import process_standard
from engines.premium import process_premium

app = FastAPI()

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_statement(
        file: Annotated[UploadFile, File(...)],
        engine_type: Annotated[str, Form(...)]  # <--- Changed '=' to ',' right here
):
    # 1. Basic Validation
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # 2. Save the file temporarily
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Routing Logic (The Decision Maker)
    if engine_type == "standard":
        result = process_standard(file_path)
        return {"status": "success", "engine": "standard", "data": result}

    elif engine_type == "premium":
        # Current logic: If we haven't finished premium, we "gray it out" via response
        premium_available = False

        if not premium_available:
            return {
                "status": "locked",
                "message": "Premium PDF Regex Classifier is currently under maintenance."
            }

        result = process_premium(file_path)
        return {"status": "success", "engine": "premium", "data": result}

    else:
        raise HTTPException(status_code=400, detail="Invalid engine type.")