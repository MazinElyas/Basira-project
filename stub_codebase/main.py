
"""
This script simulates a single batch run of the OCR pipeline:
  - Pulls messages (as if from Pub/Sub)
  - Routes each message through the OCR router
  - Logs results to BigQuery (or prints them in mock mode)

In the real system, this logic would live inside an Airflow task
within the OCR DAG, running on a schedule (e.g., every 10 minutes).
"""

from __future__ import annotations
from functions import pull_messages, route_ocr, write_ocr_log

def main():
    print("Starting OCR Worker...")

    messages = pull_messages()

    for msg in messages:
        print(f"Processing document: {msg['doc_id']}")

        ocr_output = route_ocr(msg)
        write_ocr_log(ocr_output)

        print(f"Finished {msg['doc_id']} using {ocr_output['ocr_engine']}")
        print("-" * 40)

    print("Worker cycle completed.")


if __name__ == "__main__":
    main()

