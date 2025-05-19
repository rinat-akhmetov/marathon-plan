import json
import logging
import math
import traceback
from typing import Any

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DBSession

from .database import Base, engine, get_db
from .models import Session as SessionModel
from .processing import process_zip
from .settings import get_settings

settings = get_settings()
app = FastAPI(title="Marathon Training Plan Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def _sanitize_nan(obj: Any) -> Any:
    """Recursively replace NaN floats with None."""
    if isinstance(obj, dict):
        return {k: _sanitize_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_nan(v) for v in obj]
    if isinstance(obj, float) and math.isnan(obj):
        return None
    return obj


@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...), db: DBSession = Depends(get_db)):
    # Ensure filename is a string before checking extension
    if not (file.filename or "").endswith(".zip"):
        raise HTTPException(status_code=400, detail="Upload a .zip archive")
    content = await file.read()
    try:
        # Get pydantic output model for analyzed runs
        summary_model = process_zip(content)
    except Exception as e:
        logging.error(f"Error processing zip: {e}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))
    # Serialize pydantic model to primitive types for JSON storage and response
    summary = summary_model.model_dump()
    logging.info(str(summary))
    sess = SessionModel(summary_json=json.dumps(summary, default=str))
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return {"session_id": sess.id, "summary": summary}


@app.get("/results/{session_id}")
def get_results(session_id: int, db: DBSession = Depends(get_db)):
    # Query the stored session summary
    sess = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Not found")
    # Sanitize NaN values (convert to null) before returning JSON
    raw = json.loads(str(sess.summary_json))
    clean = _sanitize_nan(raw)
    return JSONResponse(content=clean)
