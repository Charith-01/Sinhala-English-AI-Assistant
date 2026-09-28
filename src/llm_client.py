"""Gemini LLM API client wrapper using the official google-genai SDK."""

import os
import time
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.models import LLMResponse
from src.prompts import get_system_instruction

# Load environment variables from .env if available
load_dotenv()


class GeminiClient:
    """Wrapper client for sending evaluation prompts to the Gemini API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        system_instruction: Optional[str] = None,
    ):
        """Initialize the Gemini client using configured environment variables.

        Raises:
            ValueError: If GEMINI_API_KEY or GEMINI_MODEL environment variable is missing.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL")

        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "GEMINI_API_KEY is missing. Please configure GEMINI_API_KEY in your .env file or environment."
            )

        if not self.model_name or not self.model_name.strip():
            raise ValueError(
                "GEMINI_MODEL is missing. Please configure GEMINI_MODEL in your .env file or environment."
            )

        self.system_instruction = system_instruction or get_system_instruction()
        self.client = genai.Client(api_key=self.api_key)

    def generate_response(self, test_id: str, user_input: str) -> LLMResponse:
        """Send user input to the Gemini model and return an LLMResponse.

        Args:
            test_id: Unique test identifier.
            user_input: Customer prompt string.

        Returns:
            LLMResponse object containing model output, status, and latency.
        """
        start_time = time.perf_counter()
        try:
            config = types.GenerateContentConfig(
                temperature=0.2,
                system_instruction=self.system_instruction,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_input,
                config=config,
            )

            latency = time.perf_counter() - start_time
            response_text = response.text if response and response.text else ""

            return LLMResponse(
                test_id=test_id,
                model_name=self.model_name,
                response_text=response_text,
                success=True,
                error_message="",
                latency_seconds=round(latency, 4),
            )

        except Exception as e:
            latency = time.perf_counter() - start_time
            return LLMResponse(
                test_id=test_id,
                model_name=self.model_name,
                response_text="",
                success=False,
                error_message=str(e),
                latency_seconds=round(latency, 4),
            )
