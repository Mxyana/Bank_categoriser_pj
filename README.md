# Statement Insights

An AI-powered bank statement analysis API. Upload a PDF bank statement, and the service parses, normalizes, redacts PII, and returns categorized transactions with actionable financial advice.

Built around a FastAPI backend with two parsing engines (Standard and Premium), a Mindee-style data normalizer, a PII redactor, and a Groq-hosted LLM (`llama-3.3-70b-versatile`) as the advice engine. Includes a single-page dark-themed web frontend.

---

## Features

- **PDF upload endpoint** — accepts a bank statement PDF and an engine selector.
- **Dual parsing engines**
  - `standard` — default parser, always available.
  - `premium` — regex-based classifier (currently locked / under maintenance).
- **Data normalization** — flattens Mindee-style nested JSON into a clean schema with account metadata and transactions (date, description, amount, balance, CREDIT/DEBIT).
- **PII redaction** — strips `account_name` and `account_number` before the payload leaves the server for any third-party LLM.
- **AI categorization & advice** — every transaction is mapped to one of 13 allowed categories (Salary, Outward Transfers, POS & Cash Withdrawals, Bank Charges, etc.) and the LLM returns a JSON object with totals and a short actionable insight.
- **Frontend** — `index.html`, a Tailwind + Chart.js single-page UI for uploading statements and viewing insights.

---

## Project Structure

```
.
├── main.py              # FastAPI app + /upload route + static mount
├── normaliser.py        # Mindee JSON → clean schema
├── redacter.py          # Deep-copy + PII redaction for AI payload
├── advice_engine.py     # Groq LLM client + system prompt + JSON parsing
├── engines/
│   ├── standard.py      # process_standard(pdf_path)
│   └── premium.py       # process_premium(pdf_path)
├── index.html           # Frontend UI
├── uploads/             # Saved PDF uploads (auto-created)
└── data/raw_json/       # Raw parser JSON output
```

---

## Requirements

- Python 3.10+
- A Groq API key
- A Mindee account (model ID + API key) for the parsing engines

### Python dependencies

```bash
pip install fastapi uvicorn python-multipart groq python-dotenv mindee
```

---

## Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
MINDEE_API_KEY=your_mindee_api_key_here
MINDEE_MODEL_ID=your_mindee_model_id_here
```

You must obtain API keys from:
- **Groq** — https://console.groq.com
- **Mindee** — model ID and API key from your Mindee workspace

---

## Running

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000` to use the web UI, or POST directly to the API.

---

## API

### `POST /upload`

Multipart form fields:

| Field         | Type           | Description                         |
|---------------|----------------|-------------------------------------|
| `file`        | file (PDF)     | The bank statement PDF              |
| `engine_type` | string         | `standard` or `premium`             |

**Success response**

```json
{
  "status": "success",
  "engine": "standard",
  "account_info": {
    "bank_name": "...",
    "account_name": "...",
    "account_number": "...",
    "start_date": "...",
    "end_date": "...",
    "beginning_balance": 0.0,
    "ending_balance": 0.0
  },
  "transaction_count": 42,
  "insights": {
    "categorized_transactions": [ ... ],
    "financial_summary": {
      "total_credits": 0.0,
      "total_debits": 0.0
    },
    "advice_engine": {
      "identified_pattern": "...",
      "actionable_advice": "..."
    }
  }
}
```

**Error responses**

- `400` — non-PDF upload or invalid `engine_type`.
- `502` — parser engine reported an error.
- `500` — parser produced no JSON output.

The premium engine currently returns:

```json
{ "status": "locked", "message": "Premium PDF Regex Classifier is currently under maintenance." }
```

---

## Pipeline

```
PDF upload
   ↓
_safe_save()            # uuid-prefixed filename, path-traversal safe
   ↓
process_standard()      # Mindee parse → data/raw_json/<name>.json
   ↓
normalize_statement_data()   # clean schema + CREDIT/DEBIT inference
   ↓
prepare_for_ai()        # deep-copy + redact account_name / account_number
   ↓
generate_financial_advice()  # Groq llama-3.3-70b-versatile, JSON mode
   ↓
JSON response
```

---

## Categories used by the advice engine

Inward Transfers · Salary / Business Income · Reversals & Refunds · Web3 / Crypto P2P · Airtime & Data · Outward Transfers · POS & Cash Withdrawals · Bank Charges & Taxes · Utilities & Bills · Entertainment & Subscriptions · Food & Groceries · Transportation · Miscellaneous / Uncategorized

---

## Security Notes

- CORS is currently set to `allow_origins=["*"]` — tighten before production.
- Uploaded filenames are sanitized (`os.path.basename`) and prefixed with a UUID.
- PII (`account_name`, `account_number`) is removed via `prepare_for_ai` before any data is sent to Groq.
- Keep `.env` out of version control.

---

## License


