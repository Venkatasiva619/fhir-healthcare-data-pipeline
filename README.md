# FHIR Healthcare Data Pipeline

[![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=flat&logo=databricks&logoColor=white)](https://databricks.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5-orange?style=flat&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Delta Lake](https://img.shields.io/badge/Delta%20Lake-Enabled-brightgreen?style=flat)](https://delta.io/)

A production-grade healthcare data pipeline implementing the **Medallion Architecture** (Bronze-Silver-Gold) for FHIR (Fast Healthcare Interoperability Resources) data processing on Databricks.

## 🎯 Project Overview

This pipeline demonstrates modern data engineering best practices:
- **Incremental data ingestion** from HAPI FHIR R4 public API
- **SCD Type 2** (Slowly Changing Dimensions) for historical tracking
- **Medallion Architecture** with Bronze → Silver → Gold layers
- **Delta Lake** for ACID transactions and time travel
- **Unity Catalog** for data governance
- **Metadata tracking** for lineage and audit

## 🏗️ Architecture

```
FHIR API (HAPI R4)
      ↓
┌──────────────────────────────────────────────────────────────┐
│  RAW LAYER (Unity Catalog Volume)                           │
│  - JSON files with date partitioning                        │
│  - Path: /Volumes/workspace/default/fhir_raw/               │
│  - Format: {resource}/{date}/record_*.json                  │
└──────────────────────────────────────────────────────────────┘
      ↓
┌──────────────────────────────────────────────────────────────┐
│  BRONZE LAYER (Delta Tables with SCD2)                      │
│  - bronze_patient                                            │
│  - bronze_encounter                                          │
│  - bronze_observation                                        │
│  - bronze_condition                                          │
│  - Columns: resource JSON + metadata + SCD2 fields          │
└──────────────────────────────────────────────────────────────┘
      ↓
┌──────────────────────────────────────────────────────────────┐
│  SILVER LAYER (Cleaned & Transformed)                       │
│  - silver_patient                                            │
│  - silver_encounter                                          │
│  - silver_observation                                        │
│  - silver_condition                                          │
│  - Flattened FHIR resources with typed columns              │
└──────────────────────────────────────────────────────────────┘
      ↓
┌──────────────────────────────────────────────────────────────┐
│  GOLD LAYER (Analytics Views)                               │
│  - dim_patient (patient demographics)                       │
│  - fact_encounter (encounter facts)                         │
│  - fact_observation (clinical observations)                 │
│  - fact_condition (diagnosis conditions)                    │
│  - patient_summary (aggregated metrics)                     │
└──────────────────────────────────────────────────────────────┘
```

## 📁 Repository Structure

```
fhir-healthcare-data-pipeline/
├── notebooks/
│   ├── 00_run_pipeline.ipynb      # Master orchestrator
│   ├── 01_raw_ingestion.ipynb     # FHIR API data fetch
│   ├── 02_bronze_load.ipynb       # Bronze layer with SCD2
│   ├── 03_silver_transform.ipynb  # Silver transformations
│   └── 04_gold_views.ipynb        # Gold analytical views
├── docs/
│   ├── README.md                  # Detailed documentation
│   ├── PROJECT_VALIDATION.md      # Requirements compliance
│   └── QUICK_START_GUIDE.md       # 5-minute setup guide
├── .gitignore
├── SETUP.md                       # Git setup instructions
├── QUICK_REFERENCE.md             # One-page quick start
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Databricks workspace (AWS/Azure/GCP)
- Unity Catalog enabled
- Serverless or cluster with DBR 13.3+
- Python 3.10+

### Setup Steps

1. **Clone this repository**
   ```bash
   git clone https://github.com/madasvenkatasiva/fhir-healthcare-data-pipeline.git
   cd fhir-healthcare-data-pipeline
   ```

2. **Import to Databricks**
   - Open your Databricks workspace
   - Navigate to Workspace → Users → Your folder
   - Click Import → select all `.ipynb` files from `notebooks/`

3. **Create Unity Catalog Volume**
   ```sql
   CREATE VOLUME IF NOT EXISTS workspace.default.fhir_raw;
   ```

4. **Run the pipeline**
   - Open `00_run_pipeline` notebook
   - Click "Run All" or execute cells sequentially
   - Monitor progress through the orchestrator

### Manual Execution

Run notebooks in this order:
```bash
1. 01_raw_ingestion      # Fetch 3 days of FHIR data
2. 02_bronze_load        # Load to bronze with SCD2
3. 03_silver_transform   # Transform to silver
4. 04_gold_views         # Create gold views
```

## 📊 Data Pipeline Details

### Raw Ingestion (01)
- **Source**: HAPI FHIR R4 Public Server
- **Resources**: Patient, Encounter, Observation, Condition
- **Pagination**: Handles API pagination automatically
- **Storage**: Unity Catalog Volume
- **Format**: JSON files partitioned by date
- **Incremental**: Fetches last 3 days by default

### Bronze Layer (02)
- **Technology**: Delta Lake with SCD Type 2
- **Change Detection**: SHA256 hash of resource JSON
- **Versioning**: `valid_from`, `valid_to`, `is_current` columns
- **Metadata**: Extraction timestamps, API parameters, ingestion dates
- **Schema**: Preserves raw JSON in `resource` column

### Silver Layer (03)
- **Transformation**: Flatten FHIR JSON to typed columns
- **Deduplication**: Remove duplicate records
- **Data Quality**: Handle missing/null values
- **Fields**: Extract patient demographics, encounter details, observations, conditions

### Gold Layer (04)
- **Views**: Business-ready analytical datasets
- **Joins**: Patient-centric with encounter/observation/condition facts
- **Aggregations**: Patient summaries with counts and latest dates
- **Use Cases**: BI dashboards, ML features, analytics

## ✨ Key Features

### ✅ Incremental Ingestion
- Configurable time windows (default: 3 days)
- Date-based partitioning for efficient queries
- Idempotent: safe to re-run

### ✅ SCD Type 2
- Full history preservation
- Change tracking with hashing
- Current/historical record separation

### ✅ Medallion Architecture
- **Bronze**: Raw, immutable data lake
- **Silver**: Cleaned, conformed data
- **Gold**: Business-level aggregates

### ✅ Metadata & Governance
- Source URL/parameters tracking
- Extraction timestamps
- Unity Catalog integration
- Delta Lake time travel

### ✅ Error Handling
- Graceful pagination failures
- Missing field handling
- Pipeline stage status tracking

## 📈 Sample Queries

```sql
-- Patient demographics
SELECT * FROM workspace.default.dim_patient LIMIT 10;

-- Recent encounters
SELECT * FROM workspace.default.fact_encounter 
WHERE period_start >= CURRENT_DATE() - INTERVAL 7 DAYS;

-- Patient health summary
SELECT * FROM workspace.default.patient_summary
WHERE total_encounters > 0;

-- SCD2 History
SELECT patient_id, valid_from, valid_to, is_current
FROM workspace.default.bronze_patient
WHERE record_id = 'Patient/12345'
ORDER BY valid_from;
```

## 🧪 Testing & Validation

Run validation queries from `00_run_pipeline` notebook:
```sql
SELECT 'bronze_patient' AS layer, COUNT(*) AS records 
FROM workspace.default.bronze_patient
UNION ALL
SELECT 'silver_patient', COUNT(*) 
FROM workspace.default.silver_patient;
```

## 📚 Documentation

- **[PROJECT_VALIDATION.md](docs/PROJECT_VALIDATION.md)**: Complete requirements compliance matrix
- **[QUICK_START_GUIDE.md](docs/QUICK_START_GUIDE.md)**: 5-minute setup guide
- **[Detailed README](docs/README.md)**: Comprehensive technical documentation
- **[SETUP.md](SETUP.md)**: GitHub setup instructions
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**: One-page quick reference

## 🛠️ Configuration

Edit variables in each notebook:

```python
# Catalog and schema
BRONZE_CATALOG = "workspace"
BRONZE_SCHEMA = "default"

# Data paths
RAW_PATH = "/Volumes/workspace/default/fhir_raw"

# FHIR resources to process
RESOURCES = ["Patient", "Encounter", "Observation", "Condition"]

# Ingestion window
DAYS_TO_FETCH = 3
```

## 🎓 Learning Resources

- [FHIR R4 Specification](https://hl7.org/fhir/R4/)
- [Databricks Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)
- [Delta Lake SCD Type 2](https://docs.databricks.com/delta/index.html)
- [Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/index.html)

## 📝 Assignment Requirements

✅ **24/24 Mandatory Requirements Met** (100%)

| Category | Requirements | Status |
|----------|--------------|--------|
| API Ingestion | 7 | ✅ 100% |
| Metadata & Versioning | 5 | ✅ 100% |
| Medallion Architecture | 4 | ✅ 100% |
| Data Orchestration | 4 | ✅ 100% |
| Code Quality | 4 | ✅ 100% |

See [PROJECT_VALIDATION.md](docs/PROJECT_VALIDATION.md) for detailed compliance proof.

## 🤝 Contributing

This is an educational project. Feel free to:
- Report issues
- Suggest improvements
- Fork and customize

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

**Madas Venkata Siva**
- GitHub: [@madasvenkatasiva](https://github.com/madasvenkatasiva)
- Email: madasvenkatasiva@gmail.com

## 🙏 Acknowledgments

- HAPI FHIR public server for test data
- Databricks for the platform
- HL7 FHIR community

---

**Built with ❤️ on Databricks**
