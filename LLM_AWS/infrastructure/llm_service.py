"""
Infrastructure - LLM Service Implementation (Gemini)
"""
import google.generativeai as genai

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from LLM_AWS.domain.repositories import ILLMService


class GeminiLLMService(ILLMService):
    def __init__(self, gemini_key: str, model_name: str = "gemini-3-flash-preview"):
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel(model_name)
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response từ Gemini"""
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"LLM generation error: {e}")
            return f"Xin lỗi, tôi gặp lỗi khi xử lý: {str(e)}"
