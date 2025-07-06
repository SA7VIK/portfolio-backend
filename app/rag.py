import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional
import pickle
import os
from .utils import parse_markdown_to_chunks, clean_text

class RAGSystem:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize RAG system with embedding model and vector store."""
        self.model_name = model_name
        self.embedding_model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.chunk_embeddings = None
        
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts."""
        # Clean texts
        cleaned_texts = [clean_text(text) for text in texts]
        # Create embeddings
        embeddings = self.embedding_model.encode(cleaned_texts, show_progress_bar=True)
        return embeddings
    
    def build_index(self, markdown_content: str) -> None:
        """Build FAISS index from markdown content."""
        print("Building RAG index...")
        
        # Parse markdown into chunks
        self.chunks = parse_markdown_to_chunks(markdown_content)
        print(f"Created {len(self.chunks)} chunks")
        
        # Create embeddings
        self.chunk_embeddings = self.create_embeddings(self.chunks)
        
        # Build FAISS index with cosine similarity
        dimension = self.chunk_embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.chunk_embeddings)
        self.index.add(self.chunk_embeddings.astype('float32'))
        
        # Save the index
        faiss.write_index(self.index, "app/data/rag_index.pkl")
        
        print(f"Built FAISS index with {self.index.ntotal} vectors")
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Retrieve most relevant chunks for a query."""
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([clean_text(query)])
        
        # Normalize query embedding for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Return chunks with scores
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
        
        return results
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """Get formatted context for a query."""
        relevant_chunks = self.retrieve_relevant_chunks(query, top_k)
        
        if not relevant_chunks:
            return "I don't have specific information about that."
        
        context_parts = []
        for chunk, score in relevant_chunks:
            if score > 0.3:  # Only include chunks with good relevance
                context_parts.append(chunk)
        
        return "\n\n".join(context_parts) if context_parts else "I don't have specific information about that."
    
    def save_index(self, filepath: str = "app/data/rag_index.pkl") -> None:
        """Save the RAG index and chunks to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            'chunks': self.chunks,
            'embeddings': self.chunk_embeddings,
            'model_name': self.model_name
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"Saved RAG index to {filepath}")
    
    def load_index(self, filepath: str = "app/data/rag_index.pkl") -> bool:
        """Load the RAG index and chunks from disk."""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.chunks = data['chunks']
            self.chunk_embeddings = data['embeddings']
            self.model_name = data['model_name']
            
            # Rebuild FAISS index with cosine similarity
            dimension = self.chunk_embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(self.chunk_embeddings)
            self.index.add(self.chunk_embeddings.astype('float32'))
            
            print(f"Loaded RAG index with {len(self.chunks)} chunks")
            return True
            
        except FileNotFoundError:
            print(f"Index file {filepath} not found. Need to build index first.")
            return False
        except Exception as e:
            print(f"Error loading index: {e}")
            return False

def chunk_text(text, chunk_size=500):
    # Simple chunking by character count (customize as needed)
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
