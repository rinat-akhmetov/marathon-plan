import json

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Session
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


@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Upload a .zip archive")
    content = await file.read()
    try:
        summary = process_zip(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    sess = Session(summary_json=json.dumps(summary))
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return {"session_id": sess.id, "summary": summary}


@app.get("/results/{session_id}")
def get_results(session_id: int, db: Session = Depends(get_db)):
    sess = db.query(Session).filter(Session.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Not found")
    return JSONResponse(content=json.loads(sess.summary_json))
