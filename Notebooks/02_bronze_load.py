# Databricks notebook source
# DBTITLE 1,Bronze Layer - Raw to Bronze with SCD2
from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta.tables import DeltaTable

# ── Configuration ────────────────────────────────────────────────────
RAW_PATH = "/Volumes/workspace/default/fhir_raw"
BRONZE_CATALOG = "workspace"
BRONZE_SCHEMA = "default"
RESOURCES = ["patient", "encounter", "observation", "condition"]

# ── Create schema if not exists ─────────────────────────────────────
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {BRONZE_CATALOG}.{BRONZE_SCHEMA}")

print("Bronze layer setup complete.")

# COMMAND ----------

# DBTITLE 1,Process each resource with SCD2
for resource in RESOURCES:
    print(f"\n{'='*60}")
    print(f"Processing {resource.upper()} → Bronze")
    print(f"{'='*60}")
    
    # Read all raw JSON files for this resource
    raw_path = f"{RAW_PATH}/{resource}/"
    print(f"Reading from: {raw_path}")
    
    df = spark.read.option("recursiveFileLookup", "true") \
              .option("multiLine", "true") \
              .json(raw_path)
    
    # Add required metadata columns
    df = df.withColumn("extraction_timestamp", current_timestamp()) \
           .withColumn("api_url_or_params", lit(f"https://hapi.fhir.org/baseR4/{resource.title()}")) \
           .withColumn("record_id", col("resource.id")) \
           .withColumn("ingestion_date", current_date())
    
    # ── SCD Type 2 logic ────────────────────────────────────────────
    # Add versioning columns
    df_new = df.withColumn("valid_from", current_timestamp()) \
               .withColumn("valid_to", lit(None).cast(TimestampType())) \
               .withColumn("is_current", lit(True)) \
               .withColumn("resource_hash", sha2(to_json(col("resource")), 256))
    
    table_name = f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.bronze_{resource}"
    
    # Check if table exists
    table_exists = spark.catalog.tableExists(table_name)
    
    if table_exists:
        print(f"Table {table_name} exists - performing SCD2 merge...")
        bronze_table = DeltaTable.forName(spark, table_name)
        
        # Expire old records that have changed
        bronze_table.alias("old").merge(
            df_new.alias("new"),
            "old.record_id = new.record_id AND old.is_current = true"
        ).whenMatchedUpdate(
            condition="old.resource_hash != new.resource_hash",   # data changed
            set={"is_current": "false", "valid_to": "new.valid_from"}
        ).execute()
        
        # Insert new/changed records
        df_new.write.format("delta").mode("append").saveAsTable(table_name)
        print(f"  ✓ Merged changes with SCD2")
    else:
        # First load
        print(f"Creating new table: {table_name}")
        df_new.write.format("delta").mode("overwrite").saveAsTable(table_name)
        print(f"  ✓ Initial load complete")
    
    # Show count
    count = spark.table(table_name).count()
    current_count = spark.table(table_name).filter("is_current = true").count()
    print(f"  Total records: {count}")
    print(f"  Current records: {current_count}")
    print(f"Bronze {resource}: DONE ✓")

print("\n" + "="*60)
print("All Bronze tables created successfully!")
print("="*60)