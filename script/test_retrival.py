import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.rag.retriever import get_medical_retriever

def main():
    retriever = get_medical_retriever()

    query = "What are the symptoms of diabetes?"
    print(f"\n🔍 Query: {query}\n")

    results = retriever.get_relevant_documents(query)

    for i, doc in enumerate(results, start=1):
        print(f"--- Result {i} ---")
        print(doc.page_content[:500])
        print()

if __name__ == "__main__":
    main()
