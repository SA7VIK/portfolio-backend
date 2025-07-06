import re
import markdown
from typing import List, Dict, Any
import os

def load_personal_info(file_path: str = "app/data/personal_info.md") -> str:
    """Load personal information from markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. Using default content.")
        return "# Personal Information\n\nThis is a placeholder for personal information."

def parse_markdown_to_chunks(markdown_text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Parse markdown text into chunks for RAG."""
    # Convert markdown to plain text
    html = markdown.markdown(markdown_text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html)
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Create chunks
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\:]', '', text)
    return text.strip()

def format_response(response: str) -> str:
    """Format the LLM response for better presentation."""
    # Add line breaks for better readability
    response = response.replace('. ', '.\n\n')
    return response.strip()

def validate_question(question: str) -> bool:
    """Validate if the question is appropriate."""
    if not question or len(question.strip()) < 3:
        return False
    
    # Check for inappropriate content (basic filter)
    inappropriate_words = ['hack', 'crack', 'illegal', 'spam']
    question_lower = question.lower()
    
    for word in inappropriate_words:
        if word in question_lower:
            return False
    
    return True
