import faiss
import pickle
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import os

# Get API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("Please set OPENAI_API_KEY environment variable")

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

# Load FAISS index and metadata
print("Loading vector database...")
index = faiss.read_index("dmv_faiss.index")

with open("dmv_metadata.pkl", "rb") as f:
    chunks = pickle.load(f)

model = SentenceTransformer('all-MiniLM-L6-v2')

print(f"Vector database ready! {index.ntotal} chunks indexed.")
print("OpenAI connected!\n")

def retrieve_context(query, top_k=3):
    """
    Retrieve relevant chunks from vector database
    
    Args:
        query: User's question
        top_k: Number of chunks to retrieve (default: 3)
    
    Returns:
        List of relevant chunk contents
    """
    # Convert query to embedding
    query_embedding = model.encode([query])
    
    # Search FAISS index
    distances, indices = index.search(query_embedding.astype('float32'), top_k)
    
    # Get the actual chunk content
    relevant_chunks = []
    for idx in indices[0]:
        chunk = chunks[idx]
        relevant_chunks.append({
            "content": chunk["content"],
            "source": f"{chunk['page_title']} > {chunk['section_title']}",
            "url": chunk["url"]
        })
    
    return relevant_chunks

def generate_answer(query, context_chunks):
    """
    Generate answer using OpenAI GPT with retrieved context
    
    Args:
        query: User's question
        context_chunks: List of relevant chunks from vector DB
    
    Returns:
        Generated answer from GPT
    """
    # Build context from retrieved chunks
    context = "\n\n".join([
        f"Source {i+1} ({chunk['source']}):\n{chunk['content']}" 
        for i, chunk in enumerate(context_chunks)
    ])
    
    # Create the system prompt
    system_prompt = """You are a helpful assistant for the California DMV Driver Handbook.

Your job is to answer questions about California driving laws and rules based ONLY on the provided context from the official handbook.

Rules:
- Use ONLY information from the provided context
- Be accurate and cite which source you're using
- If the answer is not in the context, say "I don't have that information in the handbook sections I found."
- Be concise but complete
- Use a friendly, helpful tone"""

    # Create user prompt with context
    user_prompt = f"""Context from California DMV Driver Handbook:

{context}

---

Question: {query}

Please answer based on the context above."""

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Fast and cheap (~$0.0005 per query)
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,  
        max_tokens=400,   # Limit response length
    )
    
    return response.choices[0].message.content

def rag_query(question, show_sources=True):
    """
    Complete RAG pipeline: Retrieve relevant chunks + Generate answer
    
    Args:
        question: User's question
        show_sources: Whether to display retrieved sources
    
    Returns:
        Generated answer
    """
    print("Searching for relevant information...")
    
    # Step 1: Retrieve relevant chunks from vector DB
    context_chunks = retrieve_context(question, top_k=3)
    
    print(f"Found {len(context_chunks)} relevant sections")
    
    if show_sources:
        print("\nSources used:")
        for i, chunk in enumerate(context_chunks, 1):
            print(f"   {i}. {chunk['source']}")
    
    print("\nGenerating answer with GPT...\n")
    
    # Step 2: Generate answer using GPT with retrieved context
    answer = generate_answer(question, context_chunks)
    
    return answer, context_chunks

# Interactive loop
print("=" * 70)
print("California DMV Handbook AI Assistant (RAG with GPT)")
print("=" * 70)
print("Ask me anything about California driving rules!")
print("Type 'sources' to toggle source display")
print("Type 'quit' to exit\n")

show_sources = True

while True:
    question = input("Your question: ").strip()
    
    if question.lower() in ['quit', 'exit', 'q']:
        print("\nGoodbye! Drive safely! ")
        break
    
    if question.lower() == 'sources':
        show_sources = not show_sources
        print(f"\n Source display: {'ON' if show_sources else 'OFF'}\n")
        continue
    
    if not question:
        continue
    
    try:
        answer, sources = rag_query(question, show_sources=show_sources)
        
        print("=" * 70)
        print("Answer:")
        print(answer)
        print("=" * 70)
        
        if show_sources:
            print("\n Full sources:")
            for i, chunk in enumerate(sources, 1):
                print(f"{i}. {chunk['url']}")
        
        print()
        
    except Exception as e:
        print(f"\n Error: {e}\n")
        print("Check your API key and internet connection.\n")