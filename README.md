
# Document Intelligence Pipeline (GCP)

A scalable, secure, and cost-efficient **Document Intelligence Pipeline** built on **Google Cloud Platform (GCP)**.  
Designed for processing high-volume documents such as bank statements, invoices, ID cards, and commercial registrations.

This repository contains:

- **Architecture & Design** (diagrams, ERD, lineage)  
- **Technical Write-Up**  
- **Implementation Sample**  
- **Presentation**  
- **Data Models & Metadata Structures**

---

## 1. Project Overview

Enterprises ingest thousands of documents per day.  
This pipeline extracts, structures, validates, and analyzes document content using a cloud-native design.

### **Core Capabilities**
- Multi-type document ingestion  
- Cost-aware OCR (Tesseract + GCP Document AI)  
- Metadata-driven extraction (YAML)  
- BigQuery-based base & analytics layers  
- Full lineage, logging, and auditability  
- Feature generation for ML & analytics  

---

## 2. Architecture Summary

The system is composed of an **ingestion layer** and **three Airflow DAGs** sitting on top of GCP services:

### Ingestion layer
- Write raw documents to Cloud Storage.
- Publish messages to Pub/Sub topics.

### **DAG 1 — OCR Pipeline**
- Pulls messages from Pub/Sub  
- Chooses OCR engine  
- Extracts text and stores JSON in GCS  
- Logs to BigQuery  

### **DAG 2 — Base Layer ETL**
- Parses OCR JSON  
- Uses YAML metadata to structure data  
- Loads base tables into BigQuery  
- Runs DQ checks  

### **DAG 3 — Analytics & Features**
- Builds fact & summary tables  
- Generates customer-level features  
- Produces business-ready datasets  

Architecture diagrams & lineage visuals are available in:  
`/Architecture_and_design/`

---

## 3. Repository Structure

```
.
├── Architecture_and_design/
│   ├── architecture_overview.md
|   ├── Architecture diagram.png
|   ├── erd_bank_statements.png
│   ├── erd_fact_customers.png
│   ├── erd_dim_document.png
│   ├── erd_ocr_logs.png
│   └── customer_data_lineage.png
│
├── stub_codebase/
│   ├── main.py
│   ├── engines.py
│   └── functions.py
│
├── Basira presentation.pdf
│
├── writeup.md
│
└── README.md
```

---

## 4. Implementation Sample

A minimal, modular Python code sample demonstrating the OCR pipeline logic:

- **`main.py`** – batch pipeline runner  
- **`functions.py`** – Pub/Sub simulation, routing, logging  
- **`engines.py`** – Tesseract & GCP OCR mock engines  

These samples illustrate the core logic used inside Airflow DAG tasks.

---

## 5. Data Model & Schema Design

Located in:  
`Architecture_and_design/`

Includes:

- Base layer schemas  
- Analytical fact tables  
- Dimension tables (SCD Type 2)  
- Logging tables  
- DQ result schema  
- Lineage diagram  

---

## 6. Presentation

The final PDF is included:  
**Basira presentation.pdf**

Contains:

- Architecture summary  
- OCR flow  
- ETL flow  
- Governance model  
- Customer-level analytics model  
- Q&A slide  

---

## 7. Key Features

### Metadata-Driven  
YAML files define extraction logic, enabling rapid onboarding of new document types.

### Cost Awareness  
Tesseract vs. GCP OCR decision logic helps optimize processing cost.

### Strong Governance  
Policy tags, lineage fields, IAM and VPC-SC ensure secure handling of sensitive data.

### Clean Separation of Concerns  
Distinct DAGs for OCR, ETL, and Analytics increase clarity & maintainability.

### End-to-End Observability  
BigQuery-based logs capture performance, errors, and workflow-level metadata.

---

## 8. Future Extensions

- Add new document types with minimal engineering effort  
- Add ML-driven OCR routing model  
- Support near-real-time ingestion (Cloud Run + Pub/Sub Push)  
- Expand customer-level features for ML models
- Integrate apache spark engine for processing efficiency.
- Build & integrate AI agents to interact with the open-source OCR and enhance it.  

---
