def prepare_for_ai(clean_json):
    # Create a copy so we don't mess up the original data needed for the UI
    ai_payload = clean_json.copy()
    
    # Redact the sensitive fields
    ai_payload["account_info"]["account_name"] = "REDACTED"
    ai_payload["account_info"]["account_number"] = "REDACTED"
    
    return ai_payload