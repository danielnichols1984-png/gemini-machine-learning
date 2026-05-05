import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

# NEW: import Dash app + WSGI middleware
from starlette.middleware.wsgi import WSGIMiddleware
from client import create_dash_app


class ChatRequest(BaseModel):
    question: str


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# LlamaIndex global settings
Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)
Settings.embed_model = GoogleGenAIEmbedding(
    model_name="models/gemini-embedding-2-preview",
    api_key=api_key
)

app = FastAPI()

# Load index
PERSIST_DIR = "./storage"

if not os.path.exists(PERSIST_DIR):
    print(f"Error: {PERSIST_DIR} not found. Did you run the indexing script?")
    query_engine = None
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    print("Gemini Index loaded successfully.")


# ---------------------------
# API ROUTE
# ---------------------------
@app.post("/api/chat")
async def chat(payload: ChatRequest):
    if not query_engine:
        raise HTTPException(status_code=500, detail="Index not initialized")

    try:
        response = await query_engine.aquery(payload.question)
        return {"response": str(response)}
    except Exception as e:
        print(f"Query Error: {e}")
        return {"response": f"Server Error: {str(e)}"}


# ---------------------------
# DASH MOUNT (THE MISSING PART)
# ---------------------------
dash_app = create_dash_app()
app.mount("/dash", WSGIMiddleware(dash_app.server))


# ---------------------------
# LOCAL DEV ENTRYPOINT
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
