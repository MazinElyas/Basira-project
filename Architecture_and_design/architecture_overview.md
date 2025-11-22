
# Architecture Overview

## 1. End-to-End System Overview

The Document Intelligence Pipeline is a scalable, cost-efficient, and auditable document processing system built on Google Cloud Platform (GCP). It ingests documents from upstream applications, applies OCR with dynamic cost-aware routing, transforms extracted content into structured datasets, and serves analytics- and feature-ready tables to downstream systems. The design balances simplicity and extensibility while ensuring strong governance, lineage, and operational visibility.

The processing pipeline consists of three Airflow (Composer) DAGs, each responsible for a specific segment of the lifecycle:

1. **OCR Pipeline (DAG 1)** – Batch-pulls messages from Pub/Sub, extracts text using Tesseract or GCP OCR depending on document complexity, and writes OCR results to GCS.
2. **Base Layer ETL (DAG 2)** – Converts OCR JSON outputs into structured BigQuery base-layer tables using metadata-driven extraction logic and executes data quality checks.
3. **Analytics & Features (DAG 3)** – Produces curated fact tables, summary tables, and reusable features for downstream analytics and model-driven use cases.

Each document flows through the system with complete traceability. Lineage, logs, and data quality outcomes are written to BigQuery logging and monitoring datasets.

---

## 2. Ingestion Layer (Producer)

Documents are submitted by upstream applications through a **Cloud Run ingestion API** (`/documents/upload`).  
This API is responsible for two key actions:

### **A. Write raw documents to Cloud Storage**
Documents are stored under a structured path in the raw bucket:

```
gs://basira-raw/{doc_type}/{ingestion_date}/{doc_id}.[pdf/png/jpeg]/
```

### **B. Publish messages to Pub/Sub topics**
For each document type, the API publishes a message to a dedicated Pub/Sub topic:

- `topic-bank-statements`
- `topic-invoices`
- `topic-id-cards`
- `topic-commercial-regs`

Each message contains:

- `doc_id`
- `doc_type`
- `tenant_id`
- `gcs_uri`
- `uploaded_at`

This design **decouples ingestion from processing**, enabling Airflow to scale independently and process documents in reliable, predefined batches.

Pub/Sub acts as a **durable message buffer**, holding document-processing events until the Airflow OCR DAG pulls and processes/ACKS them.

---

## 3. DAG 1 — OCR Pipeline (Batch Pull via Pub/Sub)

The OCR pipeline runs on a schedule (e.g., every 10 minutes) and consumes messages from Pub/Sub subscriptions.  
This batch-pull model avoids long-lived consumers inside Airflow and fits naturally into batch-oriented document processing.

The pipeline applies a cost-aware OCR routing mechanism:

- **Tesseract OCR** – used for light, text-dominant documents (lower cost)
- **GCP OCR (Vision/Document AI)** – used for heavier, more complex documents

OCR output is standardized and written into:

```
gs://basira-ocr/{engine}/{doc_type}/{date}/{doc_id}.json
```

### **OCR Logging**
For each processed document, an entry is inserted into:

- `logging.OCR_logs`

Including:

- `doc_id`, `doc_type`, `tenant_id`
- `ocr_engine`
- `ocr_runtime_seconds`
- `status`, `error_message`
- `created_at`

This creates a complete audit trail for the OCR stage.

---

## 4. DAG 2 — Base Layer ETL

The Base Layer ETL pipeline is metadata-driven. It reads:

- OCR JSON outputs from GCS  
- YAML configuration files from `basira-metadata`  

The YAML files define:

- Field extraction patterns (regex / JSONPath)
- Column mappings and target data types
- Document-specific data quality rules

The pipeline loads the extracted results into the following base-layer tables:

- `baselayer.bank_statements`
- `baselayer.invoices`
- `baselayer.id_cards`
- `baselayer.commercial_regs`

Each row contains lineage attributes including:

- `doc_id`
- `doc_location`
- `tenant_id`
- `ocr_engine`
- `yaml_version`
- `ingest_date`

### **Data Quality Checks**
Data Quality checks (from YAML rules) validate correctness and completeness, with results written to:
- `monitoring.dq_results`
- `logging.baselayer_logs`

An SCD Type 2 `dim_document` table maintains long-term document metadata evolution.

---

## 5. DAG 3 — Analytics & Features

This pipeline aggregates base-layer data into business-ready structures:

- Fact tables (e.g., `fact_customers`)
- Summary tables (processing KPIs, DQ scores, OCR performance)
- Feature tables for downstream services (e.g., financial metrics)

These datasets support reporting, BI dashboards, and ML feature consumption.

---

## 6. Governance, Security & Lineage

The system enforces strict data governance principles:

- GCS buckets and BigQuery datasets are protected by IAM and VPC Service Controls.
- Sensitive fields (IDs, account numbers, personal data) are masked using BigQuery policy tags.
- Lineage metadata traces each record from the raw document → OCR → base layer → analytics.
- All steps write detailed logs with timestamps, versions, and runtime information.

---

## 7. Architecture Diagram

The full system architecture diagram reflects:

- Cloud Run API as the **document ingestion producer**
- Pub/Sub topics as the **message buffer**
- Airflow as the **batch consumer & orchestrator**
- GCS & BigQuery as the **storage and analytics layers**
