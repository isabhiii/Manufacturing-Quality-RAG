from typing import List, Any
from app.backend.rag.retriever import Retriever
from app.backend.rag.generator import get_llm_client, LLMClient
from langchain_core.documents import Document

class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()
        self.llm: LLMClient = get_llm_client()

    def build_prompt(self, query: str, context_chunks: List[Any]) -> str:
        context_text = ""
        for i, (doc, score) in enumerate(context_chunks):
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "Unknown")
            content = doc.page_content.replace("\n", " ")
            context_text += f"[{i+1}] Source: {source}, Page: {page}\nContent: {content}\n\n"

        prompt = f"""
You are a Manufacturing Quality Assistant. Use the following context documents to answer the user's question.
If the answer is not found in the documents, state that you do not know based on the provided context.
Cite the documents by their source name and page number when answering.

Context:
{context_text}

Question: {query}

Answer:
"""
        return prompt

    def run(self, query: str):
        # 1. Retrieve
        retrieved_docs = self.retriever.retrieve(query)
        
        # 2. Build Prompt
        prompt = self.build_prompt(query, retrieved_docs)
        
        # 3. Generate
        answer = self.llm.generate(prompt)
        
        return {
            "answer": answer,
            "citations": retrieved_docs, # List[Tuple[Document, float]]
            "raw_prompt": prompt
        }
