import json
import os


def get_value(field):
    """Safely extract 'value' from a Mindee field (None / list / wrong-type safe)."""
    if isinstance(field, dict):
        return field.get("value")
    return None


def _safe_dict(value):
    """Return value if it's a dict, else {}. Protects against explicit None values."""
    return value if isinstance(value, dict) else {}


def _safe_list(value):
    """Return value if it's a list, else []."""
    return value if isinstance(value, list) else []


def normalize_statement_data(json_filepath):
    if not os.path.exists(json_filepath):
        raise FileNotFoundError(f"File not found: {json_filepath}")

    with open(json_filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle nested JSON string
    if isinstance(data, str):
        data = json.loads(data)

    # Navigate Mindee structure defensively — every level may be None
    fields = _safe_dict(
        _safe_dict(_safe_dict(data).get("inference")).get("result")
    ).get("fields")
    fields = _safe_dict(fields)

    # Account holder name
    account_names = _safe_list(
        _safe_dict(fields.get("account_holder_names")).get("items")
    )
    if account_names and isinstance(account_names[0], dict):
        primary_name = account_names[0].get("value", "Unknown")
    else:
        primary_name = "Unknown"

    clean_metadata = {
        "bank_name": get_value(fields.get("bank_name")),
        "account_name": primary_name,
        "account_number": get_value(fields.get("account_number")),
        "start_date": get_value(fields.get("statement_period_start_date")),
        "end_date": get_value(fields.get("statement_period_end_date")),
        "beginning_balance": get_value(fields.get("beginning_balance")),
        "ending_balance": get_value(fields.get("ending_balance")),
    }

    # Transactions
    raw_transactions = _safe_list(
        _safe_dict(fields.get("list_of_transactions")).get("items")
    )

    clean_transactions = []
    for txn in raw_transactions:
        if not isinstance(txn, dict):
            continue

        txn_fields = _safe_dict(txn.get("fields"))

        raw_amount = get_value(txn_fields.get("amount"))
        txn_type = None
        clean_amount = None

        if raw_amount is not None:
            try:
                amt = float(raw_amount)
                txn_type = "CREDIT" if amt > 0 else "DEBIT"
                clean_amount = abs(amt)
            except (ValueError, TypeError):
                pass

        clean_transactions.append({
            "date": get_value(txn_fields.get("date")),
            "description": get_value(txn_fields.get("description")),
            "amount": clean_amount,
            "balance": get_value(txn_fields.get("balance")),
            "transaction_type": txn_type,
        })

    normalized_output = {
        "account_info": clean_metadata,
        "transaction_count": len(clean_transactions),
        "transactions": clean_transactions,
    }

    save_path = json_filepath.replace(".json", "_CLEAN.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(normalized_output, f, indent=4)

    print("\nSuccessfully normalized!")
    print(f"Clean data saved to: {save_path}")
    print(f"Transactions extracted: {len(clean_transactions)}")

    return normalized_output


if __name__ == "__main__":
    clean_data = normalize_statement_data(
        "data/raw_json/831658760-New-Bank-Statement.json"
    )
    print("\nSample Output:")
    print(json.dumps(clean_data, indent=2))
