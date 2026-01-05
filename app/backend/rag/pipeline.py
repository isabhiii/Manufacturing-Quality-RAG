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

        prompt = f"""You are a Manufacturing Quality Assistant. Answer the user's question based ONLY on the provided context documents.

Rules:
- If the answer is not in the documents, say "I don't have information about this in the provided documents."
- DO NOT add citation numbers or references like [1], [2], or (Source: ...) in your answer.
- DO NOT use markdown formatting like asterisks (*) or bullet points. Write in plain prose.
- Write a clear, direct answer in flowing paragraphs.
- Be concise but thorough.

Context:
{context_text}

Question: {query}

Answer:"""
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
