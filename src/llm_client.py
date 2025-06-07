"""
LLM Client Factory
This module reads environment variables to determine which LLM provider
to use and returns a unified client for interacting with it.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai

# Load environment variables from a .env file
load_dotenv()

class UnifiedLLMClient:
    """A wrapper to provide a consistent .generate() method for different LLMs."""

    def __init__(self, client, provider):
        self._client = client
        self._provider = provider

    def generate(self, prompt, model=None):
        """Generates a response from the LLM using a unified interface."""
        print(f"--- Sending request to {self._provider} ---")
        if self._provider == "google":
            # For Google, the model is part of the client
            model_instance = self._client
            return model_instance.generate_content(prompt).text
        
        elif self._provider in ["lm_studio", "openai", "ollama"]:
            # For OpenAI-compatible APIs
            # LM Studio doesn't use the 'model' parameter in the same way,
            # as the model is pre-loaded in the UI.
            chat_completion = self._client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="local-model", # This is often ignored by LM Studio but is required by the API
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content
        
        else:
            raise ValueError(f"Unknown LLM provider: {self._provider}")


def get_llm_client():
    """
    Reads the environment and returns the appropriate unified LLM client.
    """
    provider = os.getenv("LLM_PROVIDER")
    
    if not provider:
        raise ValueError("LLM_PROVIDER environment variable not set.")

    print(f"Found LLM_PROVIDER: '{provider}'")

    if provider == "google":
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
        # LM Studio doesn't require an API key
        client = OpenAI(base_url=base_url, api_key="not-needed")
        return UnifiedLLMClient(client=client, provider="lm_studio")

    # Add other providers like 'openai' or 'ollama' here in the future
    # elif provider == "openai":
    #     ...

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")