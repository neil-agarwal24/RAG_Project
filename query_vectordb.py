import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the FAISS index
print("Loading FAISS index...")
index = faiss.read_index("dmv_faiss.index")

# Load metadata
print("Loading metadata...")
with open("dmv_metadata.pkl", "rb") as f:
    chunks = pickle.load(f)

# Load the same embedding model
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print(f"\n Database ready! {index.ntotal} chunks indexed.\n")

def search(query, top_k=3):
    """
    Search for chunks similar to the query
    
    Args:
        query: User's question (string)
        top_k: Number of results to return (default: 3)
    
    Returns:
        List of matching chunks with similarity scores
    """
    # Convert query to embedding
    query_embedding = model.encode([query])
    
    # Search the index
    # Returns: distances and indices of top_k nearest vectors
    distances, indices = index.search(query_embedding.astype('float32'), top_k)
    
    # Build results
    results = []
    for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
        chunk = chunks[idx]
        results.append({
            "rank": i + 1,
            "chunk_id": chunk["chunk_id"],
            "page_title": chunk["page_title"],
            "section_title": chunk["section_title"],
            "content": chunk["content"],
            "url": chunk["url"],
            "distance": float(distance),  # Lower = more similar
            "similarity_score": 1 / (1 + distance)  # Convert to 0-1 score
        })
    
    return results

# Interactive query loop
print("=" * 60)
print("DMV Handbook Q&A System (Vector Search)")
print("=" * 60)
print("Ask questions about California driving rules!")
print("Type 'quit' to exit\n")

while True:
    query = input("Your question: ").strip()
    
    if query.lower() in ['quit', 'exit', 'q']:
        print("\nGoodbye!")
        break
    
    if not query:
        continue
    
    print("\n Searching...")
    results = search(query, top_k=3)
    
    print(f"\nTop {len(results)} relevant sections:\n")
    
    for result in results:
        print(f" Rank {result['rank']} - {result['page_title']} > {result['section_title']}")
        print(f"   Similarity: {result['similarity_score']:.3f}")
        print(f"   {result['content'][:200]}...")  # First 200 chars
        print(f"   Source: {result['url']}")
        print()
    
    print("-" * 60)