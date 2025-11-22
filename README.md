
# Document Intelligence Pipeline - Implementation Sample

This folder contains a simplified, self-contained implementation sample that demonstrates
the core logic of the OCR routing and logging flow described in the technical assessment.

It is **not meant to run against real GCP services**.
Instead, it illustrates how the pipeline components would be structured in code.

---

## Folder Structure

```
implementation_sample/
│
├── main.py (stub)
├── functions.py (stub)
├── engines.py (stub)
└── README.md
```

---

## Module Descriptions

### **main.py**
Simulates a single batch run of the OCR pipeline:

- Pulls messages (representing Pub/Sub messages)
- Routes each message based on complexity heuristics
- Calls the appropriate OCR engine
- Logs results into BigQuery (or prints them in mock mode)

In the real system, this logic would live inside the **Airflow OCR DAG**.

---

### **functions.py**
Holds the core pipeline logic:

- `pull_messages()`  
  Simulates pulling Pub/Sub messages.

- `route_ocr()`  
  Performs complexity routing (Tesseract vs GCP OCR) and assembles the OCR record.

- `write_ocr_log()`  
  Writes OCR logs into a **BigQuery table (`logging.OCR_logs`)**.

This is where orchestration logic is centralized.

---

### **engines.py**
Contains the OCR engine wrappers:

- `run_tesseract()` – simulates open-source OCR extraction  
- `run_gcp_ocr()` – simulates GCP OCR extraction (Vision / Document AI)

Real OCR client imports are included but commented out.

This module demonstrates how engine-specific code is organized and abstracted.

---

## Mapping to the Architecture

This sample represents the following part of the architecture:

```
Pub/Sub consumption → OCR Engines → BigQuery Logs
```

The sample focuses on:

- Pub/Sub batch consumption simulation  
- OCR routing logic  
- Logging to BigQuery  
- Clear modular structure  

It does **not** include Airflow DAG code, Cloud Run API code, or actual GCP deployments.

---
