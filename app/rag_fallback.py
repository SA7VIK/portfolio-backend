import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional
import pickle
import os
from sklearn.metrics.pairwise import cosine_similarity
from .utils import parse_markdown_to_chunks, clean_text

class RAGSystemFallback:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize RAG system with embedding model and scikit-learn fallback."""
        self.model_name = model_name
        self.embedding_model = SentenceTransformer(model_name)
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
        """Build similarity index from markdown content using scikit-learn."""
        print("Building RAG index (fallback mode)...")
        
        # Parse markdown into chunks
        self.chunks = parse_markdown_to_chunks(markdown_content)
        print(f"Created {len(self.chunks)} chunks")
        
        # Create embeddings
        self.chunk_embeddings = self.create_embeddings(self.chunks)
        
        print(f"Built similarity index with {len(self.chunks)} vectors")
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Retrieve most relevant chunks for a query using cosine similarity."""
        if self.chunk_embeddings is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([clean_text(query)])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_embedding, self.chunk_embeddings)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Return chunks with scores
        results = []
        for idx in top_indices:
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(similarities[idx])))
        
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
            
            print(f"Loaded RAG index with {len(self.chunks)} chunks")
            return True
            
        except FileNotFoundError:
            print(f"Index file {filepath} not found. Need to build index first.")
            return False
        except Exception as e:
            print(f"Error loading index: {e}")
            return False 