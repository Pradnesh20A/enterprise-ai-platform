from google import genai
from google.genai import types
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. QA endpoint will fail.")
            self.client = None
        else:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
    def generate_rag_answer(self, question: str, context_chunks: list[dict]) -> str:
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured. Please set it in your .env file.")
            
        # Format the context chunks
        context_text = ""
        for i, chunk in enumerate(context_chunks):
            context_text += f"\n--- Document {i+1} ---\n{chunk['snippet']}\n"
            
        system_instruction = (
            "You are an expert Enterprise AI Document Assistant. "
            "Your task is to answer the user's question based strictly on the provided document excerpts. "
            "If the answer cannot be found in the provided excerpts, politely state that you do not know. "
            "Do not hallucinate or use outside knowledge. Keep the answer concise and professional."
        )
        
        prompt = f"Context excerpts:\n{context_text}\n\nUser Question: {question}"
        
        try:
            response = self.client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating answer from Gemini: {e}")
            raise
            
llm_service = LLMService()
