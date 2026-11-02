from data_handlers.embed_manager import EMBEDDING_MODEL, METADATA_PATH, FAISS_INDEX_PATH

import ollama
import faiss
import numpy as np
import json

MAX_DISTANCE = 1.5 # 1.0

def retrieve_from_memory(query, top_k=5):
    # Load the FAISS index and metadata
    faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))
    with open(METADATA_PATH, 'r', encoding="utf-8") as f:
        metadata = json.load(f)

    # Embed the query using the same embedding model
    ollama_client = ollama.Client()
    response = ollama_client.embed(model=EMBEDDING_MODEL, input=query)
    query_embedding = np.array(response.embeddings, dtype=np.float32)

    # Search for the top-k most similar chunks
    D, I = faiss_index.search(query_embedding, top_k)
    # Retrieve the corresponding metadata
    results = []
    for i in range(top_k):
        idx = I[0][i]
        if idx < 0:
            continue
        distance = float(D[0][i])
        if distance > MAX_DISTANCE:
                    continue
        entry = metadata[idx]
        results.append({
            'file_name': entry['file_name'],
            'chunk_index': entry['chunk_index'],
            'chunk_text': entry['chunk_text'],
            'distance': distance
        })

    # Stop the Ollama client
    ollama_client.embed(model=EMBEDDING_MODEL, input="", keep_alive=0)
    return results
