# src/agents/ttrpg_agent/agent.py

import re
import time
import uuid
from typing import Optional, AsyncIterator, Dict, Any
from pydantic import PrivateAttr, Field, BaseModel
from google.adk.agents import BaseAgent
import google.genai.types as genai_types
from src.llm_client import get_llm_client, UnifiedLLMClient

# --- FINALIZED Pydantic Models ---

class Actions(BaseModel):
    state_delta: Dict[str, Any] = Field(default_factory=dict)

class PatchedGenerateContentResponse(genai_types.GenerateContentResponse):
    """
    A fully patched version of GenerateContentResponse that includes all fields
    required by the ADK runner and UI for a complete event object.
    """
    id: str = Field(default_factory=lambda: f"event-{uuid.uuid4()}")
    # --- KEY CHANGE: Author is no longer hardcoded. It will be set dynamically. ---
    author: str 
    partial: bool = Field(default=False)
    actions: Actions = Field(default_factory=Actions)
    timestamp: float = Field(default_factory=time.time)


class TTRPGNameGeneratorAgent(BaseAgent):
    _llm_client: Optional[UnifiedLLMClient] = PrivateAttr(default=None)
    _initialized: bool = PrivateAttr(default=False)

    def __init__(self, **kwargs):
        super().__init__(name="ttrpg_name_generator_agent_local", **kwargs)

    # ... (no changes to get_client or _clean_response) ...
    def get_client(self) -> Optional[UnifiedLLMClient]:
        if not self._initialized:
            print("\n[DEBUG] TTRPGNameGeneratorAgent: Triggering lazy initialization of LLM client...")
            try:
                self._llm_client = get_llm_client()
                print("[DEBUG] TTRPGNameGeneratorAgent: LLM client created successfully.")
            except Exception as e:
                print(f"[ERROR] TTRPGNameGeneratorAgent: Failed to create LLM client: {repr(e)}")
                self._llm_client = None
            finally:
                self._initialized = True
        return self._llm_client

    def _clean_response(self, text: str) -> str:
        cleaned_text = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
        return cleaned_text.strip()

    async def _run_async_impl(self, ctx) -> AsyncIterator:
        print("\n[INFO] TTRPGNameGeneratorAgent: Agent run started.")
        llm_client = self.get_client()

        # --- KEY CHANGE: Helper now takes the author's name ---
        def create_response(text: str, author: str):
            response_part = genai_types.Part(text=text)
            response_content = genai_types.Content(parts=[response_part], role="model")
            response_candidate = genai_types.Candidate(content=response_content)
            return PatchedGenerateContentResponse(
                candidates=[response_candidate],
                author=author # Set the author dynamically
            )

        if not llm_client:
            # Use self.name, which is available from BaseAgent
            yield create_response("Agent not initialized. Could not create LLM client.", self.name)
            return

        query = ctx.user_content.parts[0].text if ctx.user_content and hasattr(ctx.user_content, 'parts') and ctx.user_content.parts else ""
        print(f"[INFO] TTRPGNameGeneratorAgent: Received query: '{query}'")

        if not query:
            yield create_response("Could not extract a valid query from the request.", self.name)
            return

        system_prompt = "You are a creative assistant for a TTRPG Game Master. Your task is to generate a name for a character based on the user's request. Respond concisely with only the generated name."
        full_prompt = f"{system_prompt}\n\nUser Request: {query}"

        try:
            raw_response_text = llm_client.generate(full_prompt)
            final_response_text = self._clean_response(raw_response_text)
            print(f"[INFO] TTRPGNameGeneratorAgent: Generated response: '{final_response_text}'")
            
            # --- KEY CHANGE: Create the response using our helper and self.name ---
            response_obj = create_response(final_response_text, self.name)

            print(f"[DEBUG] Verifying raw object data: id='{response_obj.id}', author='{response_obj.author}'")
            print(f"[DEBUG] Final object to yield (JSON):\n{response_obj.model_dump_json(indent=2)}")
            
            yield response_obj
            print("[INFO] TTRPGNameGeneratorAgent: Successfully yielded response to ADK runner.")

        except Exception as e:
            error_message = f"An error occurred during LLM generation: {repr(e)}"
            print(f"[ERROR] TTRPGNameGeneratorAgent: {error_message}")
            yield create_response(error_message, self.name)


root_agent = TTRPGNameGeneratorAgent()