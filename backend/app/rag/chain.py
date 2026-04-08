# Simple RAG chain implementation using direct Groq API calls
import requests
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("rag_chain")

def get_rag_chain():
    """Return a callable RAG chain function."""
    def rag_chain(query: str, context_docs: list | None = None) -> str:
        """Generate an answer from Groq using retrieved context documents."""
        context = ""
        if context_docs:
            formatted_docs = []
            for doc in context_docs[: settings.TOP_K]:
                metadata = getattr(doc, "metadata", {}) or {}
                source = metadata.get("source", "Unknown source")
                page = metadata.get("page", "N/A")
                formatted_docs.append(
                    f"Source: {source} (Page {page})\n{doc.page_content.strip()}"
                )
            context = "\n\n".join(formatted_docs)
            context = f"Context from medical documents:\n{context}\n\n"

        prompt = (
            "You are a medical AI assistant. Answer the user's question based on the provided context. "
            "If the context does not contain the answer, say you don't know rather than inventing facts. "
            "Use citations from the context when available.\n\n"
            f"{context}Question: {query}\n\nAnswer:"
        )

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": settings.TEMPERATURE,
            "max_tokens": 1000,
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            logger.info("RAG chain completed successfully")
            return answer.strip()
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise RuntimeError(f"Failed to generate answer from Groq: {str(e)}")

    return rag_chain