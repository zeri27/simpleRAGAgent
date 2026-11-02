from data_handlers.data_manager import load_manifest, scan, STORAGE_DIR, DATA_DIR

import ollama
import faiss
import numpy as np
import json

METADATA_PATH = STORAGE_DIR / "metadata.json"
FAISS_INDEX_PATH = STORAGE_DIR / "faiss_index.bin"
EMBEDDING_MODEL = "all-minilm:l6-v2"

def embed():
    manifest = load_manifest()
    scanned_manifest = scan()

    # If the manifest has changed, rebuild the FAISS index
    if manifest != scanned_manifest or not FAISS_INDEX_PATH.exists() or not METADATA_PATH.exists():
        ollama_client = ollama.Client()
        # Re-embed all files
        embeddings = []
        metadata = []
        for file_name in scanned_manifest:
            file_path = DATA_DIR / file_name
            with file_path.open("r", encoding="utf-8") as f:
                content = f.read()
                # Split content into chunks of 600 characters
                chunk_size = 600
                chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]
                if not chunks:
                    continue

                response = ollama_client.embed(model=EMBEDDING_MODEL, input=chunks)
                embeddings.extend(response.embeddings)
                # Save metadata for each chunk
                for i, chunk in enumerate(chunks):
                    metadata.append({
                        "file_name": file_name,
                        "chunk_index": i,
                        "chunk_text": chunk
                    })
                print(f"Embedded {len(chunks)} chunks from {file_name}")

        if not embeddings:
            ollama_client.embed(model=EMBEDDING_MODEL, input="", keep_alive=0)
            return None

        # Convert embeddings to numpy array
        embeddings = np.array(embeddings).astype('float32')
        # Create a new FAISS index
        faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
        # Add new embeddings to the FAISS index
        faiss_index.add(embeddings)
        # Save the updated FAISS index
        faiss.write_index(faiss_index, str(FAISS_INDEX_PATH))
        # Save metadata
        with METADATA_PATH.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        ollama_client.embed(model=EMBEDDING_MODEL, input="", keep_alive=0)

    return None