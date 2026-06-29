import json
import os
from dotenv import load_dotenv
from mindee import ClientV2, InferenceParameters, PathInput, InferenceResponse

load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL_ID = os.getenv("MODEL_ID")


def process_standard(file_path):
    # Validate credentials up front — fail loudly with a useful message
    # instead of letting the SDK raise something opaque.
    if not API_KEY or not MODEL_ID:
        return {
            "error": (
                "Mindee credentials missing. Set API_KEY and MODEL_ID in your "
                ".env file."
            )
        }

    SAVE_DIR = os.path.join("data", "raw_json")
    os.makedirs(SAVE_DIR, exist_ok=True)

    mindee_client = ClientV2(api_key=API_KEY)
    params = InferenceParameters(model_id=MODEL_ID)
    input_source = PathInput(file_path)

    try:
        response = mindee_client.enqueue_and_get_result(
            InferenceResponse, input_source, params
        )

        base_name = os.path.basename(file_path)
        json_filename = os.path.splitext(base_name)[0] + ".json"
        save_path = os.path.join(SAVE_DIR, json_filename)

        raw_json_data = response.raw_http

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(raw_json_data, f, indent=4)

        print(f"Success! Raw JSON saved to: {save_path}")
        return raw_json_data

    except Exception as e:
        return {"error": f"Mindee API Error: {e!s}"}
