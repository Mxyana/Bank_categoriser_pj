import os
import json
from groq import Groq
from dotenv import load_dotenv

print("SCRIPT STARTED - GROQ EDITION")

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print("API KEY FOUND:", api_key is not None)

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found in .env file.\n"
        "Create a .env file and add:\n"
        "GROQ_API_KEY=your_api_key_here"
    )

# =========================
# INITIALIZE CLIENT
# =========================
try:
    client = Groq(api_key=api_key)
    print("Groq client initialized successfully.")
except Exception as e:
    print("Failed to initialize Groq client:", e)
    raise

# =========================
# MAIN FUNCTION
# =========================
def generate_financial_advice(ai_safe_payload):

    # Using Meta's Llama 3.3 70B - Highly capable for financial logic and strict JSON
    model_name = "llama-3.3-70b-versatile"

    system_prompt = """
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

    full_payload = f"""
{system_prompt}

INPUT DATA:
{json.dumps(ai_safe_payload, indent=2)}
"""

    print("Firing payload to the Groq Advice Engine...")

    try:
        # The Groq syntax is nearly identical to OpenAI's
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": full_payload,
                }
            ],
            model=model_name,
            temperature=0.1,
            # This explicitly forces Groq to return ONLY your JSON schema
            response_format={"type": "json_object"},
        )

        print("Raw Groq Response Received")

        # Extract the text string from the chat completion object
        response_content = chat_completion.choices[0].message.content

        if not response_content:
            print("Groq returned an empty response.")
            return None

        print("Parsing JSON response...")

        result_dict = json.loads(response_content)

        print("Successfully generated financial insights.")

        return result_dict

    except json.JSONDecodeError as e:
        print(f"Failed to parse AI response into JSON: {e}")

        try:
            print("Raw AI Output:")
            print(response_content)
        except:
            print("Could not print raw response.")

        return None

    except Exception as e:
        print(f"API Connection Error: {e}")
        return None


