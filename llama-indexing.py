import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.core.schema import TextNode
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

# 1. Load Environment
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# 2. Configure Models
Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash", api_key=api_key)
embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-2-preview", api_key=api_key)
Settings.embed_model = embed_model

def create_manual_index(folder_path):
    print(f"Reading files from: {folder_path}")
    documents = SimpleDirectoryReader(input_dir=folder_path).load_data()
    
    # 3. Parse into Nodes
    parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
    raw_nodes = parser.get_nodes_from_documents(documents)
    
    # 4. Create clean nodes with embeddings PRE-CALCULATED
    # This prevents LlamaIndex from having to "find" nodes later
    print(f"Generating embeddings for {len(raw_nodes)} chunks...")
    final_nodes = []
    for i, node in enumerate(raw_nodes):
        # Manually get the embedding for each text chunk
        text_embedding = embed_model.get_text_embedding(node.get_content())
        
        # Create a fresh node with the embedding already attached
        new_node = TextNode(
            text=node.get_content(),
            id_=f"chunk_{i}",
            embedding=text_embedding,
            metadata=node.metadata
        )
        final_nodes.append(new_node)

    print("Building Vector Store...")
    # 5. Build index from nodes that ALREADY have embeddings
    # This skips the broken 'batch' process that causes the KeyError
    index = VectorStoreIndex(final_nodes)
    return index

if __name__ == "__main__":
    try:
        index = create_manual_index("docx")
        index.storage_context.persist(persist_dir="./storage")
        print("Index saved to ./storage")
        query_engine = index.as_query_engine()
        
        print("\n--- Final Test Query ---")
        response = query_engine.query("Summarize the key points of these documents.")
        print(f"\nResponse:\n{response}")
        
    except Exception as e:
        print(f"\nManual Indexing Error: {e}")