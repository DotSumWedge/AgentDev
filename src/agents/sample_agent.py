"""
Sample agent that uses the LLM Client Factory to work with any
configured LLM provider (Google, LM Studio, etc.).
"""

from src.llm_client import get_llm_client

class SampleAgent:
    """A flexible agent that uses the configured LLM client."""
    
    def __init__(self):
        print("Initializing SampleAgent...")
        try:
            # The magic happens here!
            self.llm_client = get_llm_client()
            self.name = "SampleAgent"
            print(f"✅ Agent '{self.name}' initialized successfully.")
        except Exception as e:
            self.llm_client = None
            print(f"❌ Failed to initialize agent: {e}")

    def ask(self, question):
        if not self.llm_client:
            return "Agent not initialized. Please check your .env configuration and logs."
        
        print(f"\nAsking question: '{question}'")
        try:
            # The client has a unified .generate() method
            response = self.llm_client.generate(question)
            return response
        except Exception as e:
            return f"An error occurred while communicating with the LLM: {e}"

if __name__ == "__main__":
    agent = SampleAgent()
    if agent.llm_client:
        prompt = "In one short sentence, explain why local LLMs are useful for developers."
        answer = agent.ask(prompt)
        print("\nModel Response:")
        print("-----------------")
        print(answer)
        print("-----------------")