
# Technical Write-Up

## Introduction
This document describes the reasoning behind the design of the Document Intelligence Pipeline on GCP. The goal was to keep the solution simple, scalable, and cost-efficient without over-engineering anything. I focused on choices that are practical to implement, easy to maintain, and aligned with real-world data engineering constraints.

## Overall Approach
The pipeline is split into three Airflow DAGs: one for OCR processing, one for the base-layer ETL, and one for analytics. This separation keeps each stage focused and easier to debug. It also means failures stay local to a specific stage rather than affecting the entire end-to-end flow.

Documents arrive through a **Cloud Run ingestion API**, which receives the uploaded files from upstream systems and writes them into a GCS bucket called `basira-raw`. Immediately after writing the document, the API publishes a message to a Pub/Sub topic corresponding to the document type (bank statements, invoices, ID cards, etc.).  
This ensures ingestion is completely decoupled from processing. Airflow can pull documents in batches while the ingestion API remains fast and responsive.

Each document type has its own Pub/Sub topic. I made this choice to keep downstream routing clean and to avoid unnecessary branching conditions later.

## OCR Pipeline (DAG 1)
OCR can easily become one of the most expensive parts of the workflow. To control this, I added a simple validation step before choosing the OCR engine. If the document is light (mostly text, small file size), Tesseract is used. Heavy documents go to GCP OCR.

This is not a complex model; it's just a practical way to avoid unnecessary cost while keeping accuracy where it matters. The OCR output is stored in GCS in a clean JSON format that the next DAG can read.

A log entry is written for each document. This helps with tracking performance, failures, and cost patterns over time.

### Flow
- Messages are pulled from Pub/Sub.
- A lightweight validation checks document size, layout, and content density.
- “Light” documents → **Tesseract OCR**
- “Heavy” documents → **GCP OCR (Vision/Document AI)**

### OCR Output
Stored under:
```
gs://basira-ocr/{engine}/{doc_type}/{date}/{doc_id}.json
```

### Logging Table: `logging.OCR_logs`
| Column | Description |
|--------|-------------|
| doc_id | Unique document identifier |
| doc_type | Bank statement, invoice, etc. |
| tenant_id | Tenant/customer identifier |
| ocr_engine | tesseract or gcp |
| ocr_runtime_seconds | Processing duration |
| status | success/fail |
| error_message | If applicable |
| created_at | Timestamp |

## Base Layer ETL (DAG 2)
This stage reads OCR JSON outputs and transforms them into structured tables in BigQuery. I use metadata YAML files because they make the extraction logic flexible. Instead of hardcoding regex patterns or fields inside the DAG, they live in a YAML definition per document type.

A simplified snippet looks like:

### YAML Examples

### Bank Statement
```yaml
document_type: bank_statement
version: 1
columns:
  - name: account_number
    pattern: "Account Number: (?P<value>\d+)"
  - name: customer_name
    pattern: "Customer Name:\s*(?P<value>.+)"
  - name: statement_date
    pattern: "Statement Date: (?P<value>\d{2}/\d{2}/\d{4})"
dq_rules:
  - name: account_number_not_null
    rule: "account_number IS NOT NULL"
    severity: error
```

### Invoice
```yaml
document_type: invoice
version: 1
columns:
  - name: invoice_number
    pattern: "Invoice Number:\s*(?P<value>\S+)"
  - name: total_amount
    pattern: "Total:\s*(?P<value>\d+\.\d{2})"
```

Each base table has a `doc_id`, `doc_location`, and `tenant_id` column to preserve lineage. DQ checks are executed per document, and failures are stored in a monitoring table. I kept the DQ rules simple: not-null checks, numeric reconciliations, and basic validation patterns.

### Base Layer Tables
- baselayer.bank_statements  
- baselayer.invoices  
- baselayer.id_cards  
- baselayer.commercial_regs  

All include:
- doc_id  
- doc_name  
- doc_location  
- tenant_id  
- ocr_engine  
- yaml_version  
- ingest_date  

### DQ & Monitoring Tables
- `monitoring.dq_results`
- `logging.baselayer_logs`

## Analytics and Features (DAG 3)
This DAG builds fact tables, summary tables, and feature tables. The purpose is to support dashboards and potential ML usage later. Nothing fancy here—mainly aggregations and metrics that help operations understand volumes, quality, and processing time.

I also included an SCD Type 2 dimension table (dim_document) for documents to track document evolution.

### Analytical Layer Tables' Examples
- Fact tables (e.g., fact_customers, fact_transactions)

## Model Interaction
Multiple AI models are kept loosely coupled. The orchestration, not the models, decides the order of execution. Outputs are stored in GCS or BigQuery, and each model writes its own version metadata. This makes it easy to replace a model later without breaking the rest of the pipeline.

## Feature Serving
Features are stored in dedicated BigQuery tables (`features.*`). They are organized by business key (doc_id, customer_id) and can be served through simple SQL queries or a lightweight API. This avoids overcomplicating feature storage while still making the signals reusable.

## Closing Thoughts
I avoided heavy components and focused on a design that can be implemented quickly, explained clearly, and scaled as needed. The system balances practicality, cost efficiency, and auditability without adding unnecessary complexity.

---

# Pseudocode

### Extraction Logic
```python
def process_document(doc):
    text = load_ocr_json(doc.ocr_path)["text"]
    metadata = load_yaml(f"gs://basira-metadata/{doc.type}.yaml")

    extracted = {}
    for col in metadata["columns"]:
        pattern = re.compile(col["pattern"])
        match = pattern.search(text)
        extracted[col["name"]] = match.group("value") if match else None

    dq_results = run_dq_checks(extracted, metadata["dq_rules"])
    load_to_bq(f"baselayer.{doc.type}", extracted)
    load_dq_results(dq_results)
```

### DQ Execution
```python
def run_dq(row, rules):
    dq_results = []
    for rule in rules:
        passed = eval_rule(row, rule["rule"])
        dq_results.append({
            "rule_name": rule["name"],
            "passed": passed,
            "severity": rule["severity"]
        })
    return dq_results
```

---