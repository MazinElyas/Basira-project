
# Data Design / Schema Sketch

This document describes how documents evolve across the entire Document Intelligence Pipeline,
from raw ingestion to analytics and feature-ready datasets. It also outlines the schemas for
each major storage layer and includes representative ERD sketches for selected tables.

---

# 2. Layer-by-Layer Data Design

Below are the schemas and expected structure per layer.

---

## 2.1 Raw Layer (GCS – basira-raw)

### Storage Path
```
gs://basira-raw/{doc_type}/{date}/{doc_id}.pdf
```

### File-level Metadata (stored automatically by Cloud Run upload)
- `doc_id`
- `doc_type`
- `tenant_id`
- `uploaded_at`
- `original_filename`
- `file_size`
- `mime_type`

The Raw layer stores immutable copies of all incoming documents.

---

## 2.2 Message Layer (Pub/Sub Topics)

Each uploaded document results in a Pub/Sub message:

```json
{
  "doc_id": "doc-bank-001",
  "doc_type": "bank_statement",
  "tenant_id": "tenant_A",
  "gcs_uri": "gs://basira-raw/bank_statements/2025-01-01/doc-bank-001.pdf",
  "uploaded_at": "2025-01-01T08:15:00Z"
}
```

---

## 2.3 OCR Output Layer (GCS – basira-ocr)

### Storage Path
```
gs://basira-ocr/{engine}/{doc_type}/{date}/{doc_id}.json
```

### OCR JSON Schema
```json
{
  "doc_id": "doc-bank-001",
  "doc_type": "bank_statement",
  "tenant_id": "tenant_A",
  "ocr_engine": "gcp_ocr",
  "ocr_runtime_seconds": 1.23,
  "content": "<full text extracted>",
  "source_uri": "gs://basira-raw/bank_statements/...pdf",
  "extracted_at": "2025-01-01T08:16:04Z"
}
```

---

## 2.4 Logging Layer (BigQuery – logging.OCR_logs)

| Column               | Type      |
|----------------------|-----------|
| doc_id               | STRING    |
| doc_type             | STRING    |
| tenant_id            | STRING    |
| ocr_engine           | STRING    |
| ocr_runtime_seconds  | FLOAT     |
| status               | STRING    |
| error_message        | STRING    |
| created_at           | TIMESTAMP |

Used for monitoring OCR performance, errors, cost behavior, and auditability.

---

## 2.5 Base Layer (BigQuery – baselayer.\*)

### baselayer.bank_statements
| Column          | Type      |
|-----------------|-----------|
| doc_id          | STRING    |
| tenant_id       | STRING    |
| account_number  | STRING    |
| customer_name   | STRING    |
| statement_date  | DATE      |
| yaml_version    | INT64     |
| ocr_engine      | STRING    |
| ingest_date     | TIMESTAMP |
| doc_location    | STRING    |


---

### baselayer.invoices
| Column         | Type      |
|----------------|-----------|
| doc_id         | STRING    |
| tenant_id      | STRING    |
| invoice_number | STRING    |
| invoice_date   | DATE      |
| customer_name  | STRING    |
| total_amount   | FLOAT     |
| yaml_version   | INT64     |
| ocr_engine     | STRING    |
| doc_location   | STRING    |

---

### baselayer.id_cards
| Column      | Type   |
|-------------|--------|
| doc_id      | STRING |
| tenant_id   | STRING |
| full_name   | STRING |
| nationality | STRING |
| id_number   | STRING |
| expiry_date | DATE   |
| yaml_version| INT64  |

---

### baselayer.commercial_regs
| Column              | Type   |
|---------------------|--------|
| doc_id              | STRING |
| company_name        | STRING |
| registration_number | STRING |
| issue_date          | DATE   |
| expiry_date         | DATE   |
| yaml_version        | INT64  |

---

## 2.7 Data Quality Layer

### monitoring.dq_results
| Column     | Type      |
|------------|-----------|
| doc_id     | STRING    |
| rule_name  | STRING    |
| passed     | BOOL      |
| severity   | STRING    |
| checked_at | TIMESTAMP |

---

## 2.8 Dimension Layer – SCD Type 2 (dim_document)

| Column         | Type      |
|----------------|-----------|
| doc_id         | STRING    |
| effective_from | TIMESTAMP |
| effective_to   | TIMESTAMP |
| is_current     | BOOL      |
| doc_type       | STRING    |
| tenant_id      | STRING    |
| source_uri     | STRING    |
| yaml_version   | INT64     |
| meta_hash      | STRING    |

---

## 2.9 Analytics Layer

### analytics.fact_customers
| Column             | Type      |
|--------------------|-----------|
| customer_id        | STRING    |
| tenant_id          | STRING    |
| customer_name      | STRING    |
| total_monthly_spend| FLOAT     |
| avg_trxn_amount    | FLOAT     |
| max_single_payment | DATE      |
| num_invoices       | INT64     |
| num_bank_statements| INT64     |
| risk_indicator     | STRING    |
| last_updated       | TIMESTAMP |
---

## 2.10 Feature Layer

### features.customer_financial_signals
| Column             | Type      |
|--------------------|-----------|
| doc_id             | STRING    |
| tenant_id          | STRING    |
| avg_txn_amount     | FLOAT     |
| total_monthly_spend| FLOAT     |
| max_single_payment | FLOAT     |
| risk_indicator     | STRING    |

---

# 3. Example End-to-End Data Evolution

**Example Document**: Invoice INV-2025-001

| Stage       | Result |
|-------------|--------|
| Raw         | PDF stored in GCS |
| Message     | Pub/Sub doc metadata |
| OCR         | OCR JSON in GCS |
| Base Layer  | Rows in `invoices` |
| DQ          | Rules executed (not null, total check) |
| Analytics   | Included in fact tables |
| Features    | Used to compute customer spending signals |

---