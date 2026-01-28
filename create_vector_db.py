import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle

print("Loading DMV handbook data...")
# Load your scraped data
with open("dmv_handbook_data.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")

# Initialize embedding model
print("\nLoading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
# This model converts text → 384-dimensional vectors
# It's fast, small, and works well for semantic search

print("Creating embeddings for all chunks...")
# Extract just the content text from each chunk
texts = [chunk["content"] for chunk in chunks]

# Convert all texts to embeddings
embeddings = model.encode(texts, show_progress_bar=True)
# embeddings is now a numpy array: shape (73, 384)
# 73 chunks, each represented by 384 numbers

print(f"Embeddings shape: {embeddings.shape}")

# Create FAISS index
print("\nBuilding FAISS index...")
dimension = embeddings.shape[1]  # 384
index = faiss.IndexFlatL2(dimension)
# IndexFlatL2 = Simple index using L2 (Euclidean) distance
# "Flat" means it checks ALL vectors (exact search, not approximate)

# Add embeddings to the index
index.add(embeddings.astype('float32'))
# FAISS requires float32 format

print(f"Index contains {index.ntotal} vectors")

# Save the FAISS index to disk
print("\nSaving FAISS index...")
faiss.write_index(index, "dmv_faiss.index")

# Save metadata separately (FAISS only stores vectors, not your chunk data)
print("Saving metadata...")
with open("dmv_metadata.pkl", "wb") as f:
    pickle.dump(chunks, f)

print("\n Vector database created successfully!")
print("Files created:")
print("  - dmv_faiss.index (vector index)")
print("  - dmv_metadata.pkl (chunk metadata)")