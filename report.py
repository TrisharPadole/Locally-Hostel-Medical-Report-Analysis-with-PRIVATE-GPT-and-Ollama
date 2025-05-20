import requests
import time
import json

# Define the correct API endpoints
UPLOAD_URL = "http://localhost:8001/v1/ingest/file"  # Updated endpoint
QUERY_URL = "http://localhost:8001/v1/completions"  # Verify if this is correct

# Upload the PDF file
with open("1.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(UPLOAD_URL, files=files)

# Check the response
if response.status_code == 200:
    response_data = response.json()
    print(f"PDF uploaded successfully: {response_data}")

    # Extract the document IDs from the response
    uploaded_docs = response_data.get("data", [])
    latest_doc_ids = [doc["doc_id"] for doc in uploaded_docs]  # List of document IDs

    if not latest_doc_ids:
        print("No document IDs found. Exiting.")
        exit()
else:
    print(f"PDF upload failed. Status Code: {response.status_code}, Response: {response.text}")
    exit()

# Wait 30 seconds to ensure the document is fully processed
time.sleep(30)

# Define the query payload with a context filter
query_payload = {
    "prompt": "Classify the medical report as either 'Blood Test' or 'Ultrasound' and extract only key parameters with their values. Return only the classification and parameters in a structured format, without explanations or extra text.",
    "stream": False,  # Set to True if you want a streamed response
    "use_context": True,
    "include_sources": False,
    "context_filter": {"docs_ids": latest_doc_ids}  # Fixed key name
}

# Send the query request
query_response = requests.post(QUERY_URL, json=query_payload)

# Check if the request was successful
if query_response.status_code == 200:
    response_json = query_response.json()

    # Extract only the "content" field
    content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "No content found")

    # Store the extracted content in a JSON file
    extracted_data = {"extracted_content": content}

    with open("extracted_data.json", "w") as json_file:
        json.dump(extracted_data, json_file, indent=4)

    # Print the extracted content
    print(f"Extracted Content: {json.dumps(extracted_data, indent=4)}")

else:
    print(f"Query Failed. Status Code: {query_response.status_code}, Response: {query_response.text}")