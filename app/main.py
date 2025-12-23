from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from app.ingestion.ingest import ingest_file
from app.query.rag import answer_with_rag

# Load .env from project root no matter where uvicorn is run
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

STATIC_DIR = PROJECT_ROOT / "static"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

app = FastAPI()

# Mount static (this MUST exist)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class AskRequest(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
def home():
    return (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")

@app.get("/favicon.ico")
def favicon():
    # avoid 404 spam
    return JSONResponse(status_code=204, content=None)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / file.filename
    file_path.write_bytes(await file.read())

    chunks_indexed = ingest_file(str(file_path), file.filename)

    return {
    "status": "ok",
    "chunks_indexed": chunks_indexed,
    "filename": file.filename
}



@app.post("/ask")
async def ask(req: AskRequest):
    try:
        return answer_with_rag(req.query)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
