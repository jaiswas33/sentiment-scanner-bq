import os
import re
import functions_framework
from google.cloud import storage, bigquery
import vertexai
from vertexai.preview.generative_models import GenerativeModel

# Configuration
PROJECT_ID = "your_project_id"
REGION = "us-central1"
MODEL = "gemini-2.5-flash-preview-05-20"
DATASET_ID = "you_data_set"
TABLE_ID = "your_data_table"

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=REGION)

# Initialize GCP clients
storage_client = storage.Client()
bq_client = bigquery.Client()
table_ref = bq_client.dataset(DATASET_ID).table(TABLE_ID)

@functions_framework.cloud_event
def process_file(cloud_event):
    data = cloud_event.data
    file_name = data["name"]
    bucket_name = data["bucket"]

    if not file_name.endswith(".txt"):
        print(f"Skipping non-txt file: {file_name}")
        return

    # Extract response ID from filename
    response_id = file_name.replace("response-", "").replace(".txt", "")

    # Read the customer response from GCS
    try:
        blob = storage_client.bucket(bucket_name).blob(file_name)
        customer_response = blob.download_as_text()
    except Exception as e:
        print(f"Error reading file {file_name} from bucket {bucket_name}: {e}")
        return

    # Prompt Gemini to classify sentiment
    prompt = f"""Classify the customer sentiment of this response using only one word: Positive, Neutral, or Negative. Return only the word.\n\n{customer_response}"""

    try:
        model = GenerativeModel(MODEL)
        result = model.generate_content(prompt)
        sentiment_raw = result.text.strip()
        match = re.search(r"\b(Positive|Neutral|Negative)\b", sentiment_raw, re.IGNORECASE)
        sentiment = match.group(1).capitalize() if match else "Unknown"
    except Exception as e:
        print(f"Vertex AI error: {e}")
        sentiment = "Unknown"

    # Insert into BigQuery
    row = {
        "response_id": response_id,
        "customer_response": customer_response,
        "customer_sentiment": sentiment
    }

    try:
        errors = bq_client.insert_rows_json(table_ref, [row])
        if errors:
            print(f"BigQuery insert failed: {errors}")
        else:
            print(f"Inserted response {response_id} with sentiment: {sentiment}")
    except Exception as e:
        print(f"BigQuery insert error: {e}")
