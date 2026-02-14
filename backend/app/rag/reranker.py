from flashrank import Ranker, RerankRequest
from app.core.config import settings

class MedicalReranker:
    def __init__(self):
        # High-speed model that doesn't need a GPU
        self.ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="/tmp/")

    def rerank(self, query: str, documents: list, top_n: int = 3):
        if not documents:
            return []
        
        # Format for FlashRank
        passages = [
            {"id": i, "text": doc.page_content, "meta": doc.metadata} 
            for i, doc in enumerate(documents)
        ]
        
        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)
        
        # Return only the top_n most relevant medical chunks
        return results[:top_n]