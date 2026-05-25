# Databricks notebook source
# DBTITLE 1,FHIR Data Pipeline Orchestrator
# MAGIC %md
# MAGIC # FHIR Healthcare Data Pipeline Orchestrator
# MAGIC
# MAGIC This notebook orchestrates the complete data pipeline from raw FHIR data to gold-layer analytics.
# MAGIC
# MAGIC ## Pipeline Architecture
# MAGIC
# MAGIC ```
# MAGIC RAW (Volume)          BRONZE (Delta)        SILVER (Delta)         GOLD (Views)
# MAGIC   JSON files      →   SCD2 versioned   →   Cleaned tables    →   Analytics views
# MAGIC   /Volumes/...         bronze_*              silver_*               dim_*, fact_*
# MAGIC ```
# MAGIC
# MAGIC ## Notebooks in Execution Order
# MAGIC
# MAGIC 1. **01_raw_ingestion** - Fetch FHIR data from HAPI server
# MAGIC 2. **02_bronze_load** - Load to bronze with SCD2 versioning
# MAGIC 3. **03_silver_transform** - Transform to clean silver tables
# MAGIC 4. **04_gold_views** - Create analytical views
# MAGIC
# MAGIC ---

# COMMAND ----------

# DBTITLE 1,Configuration and Setup
from datetime import datetime
import time

# Pipeline configuration
PIPELINE_START = datetime.now()
NOTEBOOKS = [
    ("01_raw_ingestion", "Raw data ingestion from FHIR API"),
    ("02_bronze_load", "Bronze layer with SCD2"),
    ("03_silver_transform", "Silver layer transformations"),
    ("04_gold_views", "Gold analytical views")
]

print("="*70)
print("FHIR HEALTHCARE DATA PIPELINE")
print("="*70)
print(f"Pipeline started at: {PIPELINE_START.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total stages: {len(NOTEBOOKS)}\n")

# COMMAND ----------

# DBTITLE 1,Execute Pipeline Stages
# Execute each notebook in sequence
results = []

for i, (notebook_name, description) in enumerate(NOTEBOOKS, 1):
    stage_start = time.time()
    
    print(f"\n{'='*70}")
    print(f"STAGE {i}/{len(NOTEBOOKS)}: {notebook_name}")
    print(f"Description: {description}")
    print(f"{'='*70}")
    
    try:
        # Run the notebook
        result = dbutils.notebook.run(
            f"./{notebook_name}",
            timeout_seconds=3600,  # 60 minutes timeout
            arguments={}
        )
        
        stage_duration = time.time() - stage_start
        status = "✓ SUCCESS"
        
        results.append({
            "stage": i,
            "notebook": notebook_name,
            "status": "success",
            "duration": stage_duration,
            "result": result
        })
        
        print(f"\n{status} - Completed in {stage_duration:.2f} seconds")
        
    except Exception as e:
        stage_duration = time.time() - stage_start
        status = "✗ FAILED"
        error_msg = str(e)
        
        results.append({
            "stage": i,
            "notebook": notebook_name,
            "status": "failed",
            "duration": stage_duration,
            "error": error_msg
        })
        
        print(f"\n{status} - Error after {stage_duration:.2f} seconds")
        print(f"Error: {error_msg}")
        
        # Stop pipeline on failure
        print("\nPipeline stopped due to failure.")
        break

PIPELINE_END = datetime.now()
TOTAL_DURATION = (PIPELINE_END - PIPELINE_START).total_seconds()

# COMMAND ----------

# DBTITLE 1,Pipeline Summary Report
# Generate summary report
print("\n\n" + "="*70)
print("PIPELINE EXECUTION SUMMARY")
print("="*70)
print(f"Start time:  {PIPELINE_START.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"End time:    {PIPELINE_END.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total duration: {TOTAL_DURATION:.2f} seconds ({TOTAL_DURATION/60:.2f} minutes)")
print()

success_count = sum(1 for r in results if r["status"] == "success")
failed_count = sum(1 for r in results if r["status"] == "failed")

print(f"Stages completed: {success_count}/{len(NOTEBOOKS)}")
if failed_count > 0:
    print(f"Stages failed: {failed_count}")
print()

# Detailed stage results
print("Stage Details:")
print("-" * 70)
for r in results:
    status_icon = "✓" if r["status"] == "success" else "✗"
    print(f"{status_icon} Stage {r['stage']}: {r['notebook']:<25} {r['duration']:>8.2f}s")
    if r["status"] == "failed":
        print(f"  Error: {r['error']}")

print("="*70)

if failed_count == 0:
    print("\n🎉 Pipeline completed successfully!")
    print("\nNext steps:")
    print("  • Query gold views: workspace.default.dim_patient, fact_encounter, etc.")
    print("  • Run patient_summary for aggregated metrics")
    print("  • Connect BI tools to gold layer for dashboards")
else:
    print("\n⚠️  Pipeline completed with errors. Check logs above.")

# COMMAND ----------

# DBTITLE 1,Data Quality Checks
# MAGIC %md
# MAGIC ## Optional: Data Quality Validation
# MAGIC
# MAGIC Run these queries to validate the pipeline:

# COMMAND ----------

# DBTITLE 1,Validate record counts
# MAGIC %sql
# MAGIC -- Check record counts across all layers
# MAGIC SELECT 
# MAGIC   'bronze_patient' AS layer_table,
# MAGIC   COUNT(*) AS total_records,
# MAGIC   COUNT(DISTINCT record_id) AS unique_records,
# MAGIC   SUM(CASE WHEN is_current THEN 1 ELSE 0 END) AS current_records
# MAGIC FROM workspace.default.bronze_patient
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'silver_patient',
# MAGIC   COUNT(*),
# MAGIC   COUNT(DISTINCT patient_id),
# MAGIC   NULL
# MAGIC FROM workspace.default.silver_patient
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT 
# MAGIC   'dim_patient',
# MAGIC   COUNT(*),
# MAGIC   COUNT(DISTINCT patient_id),
# MAGIC   NULL
# MAGIC FROM workspace.default.dim_patient;