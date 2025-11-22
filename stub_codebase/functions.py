
"""functions.py

Core orchestration functions used by the implementation sample:

- pull_messages: simulate pulling messages from Pub/Sub
- route_ocr: decide which OCR engine to use and run it
- write_ocr_log: write OCR results into a BigQuery table (logging.OCR_logs)

This module is designed to mirror the behavior of the GCP-based
architecture, while remaining simple and readable for assessment purposes.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List
from google.cloud import bigquery
from engines import run_tesseract, run_gcp_ocr




def pull_messages() -> List[Dict[str, Any]]:
    """Simulate pulling messages from Pub/Sub subscriptions.

    In production, this would use google-cloud-pubsub's SubscriberClient
    to pull messages from a subscription, then ACK them once processed.

    """
    return [
        {
            "doc_id": "doc-bank-001",
            "doc_type": "bank_statement",
            "tenant_id": "tenant_A",
            "gcs_uri": "gs://basira-raw/bank_statements/2025-01-01/doc-bank-001.pdf",
            "uploaded_at": "2025-01-01T08:15:00Z",
        },
        {
            "doc_id": "doc-inv-002",
            "doc_type": "invoice",
            "tenant_id": "tenant_B",
            "gcs_uri": "gs://basira-raw/invoices/2025-01-01/doc-inv-002.pdf",
            "uploaded_at": "2025-01-01T08:20:00Z",
        },
    ]


def route_ocr(message: dict) -> dict:
    """
    Route document to Tesseract or GCP OCR based on simple complexity check.
    """

    doc_id = message["doc_id"]
    doc_type = message["doc_type"]
    tenant_id = message["tenant_id"]
    file_path = message["gcs_uri"]

    # Check file size to simulate complexity
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    is_light = size_mb < 1.0  # threshold

    if is_light:
        ocr_engine = "tesseract"
        ocr_result = run_tesseract(file_path)
    else:
        ocr_engine = "gcp_ocr"
        ocr_result = run_gcp_ocr(file_path)

    return {
        "doc_id": doc_id,
        "doc_type": doc_type,
        "tenant_id": tenant_id,
        "ocr_engine": ocr_engine,
        "ocr_text": ocr_result["text"],
        "ocr_runtime_seconds": round(ocr_result["runtime"], 3),
        "status": ocr_result["status"],
        "error_message": ocr_result.get("error", None),
        "created_at": datetime.utcnow().isoformat()
    }


def write_ocr_log(record: dict):
    client = bigquery.Client()

    table_id = "basira.logging.OCR_logs"

    row = [
        {
            "doc_id": record["doc_id"],
            "doc_type": record["doc_type"],
            "tenant_id": record["tenant_id"],
            "ocr_engine": record["ocr_engine"],
            "ocr_runtime_seconds": record["ocr_runtime_seconds"],
            "status": record["status"],
            "error_message": record["error_message"],
            "created_at": record["created_at"],
        }
    ]

    errors = client.insert_rows_json(table_id, row)

    if errors:
        print(f"Failed to log OCR data: {errors}")
    else:
        print(f"Logged OCR record for {record['doc_id']}")

