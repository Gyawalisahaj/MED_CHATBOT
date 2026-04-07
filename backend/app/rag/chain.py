# Simple RAG chain implementation that bypasses LangChain compatibility issues
import requests
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("rag_chain")

def get_rag_chain():
    """
    Returns a simple RAG chain function that directly calls Groq API.
    This bypasses LangChain's pydantic compatibility issues.
    """
    def rag_chain(query: str, context_docs: list = None) -> str:
        """
        Simple RAG implementation:
        1. Format context from retrieved documents
        2. Call Groq API directly
        3. Return response
        """
        try:
            # Format context
            context = ""
            if context_docs:
                context = "\n\n".join([doc.page_content for doc in context_docs[:3]])  # Limit to 3 docs
                context = f"Context from medical documents:\n{context}\n\n"

            # Create prompt
            prompt = f"""You are a medical AI assistant. Answer the following question based on the provided context.

{context}Question: {query}

Please provide a helpful, accurate answer based on medical knowledge. If the context is insufficient, use your general medical knowledge but note that."""

            # Call Groq API directly
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": settings.TEMPERATURE,
                    "max_tokens": 1000
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                logger.info(f"RAG chain completed successfully for query: {query[:50]}...")
                return answer
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return f"Error: Unable to get response from AI service (Status: {response.status_code})"

        except Exception as e:
            logger.error(f"RAG chain error: {str(e)}")
            return f"Error: {str(e)}"

    return rag_chain