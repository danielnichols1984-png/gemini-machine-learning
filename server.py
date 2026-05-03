from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from llama_index.core import StorageContext, load_index_from_storage
from client import create_dash_app

app = FastAPI()

# Load your index
storage_context = StorageContext.from_defaults(persist_dir="./ml_index")
index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine()

@app.post("/api/chat")
async def chat(payload: dict):
    question = payload.get("question", "")
    response = query_engine.query(question)
    return {"response": str(response)}

# Mount Dash at /dash
dash_app = create_dash_app()
app.mount("/dash", WSGIMiddleware(dash_app.server))

@app.get("/")
def root():
    return {"message": "FastAPI is running. Visit /dash for the UI."}
