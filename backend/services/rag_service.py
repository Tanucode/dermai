"""
services/rag_service.py
------------------------
RAG = Retrieval Augmented Generation

CONCEPT — What is RAG?
  Without RAG: You ask AI "what helps dark circles?" → AI guesses from training data
  With RAG:    You FIRST search your own knowledge base → find relevant facts
               THEN feed those facts to AI → AI gives grounded, accurate answers

WHY IT MATTERS for your resume:
  RAG is used by almost every serious AI product company (Google, OpenAI, Anthropic).
  Knowing how to build a RAG pipeline is a highly sought-after skill.

HOW IT WORKS HERE:
  1. At startup, we load skincare documents (ingredients.txt, routines.txt, etc.)
  2. We convert them to "embeddings" (numerical vectors that capture meaning)
  3. We store those vectors in ChromaDB (a vector database)
  4. When user has skin issues, we search ChromaDB for relevant information
  5. We pass retrieved text to Gemini as context for better recommendations

VECTOR DATABASE:
  A vector database stores meaning, not just keywords.
  e.g. "niacinamide helps pigmentation" and "B3 vitamin treats dark spots"
       are stored NEAR each other because they MEAN the same thing.
"""

import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# Path to our knowledge base documents
DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "skincare_dataset.json")
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

# Global variable to hold our vector store (loaded once at startup)
_vector_store = None


def initialize_rag():
    """
    Called once when the FastAPI app starts.
    Loads all documents, creates embeddings, stores in ChromaDB.

    CONCEPT — Embeddings:
      Text → embedding model → [0.23, -0.67, 0.91, ...] (a vector of 768 numbers)
      Similar texts produce similar vectors.
      This is how semantic search works!
    """
    global _vector_store

    try:
        # Use local HuggingFace embedding model (No API key needed, never throws 404!)
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        # If ChromaDB already exists, just load it (don't re-embed everything)
        if os.path.exists(CHROMA_DB_PATH):
            print("[RAG] Loading existing ChromaDB...")
            _vector_store = Chroma(
                persist_directory=CHROMA_DB_PATH,
                embedding_function=embeddings
            )
            print(f"[RAG] Loaded {_vector_store._collection.count()} documents")
            return

        # First time: load JSON documents and create the vector store
        print("[RAG] Creating ChromaDB from JSON dataset for the first time...")
        import json

        documents = []
        if os.path.exists(DATASET_PATH):
            with open(DATASET_PATH, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
                for item in dataset:
                    # Construct a rich text document for embedding
                    text_content = f"Ingredient: {item['ingredient_name']}\n"
                    text_content += f"Description: {item['description']}\n"
                    text_content += f"Benefits: {', '.join(item['benefits'])}\n"
                    text_content += f"Good for: {', '.join(item['good_for'])}\n"
                    text_content += f"Clinical Notes: {item['clinical_notes']}"
                    
                    doc = Document(
                        page_content=text_content,
                        metadata={"ingredient": item["ingredient_name"]}
                    )
                    documents.append(doc)
        else:
            print(f"[RAG] Dataset not found at {DATASET_PATH}")
            return

        print(f"[RAG] Loaded {len(documents)} clinical ingredient documents")

        # Split documents into smaller chunks
        # WHY: AI models have context limits. Smaller chunks = more precise retrieval.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,    # Each chunk = max 500 characters
            chunk_overlap=50   # 50 character overlap so we don't cut mid-sentence
        )
        chunks = text_splitter.split_documents(documents)
        print(f"[RAG] Split into {len(chunks)} chunks")

        # Create and persist ChromaDB
        _vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_DB_PATH
        )
        print("[RAG] ChromaDB created and saved!")

    except Exception as e:
        print(f"[RAG] Warning: Could not initialize RAG: {e}")
        print("[RAG] The app will still work, but recommendations may be less specific.")
        _vector_store = None


def query_knowledge_base(skin_concerns: list[str], skin_type: str) -> str:
    """
    Searches our knowledge base for information relevant to the user's skin issues.

    Args:
        skin_concerns: List of detected issues e.g. ["Dark Circles", "Acne"]
        skin_type: e.g. "oily"

    Returns:
        A string of relevant skincare knowledge to feed into Gemini as context.
    """
    if _vector_store is None:
        return _get_hardcoded_context(skin_concerns, skin_type)

    try:
        # Build a natural language query from the skin issues
        query = f"Treatment and ingredients for {', '.join(skin_concerns)} on {skin_type} skin"
        print(f"[RAG] Querying: {query}")

        # Retrieve top 5 most relevant document chunks
        # k=5 means "give me 5 most similar results"
        relevant_docs = _vector_store.similarity_search(query, k=5)

        # Combine all retrieved text into one context string
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
        print(f"[RAG] Retrieved {len(relevant_docs)} relevant chunks")

        return context

    except Exception as e:
        print(f"[RAG] Query error: {e}")
        return _get_hardcoded_context(skin_concerns, skin_type)


def _get_hardcoded_context(skin_concerns: list[str], skin_type: str) -> str:
    """
    Fallback context if RAG is not available.
    Provides basic skincare knowledge directly.
    """
    return f"""
SKINCARE KNOWLEDGE BASE:

For {skin_type} skin with concerns: {', '.join(skin_concerns)}

KEY INGREDIENTS:
- Niacinamide (5-10%): Reduces dark spots, controls sebum, minimizes pores
- Hyaluronic Acid: Deep hydration, plumps skin, suitable for all skin types
- Vitamin C (10-20%): Brightens skin, fades dark spots, antioxidant protection
- Retinol (0.025-1%): Anti-aging, speeds cell turnover, reduces wrinkles
- Salicylic Acid (0.5-2%): Unclogs pores, treats acne, exfoliates inside pores
- Ceramides: Repairs skin barrier, reduces redness, prevents moisture loss
- Azelaic Acid (10-20%): Treats dark spots, rosacea, and acne simultaneously
- Caffeine: Reduces puffiness and dark circles under eyes
- Kojic Acid: Natural skin brightener, reduces melanin production

ROUTINE ORDER (always apply thinnest to thickest):
1. Cleanser → 2. Toner → 3. Serum → 4. Moisturizer → 5. SPF (morning only)

DIET FOR SKIN:
- Eat: Antioxidant-rich foods, omega-3 fatty acids, vitamins A, C, E, zinc
- Avoid: High-glycemic foods (spike insulin = more acne), alcohol, smoking
- Hydration: 8 glasses of water minimum per day
"""
