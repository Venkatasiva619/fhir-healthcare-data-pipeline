# FHIR Healthcare Data Pipeline - Medallion Lakehouse Architecture

## 📋 Project Overview

This project implements a complete end-to-end data pipeline for healthcare data ingestion from FHIR (Fast Healthcare Interoperability Resources) API, following the Medallion Lakehouse Architecture pattern with Raw → Bronze → Silver → Gold layers.

### Key Features
- ✅ Incremental data ingestion from public FHIR API
- ✅ Slowly Changing Dimension Type 2 (SCD2) for historical tracking
- ✅ Medallion architecture (Raw → Bronze → Silver → Gold)
- ✅ Modular, reusable code with no hardcoding
- ✅ Comprehensive metadata tracking
- ✅ Pagination handling for large datasets
- ✅ Delta Lake format for ACID transactions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FHIR API (HAPI)                                                │
│  https://hapi.fhir.org/baseR4                                   │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────┐      ┌──────────────────┐                │
│  │   RAW LAYER     │      │   BRONZE LAYER   │                │
│  │   UC Volume     │  →   │   Delta Tables   │                │
│  │   JSON Files    │      │   + SCD Type 2   │                │
│  │   By Date       │      │   + Metadata     │                │
│  └─────────────────┘      └──────────────────┘                │
│         ▼                           ▼                           │
│  ┌──────────────────┐      ┌──────────────────┐               │
│  │  SILVER LAYER    │      │   GOLD LAYER     │               │
│  │  Delta Tables    │  →   │   Views          │               │
│  │  Cleaned &       │      │   Analytics      │               │
│  │  Deduped         │      │   Ready          │               │
│  └──────────────────┘      └──────────────────┘               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
/Users/madasvenkatasivagoud@gmail.com/
│
├── 00_run_pipeline.ipynb       # Master orchestration notebook
├── 01_raw_ingestion.ipynb      # API data ingestion to Volume
├── 02_bronze_load.ipynb        # Raw → Bronze with SCD2
├── 03_silver_transform.ipynb   # Bronze → Silver transformations
├── 04_gold_views.ipynb         # Silver → Gold analytical views
└── README.md                    # This file
```

---

## ✅ Requirements Validation Summary

### ✓ FHIR API Data Ingestion
| Requirement | Status | Implementation |
|------------|--------|----------------|
| Use HAPI FHIR API | ✅ | https://hapi.fhir.org/baseR4 |
| Ingest Patient, Encounter, Observation, Condition | ✅ | All 4 resources implemented |
| Incremental ingestion (2-3 days) | ✅ | Last 3 days with date folders |
| Pagination support | ✅ | Handles page links automatically |
| Store JSON as-is | ✅ | Raw layer preserves original responses |
| Convert to Delta tables | ✅ | Bronze layer uses Delta format |

### ✓ Metadata & Versioning
| Requirement | Status | Column/Feature |
|------------|--------|----------------|
| extraction_timestamp | ✅ | When API was called |
| api_url_or_params | ✅ | Source endpoint tracked |
| ingestion_date | ✅ | When data was saved |
| Track data changes | ✅ | resource_hash for comparison |
| SCD Type 2 | ✅ | valid_from, valid_to, is_current |

### ✓ Medallion Architecture
| Layer | Status | Details |
|-------|--------|--------|
| Raw | ✅ | JSON files in UC Volume by date |
| Bronze | ✅ | Delta tables with SCD2 versioning |
| Silver | ✅ | Cleaned & deduplicated Delta tables |
| Gold | ✅ | Analytical views with joins |

### ✓ Data Orchestration
| Requirement | Status | Implementation |
|------------|--------|----------------|
| Sequential processing | ✅ | Patient → Encounter → Observation → Condition |
| Transformation handling | ✅ | Silver layer transformations |
| Metadata logging | ✅ | All layers track metadata |
| Data loading | ✅ | Automated load to each layer |

### ✓ Code Quality
| Requirement | Status | Details |
|------------|--------|--------|
| Modular code | ✅ | Separate notebooks per layer |
| No hardcoding | ✅ | Configurable catalogs & paths |
| Reusable functions | ✅ | Transform functions per resource |
| Documentation | ✅ | This README + inline comments |

---

## 🚀 Quick Start

### Run Complete Pipeline
```python
# Execute master orchestrator (runs all 4 notebooks)
%run 00_run_pipeline
```

### Expected Output
```
============================================================
FHIR HEALTHCARE DATA PIPELINE
============================================================
Pipeline started at: 2026-05-25 16:20:00
Total stages: 4

STAGE 1/4: 01_raw_ingestion
  ✓ SUCCESS - Completed in 120.45 seconds

STAGE 2/4: 02_bronze_load  
  ✓ SUCCESS - Completed in 45.23 seconds

STAGE 3/4: 03_silver_transform
  ✓ SUCCESS - Completed in 18.67 seconds

STAGE 4/4: 04_gold_views
  ✓ SUCCESS - Completed in 5.32 seconds

============================================================
PIPELINE EXECUTION SUMMARY
============================================================
Total duration: 189.67 seconds (3.16 minutes)
Stages completed: 4/4

🎉 Pipeline completed successfully!
```

---

## 📈 Data Quality Validation

### Verify Record Counts
```sql
-- Check all layers
SELECT 'RAW' AS layer, 'patient' AS resource, COUNT(*) AS files 
FROM read_files('/Volumes/workspace/default/fhir_raw/patient/')

UNION ALL

SELECT 'BRONZE', 'patient', COUNT(*) 
FROM workspace.default.bronze_patient

UNION ALL

SELECT 'SILVER', 'patient', COUNT(*) 
FROM workspace.default.silver_patient;
```

### Validate SCD2 Logic
```sql
-- Find records with multiple versions
SELECT 
  record_id,
  COUNT(*) AS versions,
  SUM(CASE WHEN is_current THEN 1 ELSE 0 END) AS current_count
FROM workspace.default.bronze_patient
GROUP BY record_id
ORDER BY versions DESC;
```

### Gold Layer Analytics
```sql
-- Patient summary statistics
SELECT * FROM workspace.default.patient_summary
ORDER BY total_encounters DESC
LIMIT 10;
```

---

## 📊 Sample Queries

### Get Patient Health Overview
```sql
SELECT 
  p.patient_id,
  p.full_name,
  p.age,
  p.gender,
  COUNT(DISTINCT e.encounter_id) AS total_visits,
  COUNT(DISTINCT o.observation_id) AS total_observations,
  COUNT(DISTINCT c.condition_id) AS total_conditions
FROM workspace.default.dim_patient p
LEFT JOIN workspace.default.fact_encounter e ON p.patient_id = e.patient_id
LEFT JOIN workspace.default.fact_observation o ON p.patient_id = o.patient_id  
LEFT JOIN workspace.default.fact_condition c ON p.patient_id = c.patient_id
GROUP BY p.patient_id, p.full_name, p.age, p.gender
ORDER BY total_visits DESC
LIMIT 20;
```

### Most Common Diagnoses
```sql
SELECT 
  condition_display,
  COUNT(*) AS occurrence_count,
  COUNT(DISTINCT patient_id) AS unique_patients
FROM workspace.default.fact_condition
GROUP BY condition_display
ORDER BY occurrence_count DESC
LIMIT 15;
```

### Average Encounter Duration by Type
```sql
SELECT 
  encounter_type_display,
  COUNT(*) AS encounter_count,
  ROUND(AVG(duration_hours), 2) AS avg_duration_hours,
  ROUND(MIN(duration_hours), 2) AS min_duration_hours,
  ROUND(MAX(duration_hours), 2) AS max_duration_hours
FROM workspace.default.fact_encounter
WHERE duration_hours IS NOT NULL
GROUP BY encounter_type_display
ORDER BY encounter_count DESC;
```

---

## 🔧 Configuration Guide

### Change Catalog/Schema
Edit configuration sections in each notebook:

```python
# Example: Use a different catalog
BRONZE_CATALOG = "my_catalog"  # Instead of "workspace"
BRONZE_SCHEMA = "healthcare"   # Instead of "default"
```

### Modify Date Range
```python
# In 01_raw_ingestion.ipynb
# Current: Last 3 days
DATES = [(datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") 
         for i in range(3)]

# Change to last 7 days
DATES = [(datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") 
         for i in range(7)]

# Or specific date range
DATES = ["2026-05-20", "2026-05-21", "2026-05-22"]
```

### Add More Resources
```python
RESOURCES = [
    "patient", 
    "encounter", 
    "observation", 
    "condition",
    "medication",      # Add new
    "procedure",       # Add new  
    "allergyintolerance"  # Add new
]
```

Then add corresponding transformation functions in `03_silver_transform.ipynb`.

---

## 🐛 Troubleshooting

### Common Issues & Solutions

**Issue:** Catalog not found  
**Solution:**
```sql
SHOW CATALOGS;  -- Check available catalogs
USE CATALOG workspace;  -- Set default
```

**Issue:** Volume not found  
**Solution:**
```sql
CREATE VOLUME IF NOT EXISTS workspace.default.fhir_raw;
```

**Issue:** DBFS disabled error  
**Solution:** All code uses `/Volumes/` paths (Unity Catalog), no DBFS.

**Issue:** API timeout  
**Solution:** Reduce PAGE_SIZE or add retry logic:
```python
PAGE_SIZE = 50  # Reduce from 100
```

**Issue:** Schema mismatch in silver layer  
**Solution:** Some FHIR resources may have null nested fields. Add null checks:
```python
col("resource.name")[0]["family"] if col("resource.name") else None
```

---

## 📚 Technical Details

### SCD Type 2 Implementation

The bronze layer implements Slowly Changing Dimension Type 2 to track historical changes:

1. **Initial Load**: All records marked as `is_current = True`
2. **Subsequent Loads**:
   - Calculate `resource_hash` (SHA256 of JSON)
   - Compare with existing records
   - If changed:
     - Expire old version: Set `is_current = False`, `valid_to = now()`
     - Insert new version: Set `is_current = True`, `valid_from = now()`
   - If unchanged: Skip (no duplicate insertion)

```sql
-- Merge logic example
MERGE INTO bronze_patient old
USING new_data new
ON old.record_id = new.record_id AND old.is_current = true
WHEN MATCHED AND old.resource_hash != new.resource_hash THEN
  UPDATE SET is_current = false, valid_to = new.valid_from
```

### Data Lineage

```
FHIR API
  ↓ (01_raw_ingestion)
RAW JSON files in UC Volume
  ↓ (02_bronze_load) 
Bronze Delta Tables (versioned)
  ↓ (03_silver_transform)
Silver Delta Tables (cleaned)
  ↓ (04_gold_views)
Gold Views (analytics-ready)
```

### Performance Considerations

- **Raw Layer**: Individual JSON files for audit trail (can be large)
- **Bronze Layer**: Delta format with SCD2 (2-3x size due to history)
- **Silver Layer**: Deduplicated, current records only
- **Gold Layer**: Views with pre-computed joins (no storage overhead)

**Recommendations:**
- Run OPTIMIZE on bronze tables weekly
- Run VACUUM on bronze tables after 30 days
- Consider partitioning by `ingestion_date` for large datasets

---

## 🚀 Next Steps & Enhancements

### Immediate Actions
1. ✅ Validate pipeline runs end-to-end
2. ✅ Review data quality in gold layer
3. ☐ Create Power BI dashboard (optional)

### Future Improvements

#### 1. Incremental Processing
```python
# Only process new dates since last run
last_run_date = spark.sql("""
  SELECT MAX(ingestion_date) FROM bronze_patient
""").collect()[0][0]

DATES = [date for date in all_dates if date > last_run_date]
```

#### 2. Data Quality Framework
```python
# Add Great Expectations or Delta constraints
spark.sql("""
  ALTER TABLE silver_patient 
  ADD CONSTRAINT valid_birth_date 
  CHECK (birth_date <= current_date())
""")
```

#### 3. XML Format Support
```python
# Alternative XML ingestion
df = spark.read.format("xml") \
  .option("rowTag", "entry") \
  .load(raw_path)
```

#### 4. Monitoring & Alerting
```python
# Track pipeline metrics
metrics = {
  "records_processed": count,
  "duration_seconds": duration,
  "success": True
}
log_metrics(metrics)
```

#### 5. CI/CD with Databricks Asset Bundles
```yaml
# databricks.yml
resources:
  pipelines:
    fhir_pipeline:
      name: "FHIR Healthcare Pipeline"
      libraries:
        - notebook:
            path: ./01_raw_ingestion.ipynb
```

---

## 📝 Submission Checklist

- [x] Ingest 2-3 days of data with pagination
- [x] Store JSON responses as-is in lakehouse
- [x] Implement Raw → Bronze → Silver → Gold layers
- [x] Add metadata columns (extraction_timestamp, api_url_or_params)
- [x] Implement SCD Type 2 for versioning
- [x] Create modular, reusable code (no hardcoding)
- [x] Build orchestration pipeline
- [x] Document architecture and table relationships
- [x] Add validation queries
- [ ] Optional: XML format support
- [ ] Optional: Power BI dashboard

---

## 👥 Contact

**Author:** Mada Svenkata Siva Goud  
**Email:** madasvenkatasivagoud@gmail.com  
**Platform:** Databricks on AWS  
**Date:** May 25, 2026  

---

## 🙏 Acknowledgments

- **HAPI FHIR Server** - Public FHIR API for healthcare data
- **HL7 FHIR Community** - Healthcare interoperability standards
- **Databricks** - Medallion architecture pattern
- **Delta Lake** - ACID transactions for data lakes

---

**Project Status:** ✅ Production Ready  
**Last Updated:** May 25, 2026  
**Version:** 1.0.0