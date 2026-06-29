import os
import json
from functools import lru_cache

from groq import Groq
from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def _get_client():
    """Lazy Groq client. Validates the API key only when actually needed,
    so importing this module never crashes."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not found. Add it to your .env file: "
            "GROQ_API_KEY=your_api_key_here"
        )
    return Groq(api_key=api_key)


SYSTEM_PROMPT = """
ROLE:
You are an expert financial analyst and data structuring engine operating in the Nigerian fintech ecosystem.

TASK:
1. Map every transaction to EXACTLY ONE of the "Allowed Categories".
2. Analyze the user's spending habits, identify financial leaks, and provide a short actionable piece of advice.

CONSTRAINTS:
- Output ONLY as a valid JSON object.
- DO NOT include markdown formatting like ```json.
- DO NOT include conversational text.

ALLOWED CATEGORIES:
- Inward Transfers
- Salary / Business Income
- Reversals & Refunds
- Web3 / Crypto P2P
- Airtime & Data
- Outward Transfers
- POS & Cash Withdrawals
- Bank Charges & Taxes
- Utilities & Bills
- Entertainment & Subscriptions
- Food & Groceries
- Transportation
- Miscellaneous / Uncategorized

OUTPUT SCHEMA:
{
  "categorized_transactions": [
    {
      "date": "",
      "description": "",
      "amount": 0.0,
      "transaction_type": "",
      "category": ""
    }
  ],
  "financial_summary": {
    "total_credits": 0.0,
    "total_debits": 0.0
  },
  "advice_engine": {
    "identified_pattern": "",
    "actionable_advice": ""
  }
}
"""


def generate_financial_advice(ai_safe_payload):
    model_name = "llama-3.3-70b-versatile"

    user_content = (
        f"{SYSTEM_PROMPT}\n\nINPUT DATA:\n"
        f"{json.dumps(ai_safe_payload, indent=2)}"
    )

    response_content = None
    try:
        client = _get_client()
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": user_content}],
            model=model_name,
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        response_content = chat_completion.choices[0].message.content
        if not response_content:
            print("Groq returned an empty response.")
            return None

        return json.loads(response_content)

    except json.JSONDecodeError as e:
        print(f"Failed to parse AI response into JSON: {e}")
        if response_content is not None:
            print("Raw AI Output:")
            print(response_content)
        return None

    except Exception as e:
        print(f"API Connection Error: {e}")
        return None
