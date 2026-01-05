from typing import List, Protocol
from app.backend.core.config import settings
import openai
from langchain_google_genai import ChatGoogleGenerativeAI

class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...

class OpenAILLMClient:
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful manufacturing assistant. Answer strictly based on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

class GeminiLLMClient:
    def __init__(self, api_key: str = settings.GOOGLE_API_KEY, model: str = settings.LLM_MODEL):
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.0,
            convert_system_message_to_human=True # Sometimes needed for older chains, but fine here
        )

    def generate(self, prompt: str) -> str:
        try:
            # Gemini models often handle system context differently, but LangChain abstracts it well.
            # We'll just pass the prompt.
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

class MockLLMClient:
    """For testing without API keys."""
    def generate(self, prompt: str) -> str:
        return "This is a mock response strictly based on the provided context. (Mock Mode)"

def get_llm_client() -> LLMClient:
    """Factory to get the appropriate LLM client."""
    if hasattr(settings, "GOOGLE_API_KEY") and settings.GOOGLE_API_KEY and "AIza" in settings.GOOGLE_API_KEY:
        return GeminiLLMClient()
    
    # Fallback to OpenAI if configured (though we removed it from config, keeping code for safety)
    if hasattr(settings, "OPENAI_API_KEY") and settings.OPENAI_API_KEY:
         base_url = getattr(settings, "OPENAI_BASE_URL", None)
         return OpenAILLMClient(api_key=settings.OPENAI_API_KEY, base_url=base_url, model=settings.LLM_MODEL)
         
    return MockLLMClient()
