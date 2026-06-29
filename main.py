from typing import Annotated
from pathlib import Path
import shutil
import os
import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException


from engines.standard import process_standard
from engines.premium import process_premium
from normaliser import normalize_statement_data
from redacter import prepare_for_ai
from advice_engine import generate_financial_advice

app = FastAPI(title="Statement Insights API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten for production
    allow_methods=["POST"],
    allow_headers=["*"],
)
# Ensure upload directory exists
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _safe_save(file: UploadFile) -> Path:
    """Save upload using a sanitized filename to avoid path traversal."""
    # Strip directory components from the client filename
    original_name = os.path.basename(file.filename or "upload.pdf")
    # Prefix with a uuid so concurrent uploads don't collide
    safe_name = f"{uuid.uuid4().hex}_{original_name}"
    dest = UPLOAD_DIR / safe_name
    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return dest


@app.post("/upload")
async def upload_statement(
    file: Annotated[UploadFile, File(...)],
    engine_type: Annotated[str, Form(...)],
):
    # 1. Basic validation
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if engine_type not in {"standard", "premium"}:
        raise HTTPException(status_code=400, detail="Invalid engine type.")

    # 2. Save the file safely
    file_path = _safe_save(file)

    # 3. Routing logic
    if engine_type == "premium":
        premium_available = False
        if not premium_available:
            return {
                "status": "locked",
                "message": "Premium PDF Regex Classifier is currently under maintenance.",
            }
        raw = process_premium(str(file_path))
    else:
        raw = process_standard(str(file_path))

    if isinstance(raw, dict) and raw.get("error"):
        raise HTTPException(status_code=502, detail=raw["error"])

    # 4. Full pipeline: normalise -> redact -> advice
    # process_standard saved the raw JSON to data/raw_json/<name>.json
    raw_json_path = Path("data") / "raw_json" / (file_path.stem + ".json")
    if not raw_json_path.exists():
        raise HTTPException(status_code=500, detail="Parser did not produce JSON output.")

    clean = normalize_statement_data(str(raw_json_path))
    ai_safe = prepare_for_ai(clean)
    insights = generate_financial_advice(ai_safe)

    return {
        "status": "success",
        "engine": engine_type,
        "account_info": clean["account_info"],
        "transaction_count": clean["transaction_count"],
        "insights": insights,
    }
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory=".", html=True), name="static")