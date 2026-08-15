from google import genai
from google.genai import types
from app.core.config import settings
import logging
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import json

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. QA endpoint will fail.")
            self.client = None
        else:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
    async def generate_rag_answer(self, question: str, context_chunks: list[dict], history: list[dict] = None, system_prompt: str = None, temperature: float = None, db: AsyncSession = None, user_id: UUID = None) -> str:
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured. Please set it in your .env file.")
            
        if history is None:
            history = []
            
        # Format the context chunks
        context_text = ""
        for i, chunk in enumerate(context_chunks):
            context_text += f"\n--- Document {i+1} ---\n{chunk['snippet']}\n"
            
        system_instruction = system_prompt or (
            "You are an expert Enterprise AI Assistant. "
            "You have access to a semantic search database of the user's uploaded documents. "
            "When answering questions related to the user's data, base your answers strictly on the provided document excerpts. "
            "However, you may also engage in normal conversation, answer general knowledge questions, and refer back to your conversational history. "
            "Keep your answers concise, professional, and helpful."
        )
        
        prompt = f"Context excerpts:\n{context_text}\n\nUser Question: {question}"
        
        contents_array = []
        for msg in history:
            role = "model" if msg["role"] == "assistant" else "user"
            contents_array.append(
                types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
            )
            
        contents_array.append(
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        )
        
        # Define tool schemas for Gemini manually to prevent Automatic Function Calling
        tools = [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="get_current_time",
                        description="Returns the current date and time."
                    ),
                    types.FunctionDeclaration(
                        name="get_platform_stats",
                        description="Returns the total number of users and documents currently registered on the Enterprise AI platform. Useful for telemetry."
                    ),
                    types.FunctionDeclaration(
                        name="summarize_document",
                        description="Reads an entire document belonging to the user by its exact filename and returns its full content for you to summarize. Use this when the user explicitly asks to summarize a specific document.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "filename": types.Schema(type="STRING", description="The exact filename of the document to summarize.")
                            },
                            required=["filename"]
                        )
                    )
                ]
            )
        ]

        while True:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=contents_array,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=temperature if temperature is not None else 0.2,
                        tools=tools
                    )
                )
                
                if not response.function_calls:
                    return response.text
                
                # Append the model's function call block to history
                contents_array.append(response.candidates[0].content)
                
                function_responses = []
                for fc in response.function_calls:
                    logger.info(f"Executing tool: {fc.name} with args {fc.args}")
                    
                    result_data = "Function execution failed."
                    
                    if fc.name == "get_current_time":
                        result_data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                    elif fc.name == "get_platform_stats":
                        if db:
                            from app.models.user import User
                            from app.models.document import Document
                            u_count = await db.scalar(select(func.count()).select_from(User))
                            d_count = await db.scalar(select(func.count()).select_from(Document))
                            result_data = f"Platform has {u_count} users and {d_count} total documents."
                        else:
                            result_data = "Database session unavailable."
                            
                    elif fc.name == "summarize_document":
                        filename = fc.args.get("filename")
                        if db and user_id and filename:
                            from app.models.document import Document, DocumentChunk
                            stmt = select(Document).where(Document.uploaded_by == user_id, Document.filename.ilike(f"%{filename}%")).limit(1)
                            doc = await db.scalar(stmt)
                            if doc:
                                chunks = await db.scalars(select(DocumentChunk).where(DocumentChunk.document_id == doc.id))
                                full_text = "\n".join([c.content for c in chunks])
                                result_data = f"--- FULL DOCUMENT CONTENT FOR {filename} ---\n{full_text}"
                            else:
                                result_data = f"Document named '{filename}' not found in your uploads."
                        else:
                            result_data = "Missing required parameters to fetch document."
                            
                    function_responses.append(
                        types.Part.from_function_response(name=fc.name, response={"result": result_data})
                    )
                
                # Append function results back to the model
                contents_array.append(
                    types.Content(role="function", parts=function_responses)
                )

            except Exception as e:
                logger.error(f"Error generating answer from Gemini: {e}")
                raise
            
llm_service = LLMService()
