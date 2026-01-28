# California DMV RAG System

A Retrieval-Augmented Generation (RAG) system for answering questions about California DMV rules and regulations.

## Features

- **Web Scraping**: Scrapes 42 pages from the California DMV website
- **Vector Database**: Uses FAISS for efficient similarity search
- **Embeddings**: Leverages sentence-transformers (all-MiniLM-L6-v2)
- **LLM Integration**: Powered by OpenAI GPT-3.5-turbo
- **Comprehensive Coverage**: 105 chunks, 21,433 words from multiple DMV resources

## Dataset Coverage

- Driver Handbook (core content)
- Motorcyclists Guide
- Truck/Commercial Drivers
- Teen Drivers
- Senior Drivers
- Bicyclists & Pedestrians
- Practice Tests & Educational Materials
- Boat & Vessel Registration
- Special Interest Guides

## Setup

1. Install dependencies:
```bash
pip install requests beautifulsoup4 faiss-cpu sentence-transformers openai
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

### 1. Scrape DMV Content
```bash
python3 scrape_dmv.py
```
Creates `dmv_handbook_data.json` with 105 chunks from 42 pages.

### 2. Build Vector Database
```bash
python3 create_vector_db.py
```
Creates `dmv_faiss.index` and `dmv_metadata.pkl`.

### 3. Run RAG Agent
```bash
python3 rag_agent.py
```
Interactive Q&A system combining retrieval and GPT generation.

### Alternative: Query Vector DB Only
```bash
python3 query_vectordb.py
```
Test retrieval without LLM generation.

## Project Structure

```
RAG/
├── scrape_dmv.py           # Web scraper for DMV content
├── dmv_handbook_data.json  # Scraped data (105 chunks)
├── create_vector_db.py     # Vector database builder
├── dmv_faiss.index         # FAISS index (gitignored)
├── dmv_metadata.pkl        # Chunk metadata (gitignored)
├── query_vectordb.py       # Vector search interface
└── rag_agent.py            # Full RAG system with GPT
```

## Example Questions

- "What is the speed limit in school zones?"
- "How do I get a motorcycle license?"
- "What are the rules for teen drivers?"
- "What protective gear is required for motorcyclists?"
- "Where can I find DMV practice tests?"

## Stats

- **105 chunks** of content
- **38 unique pages** scraped
- **21,433 words** total
- **~86 equivalent pages** of text
- **311 KB** total storage

## Architecture

1. **Retrieval**: FAISS vector search finds top 3 relevant chunks
2. **Generation**: OpenAI GPT-3.5-turbo generates answers from retrieved context



