#!/usr/bin/env python3
"""
Example usage of the Ollama API Middleware
This script demonstrates how to use the API with authentication
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your-api-key-here"  # Replace with your actual API key

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def list_models():
    """List available models"""
    try:
        response = requests.get(f"{BASE_URL}/api/tags", headers=headers)
        response.raise_for_status()
        models = response.json()
        print("Available models:")
        for model in models.get("models", []):
            print(f"  - {model['name']}")
        return models
    except requests.exceptions.RequestException as e:
        print(f"Error listing models: {e}")
        return None

def generate_text(model="llama2", prompt="Hello, how are you?"):
    """Generate text using a model"""
    try:
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(f"{BASE_URL}/api/generate", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print(f"Generated text: {result.get('response', 'No response')}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error generating text: {e}")
        return None

def chat_with_model(model="llama2", message="Hello!"):
    """Chat with a model"""
    try:
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": message}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/chat", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print(f"Chat response: {result.get('message', {}).get('content', 'No response')}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error chatting with model: {e}")
        return None

def main():
    print("🤖 Ollama API Middleware Example")
    print("=" * 40)
    
    # First, get your API key from the web interface
    print("1. Get your API key from http://localhost:8000")
    print("2. Update the API_KEY variable in this script")
    print("3. Make sure Ollama is running on localhost:11434")
    print()
    
    if API_KEY == "your-api-key-here":
        print("❌ Please update the API_KEY variable with your actual API key")
        return
    
    # List available models
    print("📋 Listing available models...")
    models = list_models()
    
    if models:
        # Try to generate text
        print("\n📝 Generating text...")
        generate_text("llama2", "Explain what is artificial intelligence in one sentence.")
        
        # Try to chat
        print("\n💬 Chatting with model...")
        chat_with_model("llama2", "What's the weather like today?")
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    main() 