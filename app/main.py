from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from app.ingestion.ingest import ingest_pdf, save_upload, UPLOAD_DIR
from app.query.rag import answer_with_rag
from dotenv import load_dotenv
load_dotenv()

# ✅ CREATE APP ONCE
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


class QueryRequest(BaseModel):
    query: str
    source: Optional[str] = None
    cross_document: bool = False


@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            return JSONResponse(
                status_code=400,
                content={"status": "error", "error": "Only PDF files are allowed."},
            )

        file_bytes = await file.read()
        saved_path = save_upload(file_bytes, file.filename)

        chunks_indexed = ingest_pdf(saved_path, file.filename)

        return {
            "status": "ok",
            "filename": file.filename,
            "chunks_indexed": chunks_indexed,
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)},
        )


@app.get("/files")
def list_files() -> List[str]:
    if not UPLOAD_DIR.exists():
        return []
    return sorted(
        [
            p.name
            for p in UPLOAD_DIR.iterdir()
            if p.is_file() and p.suffix.lower() == ".pdf"
        ]
    )


@app.post("/query")
async def query(
    question: str = Form(...),
    source: Optional[str] = Form(None),
    cross_document: bool = Form(False),
):
    if not question.strip():
        return JSONResponse(
            status_code=400,
            content={"detail": "Question is required"},
        )

    answer, sources, confidence  = answer_with_rag(
        question,
        source,
        cross_document,
    )

    return {
    "answer": answer,
    "sources": sources,
    "confidence": confidence,
}
