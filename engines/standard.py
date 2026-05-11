import json
import os
from dotenv import load_dotenv
from mindee import ClientV2, InferenceParameters, PathInput, InferenceResponse

# Load environment variables
load_dotenv()

# Get values from .env
API_KEY = os.getenv("API_KEY")
MODEL_ID = os.getenv("MODEL_ID")

def process_standard(file_path):
    # Setup save directory
    SAVE_DIR = os.path.join("data", "raw_json")
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Initialize Mindee client
    mindee_client = ClientV2(api_key=API_KEY)

    # Set inference parameters
    params = InferenceParameters(model_id=MODEL_ID)

    # Input file
    input_source = PathInput(file_path)

    try:
        # Send document for inference
        response = mindee_client.enqueue_and_get_result(
            InferenceResponse,
            input_source,
            params
        )

        # Create JSON filename
        base_name = os.path.basename(file_path)
        json_filename = os.path.splitext(base_name)[0] + ".json"
        save_path = os.path.join(SAVE_DIR, json_filename)

        # Extract raw response
        raw_json_data = response.raw_http

        # Save JSON
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(raw_json_data, f, indent=4)

        print(f"Success! Raw JSON saved to: {save_path}")

        return raw_json_data

    except Exception as e:
        return {"error": f"Mindee API Error: {str(e)}"}