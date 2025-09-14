import os
import threading
import uuid
from typing import Dict, List, Optional
from fastapi.responses import StreamingResponse
from gtts import gTTS
import io
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from typing import Annotated, TypedDict
from langchain_community.tools import DuckDuckGoSearchResults
from template_prompts import template_text

load_dotenv()

EMPATHIA_PROMPTS_PATH = os.getenv("EMPATHIA_PROMPTS_PATH", "empathic_prompts.txt")
CHROMA_DIR = os.getenv("EMPATHIA_CHROMA_DIR", "./empathia_chroma_db")
MODEL_NAME = os.getenv("EMPATHIA_OLLAMA_MODEL", "llama3.1")
MAX_HISTORY = int(os.getenv("EMPATHIA_MAX_HISTORY", "10"))

app = FastAPI(title="Empathia API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_hist_lock = threading.Lock()
session_histories: Dict[str, List] = {}  

def _load_prompts_into_chroma(prompts_path: str, chroma_dir: str):
    with open(prompts_path, "r", encoding="utf-8") as f:
        raw = f.read()
    parts = [p.strip() for p in raw.split("|") if p.strip()]
    docs = [Document(page_content=p, metadata={"topic": "empathetic_prompt"}) for p in parts]
    embedding_fn = OllamaEmbeddings(model=MODEL_NAME)
    vs = Chroma(
        collection_name="Empathia_namespace",
        embedding_function=embedding_fn,
        persist_directory=chroma_dir,
    )
    try:
        existing = vs._collection.count()
    except Exception:
        existing = None

    if not existing:
        vs.add_documents(docs)
    return vs

_vector_store = _load_prompts_into_chroma(EMPATHIA_PROMPTS_PATH, CHROMA_DIR)
_ollama_model = ChatOllama(model=MODEL_NAME)
_parser = StrOutputParser()

class RespondRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    k: Optional[int] = 3

@app.post("/session")
def create_session():
    sid = str(uuid.uuid4())
    with _hist_lock:
        session_histories[sid] = []
    return {"session_id": sid}


@app.post("/respond")
def respond(req: RespondRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Empty query")

    sid = req.session_id or str(uuid.uuid4())
    with _hist_lock:
        if sid not in session_histories:
            session_histories[sid] = []
        history = session_histories[sid]

    try:
        hits = _vector_store.similarity_search(req.query, k=req.k or 3)
    except Exception:
        hits = []

    anchor_text = " ".join([h.page_content for h in hits]) if hits else "You are Empathia, a compassionate assistant."

    trimmed_history = []
    with _hist_lock:
        recent = history[-MAX_HISTORY:]
    for (role, text) in recent:
        if role == "user":
            trimmed_history.append(f"User: {text}")
        else:
            trimmed_history.append(f"Assistant: {text}")
    history_block = "\n".join(trimmed_history) if trimmed_history else "No prior conversation."

    template_text1 = template_text

    prompt = PromptTemplate(template=template_text1, input_variables=["anchor", "chat_history", "query"])

    chain = prompt | _ollama_model | _parser
    try:
        response_text = chain.invoke({"anchor": anchor_text, "chat_history": history_block, "query": req.query})
    except Exception:
        assembled = template_text1.format(anchor=anchor_text, chat_history=history_block, query=req.query)
        try:
            response_text = _ollama_model(assembled)
        except Exception:
            response_text = "Sorry — I'm having trouble generating a response right now."

    with _hist_lock:
        session_histories[sid].append(("user", req.query))
        session_histories[sid].append(("assistant", response_text))
        if len(session_histories[sid]) > MAX_HISTORY * 2:
            session_histories[sid] = session_histories[sid][-MAX_HISTORY * 2 :]

    return {"response": response_text, "session_id": sid}


