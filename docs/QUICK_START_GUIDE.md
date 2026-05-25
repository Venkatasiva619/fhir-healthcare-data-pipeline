# FHIR Healthcare Pipeline - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Verify Environment
```sql
-- Check you have access to Unity Catalog
SHOW CATALOGS;
USE CATALOG workspace;
```

### Step 2: Run Complete Pipeline

Simply open and run: **`00_run_pipeline`**

This will execute all 4 stages automatically:
1. ✅ Raw ingestion (2-5 min)
2. ✅ Bronze load with SCD2 (1-2 min)
3. ✅ Silver transformations (~30 sec)
4. ✅ Gold views (~10 sec)

**Total time: ~4-8 minutes**

### Step 3: Validate Results

```sql
-- Check bronze layer
SELECT * FROM workspace.default.bronze_patient LIMIT 5;

-- Check silver layer
SELECT * FROM workspace.default.silver_patient LIMIT 5;

-- Check gold views
SELECT * FROM workspace.default.dim_patient LIMIT 5;

-- Patient summary analytics
SELECT * FROM workspace.default.patient_summary 
ORDER BY total_encounters DESC LIMIT 10;
```

---

## 📊 What You Get

### Data Assets Created

**Raw Layer** (JSON files)
```
/Volumes/workspace/default/fhir_raw/
  ├── patient/2026-05-25/    (100 files)
  ├── encounter/2026-05-25/  (100 files)
  ├── observation/2026-05-25/ (100 files)
  └── condition/2026-05-25/   (100 files)
```

**Bronze Tables** (Delta with SCD2)
- `workspace.default.bronze_patient` (300 records)
- `workspace.default.bronze_encounter` (300 records)
- `workspace.default.bronze_observation` (300 records)
- `workspace.default.bronze_condition` (300 records)

**Silver Tables** (Cleaned)
- `workspace.default.silver_patient`
- `workspace.default.silver_encounter`
- `workspace.default.silver_observation`
- `workspace.default.silver_condition`

**Gold Views** (Analytics)
- `workspace.default.dim_patient` - Patient demographics
- `workspace.default.fact_encounter` - Encounters with duration
- `workspace.default.fact_observation` - Clinical observations
- `workspace.default.fact_condition` - Diagnoses
- `workspace.default.patient_summary` - Aggregated metrics

---

## 📋 Sample Analytics Queries

### 1. Patient Demographics
```sql
SELECT 
  gender,
  COUNT(*) AS patient_count,
  ROUND(AVG(age), 1) AS avg_age
FROM workspace.default.dim_patient
GROUP BY gender;
```

### 2. Encounter Statistics
```sql
SELECT 
  encounter_class,
  COUNT(*) AS total_encounters,
  ROUND(AVG(duration_hours), 2) AS avg_duration_hours
FROM workspace.default.fact_encounter
WHERE duration_hours IS NOT NULL
GROUP BY encounter_class;
```

### 3. Most Common Conditions
```sql
SELECT 
  condition_display,
  COUNT(*) AS occurrence_count
FROM workspace.default.fact_condition
GROUP BY condition_display
ORDER BY occurrence_count DESC
LIMIT 10;
```

### 4. Patient Health Summary
```sql
SELECT 
  patient_id,
  full_name,
  age,
  gender,
  total_encounters,
  total_observations,
  total_conditions,
  last_encounter_date
FROM workspace.default.patient_summary
ORDER BY total_encounters DESC
LIMIT 20;
```

---

## 🔧 Customization Options

### Change Date Range

Edit `01_raw_ingestion.ipynb`:
```python
# Change from 3 days to 7 days
DATES = [(datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") 
         for i in range(7)]  # Changed from 3 to 7
```

### Use Different Catalog

Edit configuration in all notebooks:
```python
BRONZE_CATALOG = "my_catalog"  # Instead of "workspace"
SILVER_CATALOG = "my_catalog"
```

### Add More Resources

Edit `RESOURCES` list in all notebooks:
```python
RESOURCES = [
    "patient", 
    "encounter", 
    "observation", 
    "condition",
    "medication",  # Add new
    "procedure"    # Add new
]
```

Then create corresponding transformation in `03_silver_transform.ipynb`.

---

## ❓ Troubleshooting

### Issue: "Catalog not found"
```sql
SHOW CATALOGS;
USE CATALOG workspace;
```

### Issue: "Volume not found"
```sql
CREATE VOLUME IF NOT EXISTS workspace.default.fhir_raw;
```

### Issue: Pipeline fails midway

Run individual notebooks to identify which stage failed:
1. `01_raw_ingestion` - Check API connectivity
2. `02_bronze_load` - Check volume path
3. `03_silver_transform` - Check bronze tables exist
4. `04_gold_views` - Check silver tables exist

### Issue: "Connection timeout"

Reduce page size in `01_raw_ingestion.ipynb`:
```python
PAGE_SIZE = 50  # Reduce from 100
```

---

## 📚 Documentation

- **Full Documentation**: See [README.md](README.md)
- **Requirements Validation**: See [PROJECT_VALIDATION.md](PROJECT_VALIDATION.md)
- **Inline Comments**: All notebooks have detailed comments

---

## 🎯 Key Features

✓ **Incremental Processing**: 2-3 days of data with pagination  
✓ **JSON Preservation**: Original API responses stored as-is  
✓ **SCD Type 2**: Full historical tracking with versioning  
✓ **Medallion Architecture**: Raw → Bronze → Silver → Gold  
✓ **Metadata Tracking**: Complete audit trail  
✓ **Delta Lake**: ACID transactions  
✓ **Analytics-Ready**: Pre-joined gold views  
✓ **Configurable**: No hardcoding  

---

## 👥 Support

**Author**: Mada Svenkata Siva Goud  
**Email**: madasvenkatasivagoud@gmail.com  
**Platform**: Databricks on AWS  

---

## ✅ Success Criteria

You've successfully completed the setup when:

1. ✅ All 4 notebooks run without errors
2. ✅ Bronze tables contain 300 records each (100 per day × 3 days)
3. ✅ Silver tables are populated with deduplicated data
4. ✅ Gold views return results
5. ✅ Sample analytics queries work
6. ✅ SCD2 versioning columns are present (valid_from, valid_to, is_current)

**Congratulations! Your FHIR healthcare data pipeline is ready for analytics.**