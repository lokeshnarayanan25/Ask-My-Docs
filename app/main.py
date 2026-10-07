from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.schemas import AskRequest, AskResponse
from app.services.rag_service import ask_question


app = FastAPI(title="Ask My Docs")

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to static frontend files
STATIC_DIR = Path(__file__).parent / "static"

# Mount static directory if it exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    """Serve web application UI."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Ask My Docs API is running"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    """RAG question answering endpoint."""
    try:
        return ask_question(request.question)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your question: {str(error)}"
        )