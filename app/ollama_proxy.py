import httpx
from fastapi import HTTPException
from typing import Dict, Any
import json

class OllamaProxy:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
    
    async def forward_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None):
        """Forward request to Ollama API"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url)
                else:
                    raise HTTPException(status_code=405, detail="Method not allowed")
                
                return response.json(), response.status_code
                
            except httpx.RequestError as e:
                raise HTTPException(status_code=503, detail=f"Ollama service unavailable: {str(e)}")
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Invalid JSON response from Ollama")
    
    async def list_models(self):
        """List available models"""
        return await self.forward_request("GET", "/api/tags")
    
    async def generate(self, data: Dict[str, Any]):
        """Generate text using a model"""
        return await self.forward_request("POST", "/api/generate", data=data)
    
    async def chat(self, data: Dict[str, Any]):
        """Chat with a model"""
        return await self.forward_request("POST", "/api/chat", data=data)
    
    async def pull_model(self, data: Dict[str, Any]):
        """Pull a model"""
        return await self.forward_request("POST", "/api/pull", data=data)
    
    async def push_model(self, data: Dict[str, Any]):
        """Push a model"""
        return await self.forward_request("POST", "/api/push", data=data)
    
    async def create_model(self, data: Dict[str, Any]):
        """Create a model"""
        return await self.forward_request("POST", "/api/create", data=data)
    
    async def delete_model(self, name: str):
        """Delete a model"""
        return await self.forward_request("DELETE", f"/api/delete", data={"name": name})
    
    async def show_model(self, data: Dict[str, Any]):
        """Show model information"""
        return await self.forward_request("POST", "/api/show", data=data) 