"""
Infrastructure - Vector DB Repository Implementation (Knowledge Base)
"""
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from LLM_AWS.domain.repositories import IVectorDBRepository
from LLM_AWS.domain.entities import VectorSearchResult


class QdrantVectorDBRepository(IVectorDBRepository):
    def __init__(self, qdrant_url: str, qdrant_key: str, gemini_key: str, collection_name: str = "nfl_wiki_gemini_3072"):
        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_key, check_compatibility=False)
        self.collection_name = collection_name
        self.dim = 3072  # Sử dụng 3072 dim cho knowledge base
        
        genai.configure(api_key=gemini_key)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Tạo embedding cho query"""
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"Embedding error: {e}")
            raise
    
    def search(self, query: str, limit: int = 3) -> List[VectorSearchResult]:
        """Tìm kiếm trong knowledge base"""
        try:
            query_vector = self._get_embedding(query)
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True
            )
            
            return [
                VectorSearchResult(
                    content=hit.payload.get('content', ''),
                    metadata={
                        'title': hit.payload.get('title', ''),
                        'url': hit.payload.get('url', ''),
                        'metadata': hit.payload.get('metadata', {})
                    },
                    score=hit.score
                )
                for hit in results
            ]
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
