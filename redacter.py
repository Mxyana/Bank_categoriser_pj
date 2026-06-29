import copy


def prepare_for_ai(clean_json):
    """
    Return a deep copy of the normalised statement with PII removed so it can
    be safely sent to a third-party LLM. A shallow copy is NOT safe here —
    nested dicts would still alias the original and leak PII.
    """
    ai_payload = copy.deepcopy(clean_json)

    account_info = ai_payload.get("account_info")
    if isinstance(account_info, dict):
        if "account_name" in account_info:
            account_info["account_name"] = "REDACTED"
        if "account_number" in account_info:
            account_info["account_number"] = "REDACTED"

    return ai_payload
