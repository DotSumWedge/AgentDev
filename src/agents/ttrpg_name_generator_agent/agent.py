# src/agents/ttrpg_name_generator_agent/agent.py

import re
import time
import uuid
from typing import Optional, AsyncIterator
from pydantic import PrivateAttr
from google.adk.agents import BaseAgent

# --- Final Approach: Use the official ADK Event and Content types ---
from google.adk.events import Event
from google.genai import types as genai_types

from src.llm_client import get_llm_client, UnifiedLLMClient


class TTRPGNameGeneratorAgent(BaseAgent):
    _llm_client: Optional[UnifiedLLMClient] = PrivateAttr(default=None)
    _initialized: bool = PrivateAttr(default=False)

    def __init__(self, **kwargs):
        super().__init__(name="ttrpg_name_generator_agent_local", **kwargs)

    def get_client(self) -> Optional[UnifiedLLMClient]:
        if not self._initialized:
            print("\n[DEBUG] TTRPGNameGeneratorAgent: Triggering lazy initialization...")
            try:
                self._llm_client = get_llm_client()
                print("[DEBUG] ...LLM client created successfully.")
            except Exception as e:
                print(f"[ERROR] ...Failed to create LLM client: {repr(e)}")
                self._llm_client = None
            finally:
                self._initialized = True
        return self._llm_client

    def _clean_response(self, text: str) -> str:
        cleaned_text = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
        return cleaned_text.strip()

    async def _run_async_impl(self, ctx) -> AsyncIterator[Event]:
        print("\n[INFO] TTRPGNameGeneratorAgent: Agent run started.")
        llm_client = self.get_client()
        current_invocation_id = ctx.invocation_id
        print(f"[INFO] TTRPGNameGeneratorAgent: Captured invocation_id: '{current_invocation_id}'")

        def create_event(text: str, author: str, invocation_id: str) -> Event:
            # Create the part, content, and then the final Event object
            # This matches the schema shown in the official ADK documentation curl examples
            part = genai_types.Part(text=text)
            content = genai_types.Content(parts=[part], role="model")
            
            # The key change: We construct an Event with top-level 'content'
            return Event(
                content=content,
                author=author,
                invocation_id=invocation_id
            )

        if not llm_client:
            yield create_event("Agent not initialized. Could not create LLM client.", self.name, current_invocation_id)
            return

        query = ctx.user_content.parts[0].text if ctx.user_content and hasattr(ctx.user_content, 'parts') and ctx.user_content.parts else ""
        print(f"[INFO] TTRPGNameGeneratorAgent: Received query: '{query}'")

        if not query:
            yield create_event("Could not extract a valid query from the request.", self.name, current_invocation_id)
            return

        system_prompt = "You are a creative assistant for a TTRPG Game Master. Your task is to generate a name for a character, town, river, or any other thing that can be named based on the user's request. Respond concisely with only the generated name."
        full_prompt = f"{system_prompt}\n\nUser Request: {query}"

        try:
            raw_response_text = llm_client.generate(full_prompt)
            final_response_text = self._clean_response(raw_response_text)
            print(f"[INFO] TTRPGNameGeneratorAgent: Generated response: '{final_response_text}'")
            
            response_event = create_event(final_response_text, self.name, current_invocation_id)

            # VERIFICATION LOG: Print the JSON, excluding None values to match the clean curl output
            print("\n--- BEGIN YIELDED OBJECT ---")
            print(response_event.model_dump_json(indent=2, exclude_none=True))
            print("--- END YIELDED OBJECT ---\n")
            
            yield response_event
            print("[INFO] TTRPGNameGeneratorAgent: Successfully yielded response to ADK runner.")

        except Exception as e:
            error_message = f"An error occurred during LLM generation: {repr(e)}"
            print(f"[ERROR] TTRPGNameGeneratorAgent: {error_message}")
            yield create_event(error_message, self.name, current_invocation_id)

root_agent = TTRPGNameGeneratorAgent()