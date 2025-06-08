"""
LLM Client Factory
This module reads environment variables to determine which LLM provider
to use and returns a unified client for interacting with it.
"""

import os
import inspect
import httpx
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from a .env file
load_dotenv()

# --- REVISED DEBUGGING WRAPPER ---
def create_openai_client_safely(**kwargs):
    """
    A wrapper to correctly initialize the OpenAI client for custom endpoints
    like LM Studio, avoiding ADK's argument injection.
    """
    print(f"[DEBUG] create_openai_client_safely: Attempting to create OpenAI client with args: {kwargs}")
    try:
        # Create a base httpx client. It won't have the base_url.
        # This is where you would configure proxies, certs, etc. if needed.
        http_client = httpx.Client()
        
        # --- KEY CHANGE: The base_url MUST be passed to the OpenAI constructor. ---
        # It uses this to know where to send requests. The http_client is for transport.
        client = OpenAI(
            base_url=kwargs.get("base_url"),
            api_key=kwargs.get("api_key", "not-needed"),
            http_client=http_client
        )
        print(f"[DEBUG] create_openai_client_safely: OpenAI client created. Target base_url: {client.base_url}")
        return client
    except TypeError as e:
        print(f"\n[FATAL] create_openai_client_safely: Caught TypeError during OpenAI client initialization!")
        print(f"[FATAL] create_openai_client_safely: The calling function tried to pass these arguments: {kwargs}")
        print(f"[FATAL] create_openai_client_safely: The error was: {e}\n")
        raise e

class UnifiedLLMClient:
    """A wrapper to provide a consistent .generate() method for different LLMs."""
    # ... (no changes in this class) ...
    def __init__(self, client, provider):
        self._client = client
        self._provider = provider

    def generate(self, prompt, model=None):
        """Generates a response from the LLM using a unified interface."""
        print(f"\n[DEBUG] UnifiedLLMClient: Generating response from '{self._provider}'.")
        if self._provider == "google":
            model_instance = self._client
            return model_instance.generate_content(prompt).text
        
        elif self._provider in ["lm_studio", "openai", "ollama"]:
            print(f"[DEBUG] UnifiedLLMClient: Sending request to OpenAI-compatible endpoint at {self._client.base_url}")
            chat_completion = self._client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="local-model",
                temperature=0.7,
            )
            response_content = chat_completion.choices[0].message.content
            print(f"[DEBUG] UnifiedLLMClient: Received content: '{response_content[:70]}...'")
            return response_content
        
        else:
            raise ValueError(f"Unknown LLM provider: {self._provider}")

def get_llm_client():
    """
    Reads the environment and returns the appropriate unified LLM client.
    """
    provider = os.getenv("LLM_PROVIDER")
    
    if not provider:
        raise ValueError("LLM_PROVIDER environment variable not set.")

    print(f"[DEBUG] get_llm_client: Found LLM_PROVIDER: '{provider}'")

    if provider == "google":
        # ... (no changes here) ...
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set for the 'google' provider.")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        return UnifiedLLMClient(client=model, provider="google")

    elif provider == "lm_studio":
        base_url = os.getenv("LM_STUDIO_BASE_URL")
        if not base_url:
            raise ValueError("LM_STUDIO_BASE_URL is not set for the 'lm_studio' provider.")
        
        print(f"[DEBUG] get_llm_client: Preparing to create OpenAI client for LM Studio.")
        
        # Use our revised safe wrapper function
        client = create_openai_client_safely(base_url=base_url, api_key="not-needed")
        return UnifiedLLMClient(client=client, provider="lm_studio")

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")