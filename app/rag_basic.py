import re
from typing import List, Tuple, Optional
import pickle
import os
from .utils import parse_markdown_to_chunks, clean_text

class RAGSystemBasic:
    def __init__(self):
        """Initialize basic RAG system with simple text matching."""
        self.chunks = []
        
    def calculate_similarity(self, query: str, text: str) -> float:
        """Calculate simple text similarity using word overlap."""
        query_words = set(re.findall(r'\w+', query.lower()))
        text_words = set(re.findall(r'\w+', text.lower()))
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(text_words)
        union = query_words.union(text_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def build_index(self, markdown_content: str) -> None:
        """Build basic index from markdown content."""
        print("Building RAG index (basic mode)...")
        
        # Parse markdown into chunks
        self.chunks = parse_markdown_to_chunks(markdown_content)
        print(f"Created {len(self.chunks)} chunks")
        
        print(f"Built basic index with {len(self.chunks)} chunks")
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Retrieve most relevant chunks using simple text similarity."""
        if not self.chunks:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Calculate similarities
        similarities = []
        for chunk in self.chunks:
            similarity = self.calculate_similarity(query, chunk)
            similarities.append((chunk, similarity))
        
        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """Get formatted context for a query."""
        relevant_chunks = self.retrieve_relevant_chunks(query, top_k)
        
        if not relevant_chunks:
            return "I don't have specific information about that."
        
        context_parts = []
        for chunk, score in relevant_chunks:
            if score > 0.1:  # Lower threshold for basic matching
                context_parts.append(chunk)
        
        return "\n\n".join(context_parts) if context_parts else "I don't have specific information about that."
    
    def save_index(self, filepath: str = "app/data/rag_index.pkl") -> None:
        """Save the RAG index and chunks to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            'chunks': self.chunks
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
            
            print(f"Loaded RAG index with {len(self.chunks)} chunks")
            return True
            
        except FileNotFoundError:
            print(f"Index file {filepath} not found. Need to build index first.")
            return False
        except Exception as e:
            print(f"Error loading index: {e}")
            return False 