"""Unit tests for GeminiClient wrapper using unittest.mock."""

import unittest
from unittest.mock import MagicMock, patch

from src.llm_client import GeminiClient
from src.models import LLMResponse


class TestGeminiClient(unittest.TestCase):
    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key_raises_error(self):
        """Verify missing GEMINI_API_KEY raises a clear ValueError."""
        with self.assertRaises(ValueError) as ctx:
            GeminiClient(api_key="", model_name="gemini-3.1-flash-lite")
        self.assertIn("GEMINI_API_KEY is missing", str(ctx.exception))

    @patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}, clear=True)
    def test_missing_model_name_raises_error(self):
        """Verify missing GEMINI_MODEL raises a clear ValueError."""
        with self.assertRaises(ValueError) as ctx:
            GeminiClient(api_key="fake_key", model_name="")
        self.assertIn("GEMINI_MODEL is missing", str(ctx.exception))

    @patch("src.llm_client.genai.Client")
    @patch.dict(
        "os.environ",
        {"GEMINI_API_KEY": "test_key", "GEMINI_MODEL": "gemini-3.1-flash-lite"},
        clear=True,
    )
    def test_successful_response_generation(self, mock_client_cls):
        """Verify successful Gemini API response builds a valid LLMResponse object."""
        mock_genai_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Delivery to Colombo costs LKR 350."
        mock_genai_instance.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_genai_instance

        client = GeminiClient(system_instruction="Test Instruction")
        res = client.generate_response("TC001", "What is delivery fee for Colombo?")

        self.assertIsInstance(res, LLMResponse)
        self.assertEqual(res.test_id, "TC001")
        self.assertEqual(res.model_name, "gemini-3.1-flash-lite")
        self.assertEqual(res.response_text, "Delivery to Colombo costs LKR 350.")
        self.assertTrue(res.success)
        self.assertEqual(res.error_message, "")
        self.assertGreaterEqual(res.latency_seconds, 0.0)

    @patch("src.llm_client.genai.Client")
    @patch.dict(
        "os.environ",
        {"GEMINI_API_KEY": "test_key", "GEMINI_MODEL": "gemini-3.1-flash-lite"},
        clear=True,
    )
    def test_api_exception_handling(self, mock_client_cls):
        """Verify API exceptions are caught and returned as failed LLMResponse without crashing."""
        mock_genai_instance = MagicMock()
        mock_genai_instance.models.generate_content.side_effect = Exception("API rate limit exceeded")
        mock_client_cls.return_value = mock_genai_instance

        client = GeminiClient(system_instruction="Test Instruction")
        res = client.generate_response("TC001", "Hello")

        self.assertIsInstance(res, LLMResponse)
        self.assertEqual(res.test_id, "TC001")
        self.assertFalse(res.success)
        self.assertEqual(res.response_text, "")
        self.assertIn("API rate limit exceeded", res.error_message)
        self.assertGreaterEqual(res.latency_seconds, 0.0)


if __name__ == "__main__":
    unittest.main()
