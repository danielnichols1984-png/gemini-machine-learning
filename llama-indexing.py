# This is the file for training the model
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("API key: " + api_key[0:6])
else:
    print("API key not found")

print("Indexing from:", os.path.abspath("pdf"))
# Load documents
documents = SimpleDirectoryReader("pdf").load_data()

# Application Verification / Not needed for application
print(f"Loaded {len(documents)} documents")
for d in documents:
    print("Document preview:", d.text[:200])


# Create index
index = VectorStoreIndex.from_documents(documents)
print("Index built successfully")

# Nodes for verification / Not needed for application
nodes = index.storage_context.docstore.docs
print("Number of nodes:", len(nodes))

# Create query engine
engine = index.as_query_engine()


index.storage_context.persist("ml_index")