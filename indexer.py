# app/indexer.py
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def build_index():
    with open("catalog.json", "r") as f:
        data = json.load(f)
    
    # This model turns text into numbers (vectors)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    texts = [f"{item['name']}" for item in data]
    embeddings = model.encode(texts)
    
    # Create the FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype('float32'))
    
    faiss.write_index(index, "catalog.index")
    print("Success: catalog.index created.")

if __name__ == "__main__":
    build_index()