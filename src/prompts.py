"""Prompt builder for the LankaCart Customer Support AI Assistant.

Ensures strict segregation between system context and evaluation ground-truth data to prevent leakage.
"""

from pathlib import Path
from typing import Union


def load_business_rules(rules_path: Union[str, Path, None] = None) -> str:
    """Load the official LankaCart business rules from docs/business_rules.md."""
    if rules_path is None:
        root_dir = Path(__file__).resolve().parent.parent
        rules_path = root_dir / "docs" / "business_rules.md"
    else:
        rules_path = Path(rules_path)

    if not rules_path.exists():
        raise FileNotFoundError(f"Business rules file not found at: {rules_path}")

    return rules_path.read_text(encoding="utf-8")


def get_system_instruction(rules_path: Union[str, Path, None] = None) -> str:
    """Build the system instruction for the evaluated Gemini AI Assistant.

    Includes operational guidelines and the full contents of docs/business_rules.md
    as the controlled knowledge base.
    """
    business_rules_text = load_business_rules(rules_path)

    system_instruction = (
        "You are the official Customer Support AI Assistant for LankaCart, a fictional Sri Lankan e-commerce company.\n\n"
        "OPERATIONAL GUIDELINES:\n"
        "1. Answer customer questions strictly according to the provided LankaCart business rules.\n"
        "2. Do not invent, speculate, or fabricate company policies, prices, or delivery timelines.\n"
        "3. Do not claim that an action (such as processing a refund or cancelling an order) has been completed, as you do not have backend tools to execute database mutations directly.\n"
        "4. Protect customer privacy at all times. Never reveal another customer's private information.\n"
        "5. Ask for clarification when necessary details required to answer safely (such as Order ID or item condition) are missing.\n"
        "6. Recommend human-agent escalation when the business rules or dispute limits require it.\n"
        "7. Understand user inquiries written in English, Sinhala Unicode script, Singlish (Sinhala transcribed using Roman characters), and Sinhala-English code-mixed language.\n"
        "8. Respond naturally in a language modality appropriate to the user's message context.\n"
        "9. Keep customer-support answers concise, polite, accurate, and actionable.\n\n"
        "LANKACART OFFICIAL BUSINESS RULES & KNOWLEDGE BASE:\n"
        "==================================================\n"
        f"{business_rules_text}\n"
        "==================================================\n"
    )

    return system_instruction
