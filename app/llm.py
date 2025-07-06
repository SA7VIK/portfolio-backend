import requests
import json
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class LLMInterface:
    def __init__(self, provider: str = "ollama", model_name: str = "llama2"):
        """
        Initialize LLM interface.
        
        Args:
            provider: "ollama", "openrouter", "huggingface", "groq", or "mock"
            model_name: Model name for the provider
        """
        self.provider = provider
        self.model_name = model_name
        self.api_key = None
        
        if provider == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
        elif provider == "groq":
            self.api_key = os.getenv("GROQ_API_KEY")
        
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using the selected LLM provider."""
        if self.provider == "ollama":
            return self._ollama_generate(prompt, context)
        elif self.provider == "openrouter":
            return self._openrouter_generate(prompt, context)
        elif self.provider == "groq":
            return self._groq_generate(prompt, context)
        elif self.provider == "huggingface":
            return self._huggingface_generate(prompt, context)
        elif self.provider == "mock":
            return self._mock_generate(prompt, context)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _mock_generate(self, prompt: str, context: str = "") -> str:
        """Generate mock response for testing without LLM."""
        if context:
            return f"Hey there! 👋 I'm Satvik's personal chatbot assistant. Based on the information I have about Satvik:\n\n{context}\n\nQuestion: {prompt}\n\nI'm currently running in mock mode for testing. In production, I'd give you a much more detailed and personalized response about Satvik! I can tell you about his skills, projects, experience, and more - just ask away! 😊"
        else:
            return f"Hi! I'm Satvik's personal chatbot assistant! 🤖\n\nQuestion: {prompt}\n\nI'm currently running in mock mode for testing. I'd love to help you learn about Satvik, but I need to be connected to a real language model first. Once that's set up, I'll be able to answer all your questions about Satvik's skills, projects, and experience! 😄"
    
    def _ollama_generate(self, prompt: str, context: str = "") -> str:
        """Generate response using Ollama (local)."""
        try:
            # Prepare the full prompt with context and system message
            system_message = "You are Satvik's personal chatbot assistant. Your role is to help visitors learn about Satvik by answering questions based on the information provided in his portfolio. Be polite, friendly, and slightly humorous when appropriate. Only provide information that you can find in the context provided by Satvik. If you don't have specific information about something, politely say 'I don't have that information about Satvik, but you can ask me about his skills, projects, experience, or other details I do know about!' Never make up or generate random information about Satvik."
            
            full_prompt = f"{system_message}\n\n{self._create_prompt(prompt, context)}"
            
            # Ollama API call
            url = "http://localhost:11434/api/generate"
            data = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "Sorry, I couldn't generate a response.")
            
        except requests.exceptions.RequestException as e:
            print(f"Ollama API error: {e}")
            return "Sorry, I'm having trouble connecting to the language model. Please make sure Ollama is running."
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, an error occurred while generating the response."
    
    def _openrouter_generate(self, prompt: str, context: str = "") -> str:
        """Generate response using OpenRouter (cloud)."""
        if not self.api_key:
            return "OpenRouter API key not configured. Please set OPENROUTER_API_KEY environment variable."
        
        try:
            full_prompt = self._create_prompt(prompt, context)
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are Satvik's personal chatbot assistant. Your role is to help visitors learn about Satvik by answering questions based on the information provided in his portfolio. Be polite, friendly, and slightly humorous when appropriate. Only provide information that you can find in the context provided by Satvik. If you don't have specific information about something, politely say 'I don't have that information about Satvik, but you can ask me about his skills, projects, experience, or other details I do know about!' Never make up or generate random information about Satvik."},
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            print(f"OpenRouter API error: {e}")
            return "Sorry, I'm having trouble connecting to the language model."
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, an error occurred while generating the response."
    
    def _huggingface_generate(self, prompt: str, context: str = "") -> str:
        """Generate response using Hugging Face (local)."""
        try:
            from transformers import pipeline
            
            # This is a simplified version - you might want to use a more sophisticated approach
            system_message = "You are Satvik's personal chatbot assistant. Your role is to help visitors learn about Satvik by answering questions based on the information provided in his portfolio. Be polite, friendly, and slightly humorous when appropriate. Only provide information that you can find in the context provided by Satvik. If you don't have specific information about something, politely say 'I don't have that information about Satvik, but you can ask me about his skills, projects, experience, or other details I do know about!' Never make up or generate random information about Satvik."
            
            full_prompt = f"{system_message}\n\n{self._create_prompt(prompt, context)}"
            
            # Use a simple text generation pipeline
            generator = pipeline("text-generation", model="gpt2", device=-1)  # CPU
            
            result = generator(full_prompt, max_length=200, num_return_sequences=1)
            return result[0]["generated_text"][len(full_prompt):].strip()
            
        except ImportError:
            return "Hugging Face transformers not installed. Please install with: pip install transformers torch"
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, an error occurred while generating the response."
    
    def _groq_generate(self, prompt: str, context: str = "") -> str:
        """Generate response using Groq (cloud)."""
        if not self.api_key:
            return "Groq API key not configured. Please set GROQ_API_KEY environment variable."
        
        try:
            full_prompt = self._create_prompt(prompt, context)
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,  # e.g., "llama3-8b-8192", "mixtral-8x7b-32768"
                "messages": [
                    {"role": "system", "content": "You are Satvik's personal chatbot assistant. Your role is to help visitors learn about Satvik by answering questions based on the information provided in his portfolio. Be polite, friendly, and slightly humorous when appropriate. Only provide information that you can find in the context provided by Satvik. If you don't have specific information about something, politely say 'I don't have that information about Satvik, but you can ask me about his skills, projects, experience, or other details I do know about!' Never make up or generate random information about Satvik."},
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            print(f"Groq API error: {e}")
            return "Sorry, I'm having trouble connecting to the language model."
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, an error occurred while generating the response."
    
    def _create_prompt(self, question: str, context: str = "") -> str:
        """Create a formatted prompt with context."""
        if context:
            prompt = f"""Based on the following information about Satvik, please answer the question.

Satvik's Information:
{context}

Question: {question}

Please provide a helpful and accurate response based on the information above. If the information doesn't contain details about the specific question, please say so politely."""
        else:
            prompt = f"""Question: {question}

Please provide a helpful response. If you don't have specific information about this, please say so politely."""
        
        return prompt
    
    def test_connection(self) -> bool:
        """Test if the LLM provider is accessible."""
        try:
            if self.provider == "ollama":
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                return response.status_code == 200
            elif self.provider == "openrouter":
                return self.api_key is not None
            elif self.provider == "groq":
                return self.api_key is not None
            elif self.provider == "mock":
                return True  # Mock always works
            else:
                return True
        except:
            return False
