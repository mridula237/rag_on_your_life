from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.ingestion.ingest import save_upload, ingest_pdf
from app.query.search import search_documents
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ==============================
# Home
# ==============================
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ==============================
# Upload PDF
# ==============================
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    contents = await file.read()
    path = save_upload(contents, file.filename)
    chunks = ingest_pdf(str(path), file.filename)

    return JSONResponse({
        "filename": file.filename,
        "chunks_indexed": chunks
    })


# ==============================
# List Uploaded Files
# ==============================
@app.get("/files")
async def list_files():
    files = [f.name for f in UPLOAD_DIR.glob("*.pdf")]
    return {"files": files}


# ==============================
# Query (NON-STREAMING)
# ==============================
@app.post("/query")
async def query(data: dict):

    query_text = data.get("query")
    search_all = data.get("search_all", False)

    if not query_text:
        return {"answer": "No query provided.", "sources": []}

    # Retrieve relevant chunks
    results = search_documents(query_text, search_all)

    if not results:
        return {"answer": "No relevant information found.", "sources": []}

    # Build context from retrieved documents
    context = "\n\n".join([doc.page_content for doc in results])

    prompt = f"""
    Use the following context to answer the question.

    Context:
    {context}

    Question:
    {query_text}

    Answer clearly and concisely.
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    # Extract sources
    sources = []
    for doc in results:
        sources.append({
            "source": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", "N/A")
        })

    return {
        "answer": response.content,
        "sources": sources
    }