import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from pydantic import BaseModel

# Define the data structure for the incoming request
class ChatRequest(BaseModel):
    question: str


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# 1. Global Settings (Match your indexing script exactly)
Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-2-preview", api_key=api_key)

app = FastAPI()

# 2. Load the Index globally on startup
# Assuming your indexing script saved to './storage'
PERSIST_DIR = "./storage"

if not os.path.exists(PERSIST_DIR):
    print(f"Error: {PERSIST_DIR} not found. Did you run the indexing script?")
    query_engine = None
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    # No changes needed here, but ensure this is global so the function can see it
    query_engine = index.as_query_engine() 
    print("Gemini Index loaded successfully.")

# 2. In your FastAPI route:
@app.post("/api/chat")
async def chat(payload: ChatRequest):
    if not query_engine:
        raise HTTPException(status_code=500, detail="Index not initialized")
    
    try:
        # Use aquery and await it
        response = await query_engine.aquery(payload.question)
        return {"response": str(response)}
    except Exception as e:
        print(f"Query Error: {e}")
        return {"response": f"Server Error: {str(e)}"}
    
if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)