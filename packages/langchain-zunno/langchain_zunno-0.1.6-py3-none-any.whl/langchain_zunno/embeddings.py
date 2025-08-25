"""
LangChain Embeddings integration for Zunno.
"""

from typing import List, Union, Dict, Any
from langchain.embeddings.base import Embeddings
import requests
import json


class ZunnoLLMEmbeddings(Embeddings):
    """Zunno Embeddings wrapper for LangChain."""
    
    model_name: str
    base_url: str = "http://13.203.232.8/v1/text-embeddings"
    timeout: int = 300
    return_full_response: bool = False
    
    def __init__(self, model_name: str, base_url: str = None, timeout: int = 300, return_full_response: bool = False):
        super().__init__()
        self.model_name = model_name
        if base_url:
            self.base_url = base_url
        self.timeout = timeout
        self.return_full_response = return_full_response
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = []
        for text in texts:
            embedding = self.embed_query(text)
            if isinstance(embedding, list):
                embeddings.append(embedding)
            else:
                # If full response is returned, extract embeddings
                try:
                    data = json.loads(embedding) if isinstance(embedding, str) else embedding
                    embeddings.append(data.get("embeddings", []))
                except:
                    embeddings.append([])
        return embeddings
    
    def embed_query(self, text: str) -> Union[List[float], str]:
        """Embed a single query."""
        try:
            payload = {
                "model_name": self.model_name,
                "text": text,
                "options": {
                    "normalize": True
                }
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Zunno embeddings API error: {response.text}")
            
            data = response.json()
            
            # Return full response if requested, otherwise just the embeddings
            if self.return_full_response:
                return json.dumps(data, indent=2)
            else:
                embeddings = data.get("embeddings", [])
                if not embeddings:
                    raise Exception("No embeddings returned from API")
                return embeddings
            
        except Exception as e:
            raise Exception(f"Error getting text embeddings: {e}")
    
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Async embed a list of documents."""
        embeddings = []
        for text in texts:
            embedding = await self.aembed_query(text)
            if isinstance(embedding, list):
                embeddings.append(embedding)
            else:
                # If full response is returned, extract embeddings
                try:
                    data = json.loads(embedding) if isinstance(embedding, str) else embedding
                    embeddings.append(data.get("embeddings", []))
                except:
                    embeddings.append([])
        return embeddings
    
    async def aembed_query(self, text: str) -> Union[List[float], str]:
        """Async embed a single query."""
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model_name": self.model_name,
                    "text": text,
                    "options": {
                        "normalize": True
                    }
                }
                
                response = await client.post(
                    self.base_url,
                    json=payload
                )
                
                if response.status_code != 200:
                    raise Exception(f"Zunno embeddings API error: {response.text}")
                
                data = response.json()
                
                # Return full response if requested, otherwise just the embeddings
                if self.return_full_response:
                    return json.dumps(data, indent=2)
                else:
                    embeddings = data.get("embeddings", [])
                    if not embeddings:
                        raise Exception("No embeddings returned from API")
                    return embeddings
                
        except Exception as e:
            raise Exception(f"Error getting text embeddings: {e}")


def create_zunno_embeddings(
    model_name: str,
    base_url: str = "http://13.203.232.8/v1/text-embeddings",
    timeout: int = 300,
    return_full_response: bool = False
) -> ZunnoLLMEmbeddings:
    """Create a Zunno Embeddings instance."""
    return ZunnoLLMEmbeddings(
        model_name=model_name,
        base_url=base_url,
        timeout=timeout,
        return_full_response=return_full_response
    ) 