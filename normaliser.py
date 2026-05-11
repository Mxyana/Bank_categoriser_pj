import json
import os


def get_value(field):
    """
    Safely extract the 'value' from a Mindee field.
    Prevents crashes if field is None, list, or malformed.
    """
    if isinstance(field, dict):
        return field.get("value")
    return None


def normalize_statement_data(json_filepath):

    # =========================
    # VALIDATE FILE
    # =========================

    if not os.path.exists(json_filepath):
        raise FileNotFoundError(f"File not found: {json_filepath}")

    # =========================
    # LOAD JSON
    # =========================

    with open(json_filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle nested JSON string
    if isinstance(data, str):
        data = json.loads(data)

    # =========================
    # NAVIGATE MINDEE STRUCTURE
    # =========================

    fields = (
        data.get("inference", {})
            .get("result", {})
            .get("fields", {})
    )

    # =========================
    # ACCOUNT HOLDER NAME
    # =========================

    account_names = (
        fields.get("account_holder_names", {})
              .get("items", [])
    )

    if (
        isinstance(account_names, list)
        and len(account_names) > 0
        and isinstance(account_names[0], dict)
    ):
        primary_name = account_names[0].get("value", "Unknown")
    else:
        primary_name = "Unknown"

    # =========================
    # CLEAN ACCOUNT METADATA
    # =========================

    clean_metadata = {
        "bank_name": get_value(fields.get("bank_name")),
        "account_name": primary_name,
        "account_number": get_value(fields.get("account_number")),
        "start_date": get_value(fields.get("statement_period_start_date")),
        "end_date": get_value(fields.get("statement_period_end_date")),
        "beginning_balance": get_value(fields.get("beginning_balance")),
        "ending_balance": get_value(fields.get("ending_balance"))
    }

    # =========================
    # TRANSACTIONS
    # =========================

    raw_transactions = (
        fields.get("list_of_transactions", {})
              .get("items", [])
    )

    clean_transactions = []

    for txn in raw_transactions:

        if not isinstance(txn, dict):
            continue

        txn_fields = txn.get("fields", {})

        if not isinstance(txn_fields, dict):
            continue

        # =========================
        # AMOUNT + TRANSACTION TYPE
        # =========================

        raw_amount = get_value(txn_fields.get("amount"))

        if raw_amount is not None:

            try:
                raw_amount = float(raw_amount)

                txn_type = (
                    "CREDIT"
                    if raw_amount > 0
                    else "DEBIT"
                )

                clean_amount = abs(raw_amount)

            except (ValueError, TypeError):

                txn_type = None
                clean_amount = None

        else:
            txn_type = None
            clean_amount = None

        # =========================
        # CLEAN TRANSACTION
        # =========================

        clean_txn = {
            "date": get_value(txn_fields.get("date")),
            "description": get_value(txn_fields.get("description")),
            "amount": clean_amount,
            "balance": get_value(txn_fields.get("balance")),
            "transaction_type": txn_type
        }

        clean_transactions.append(clean_txn)

    # =========================
    # FINAL OUTPUT
    # =========================

    normalized_output = {
        "account_info": clean_metadata,
        "transaction_count": len(clean_transactions),
        "transactions": clean_transactions
    }

    # =========================
    # SAVE CLEAN FILE
    # =========================

    save_path = json_filepath.replace(".json", "_CLEAN.json")

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(normalized_output, f, indent=4)

    print("\nSuccessfully normalized!")
    print(f"Clean data saved to: {save_path}")
    print(f"Transactions extracted: {len(clean_transactions)}")

    return normalized_output


# =========================
# TEST
# =========================

if __name__ == "__main__":

    clean_data = normalize_statement_data(
        "data/raw_json/831658760-New-Bank-Statement.json"
    )

    print("\nSample Output:")
    print(json.dumps(clean_data, indent=2))