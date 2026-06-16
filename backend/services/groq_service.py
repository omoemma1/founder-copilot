# services/groq_service.py
import os
from dotenv import load_dotenv
from groq import Groq
from typing import Dict, Optional
import json

# Load .env file
load_dotenv()

class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("⚠️ GROQ_API_KEY not found. Get free key at: https://console.groq.com")
            self.enabled = False
            return
        try:
            self.client = Groq(api_key=self.api_key)
            self.enabled = True
            self.model = "llama-3.3-70b-versatile"
            print("✅ Groq AI loaded successfully!")
        except Exception as e:
            print(f"❌ Failed to initialize Groq: {e}")
            self.enabled = False

    async def chat(self, message: str, role: str = "architect", context: Dict = None):
        if not self.enabled:
            return "Groq AI is not configured. Please set GROQ_API_KEY in .env file."

        prompts = {
            "architect": "You are an Elite Software Architect. Provide detailed technical guidance.",
            "debug": "You are a Master Debugger. Find and fix problems quickly.",
            "founder": "You are a Strategic Business Advisor. Think about business impact.",
            "review": "You are a Senior Code Reviewer. Ensure code quality."
        }

        system_prompt = prompts.get(role, prompts["architect"])

        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.append({"role": "system", "content": f"Context: {json.dumps(context)}"})
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error from Groq: {str(e)}"

# Create global instance
groq = GroqService()