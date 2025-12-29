from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from app.ingestion.ingest import ingest_pdf, save_upload
from app.query.rag import answer_with_rag

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

STATIC_DIR = PROJECT_ROOT / "static"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
UPLOAD_DIR = Path("./uploads")

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class AskRequest(BaseModel):
    query: str


@app.get("/", response_class=HTMLResponse)
def home():
    return (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/favicon.ico")
def favicon():
    return JSONResponse(status_code=204, content=None)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    saved_path = save_upload(data, file.filename)

    try:
        chunks_indexed = ingest_pdf(saved_path, file.filename)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    return {
        "status": "ok",
        "filename": file.filename,
        "chunks_indexed": chunks_indexed,
    }


from fastapi import HTTPException

@app.post("/ask")
async def ask(req: AskRequest):
    try:
        return answer_with_rag(req.query)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )



@app.get("/files")
def list_files():
    if not UPLOAD_DIR.exists():
        return []
    return sorted([f.name for f in UPLOAD_DIR.iterdir() if f.is_file()])
