from openai import OpenAI
import httpx
from typing import List, Dict
import os

class Chatbot:
    def __init__(self, model_name="gpt-4", temperature=0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.conversation_history = []
        
        # Configure custom HTTP client
        http_client = httpx.Client()
        
        # Initialize OpenAI client with custom HTTP client
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            http_client=http_client
        )

    def create_system_prompt(self, context_chunks: List[Dict]) -> str:
        """Create system prompt with context from retrieved chunks."""
        context = "\n\n".join([
            f"Content from {chunk['metadata']['url']}:\n{chunk['chunk']}"
            for chunk in context_chunks
        ])
        
        return f"""You are a helpful AI assistant for InWeb Info company. 
        Use the following context to answer questions about the company and its services.
        If you don't find the answer in the context, say so politely.
        
        Context:
        {context}
        """

    def get_response(self, query: str, context_chunks: List[Dict]) -> str:
        """Generate a response using the OpenAI API."""
        try:
            # Create messages array
            messages = [
                {"role": "system", "content": self.create_system_prompt(context_chunks)},
                *self.conversation_history,
                {"role": "user", "content": query}
            ]

            # Get completion from OpenAI
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=1000
            )

            # Extract response
            assistant_response = response.choices[0].message.content

            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": query},
                {"role": "assistant", "content": assistant_response}
            ])

            return assistant_response

        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = [] 