# Databricks notebook source
# DBTITLE 1,Silver Layer - Bronze to Silver Transformations
from pyspark.sql.functions import *
from pyspark.sql.types import *

# ── Configuration ────────────────────────────────────────────────────
BRONZE_CATALOG = "workspace"
BRONZE_SCHEMA = "default"
SILVER_CATALOG = "workspace"
SILVER_SCHEMA = "default"

print("Silver layer transformation started...")

# COMMAND ----------

# DBTITLE 1,Transform Patient to Silver
def build_silver_patient():
    """
    Transform bronze patient data to silver layer.
    Extract key patient demographics.
    """
    print("\nTransforming Patient...")
    
    df = spark.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.bronze_patient") \
              .filter("is_current = true")
    
    silver_df = df.select(
        col("resource.id").alias("patient_id"),
        # Handle name array - get first name entry
        col("resource.name")[0]["family"].alias("family_name"),
        col("resource.name")[0]["given"][0].alias("given_name"),
        col("resource.gender").alias("gender"),
        col("resource.birthDate").alias("birth_date"),
        # Metadata
        col("extraction_timestamp"),
        col("ingestion_date")
    ).dropDuplicates(["patient_id"])
    
    return silver_df

# Write Silver Patient
table_name = f"{SILVER_CATALOG}.{SILVER_SCHEMA}.silver_patient"
build_silver_patient().write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(table_name)

count = spark.table(table_name).count()
print(f"  ✓ Silver Patient: {count} records")

# COMMAND ----------

# DBTITLE 1,Transform Encounter to Silver
def build_silver_encounter():
    """
    Transform bronze encounter data to silver layer.
    Extract encounter details and patient references.
    """
    print("\nTransforming Encounter...")
    
    df = spark.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.bronze_encounter") \
              .filter("is_current = true")
    
    silver_df = df.select(
        col("resource.id").alias("encounter_id"),
        col("resource.subject.reference").alias("patient_ref"),
        col("resource.status").alias("status"),
        col("resource.class.code").alias("encounter_class"),
        col("resource.type")[0]["coding"][0]["code"].alias("encounter_type_code"),
        col("resource.type")[0]["coding"][0]["display"].alias("encounter_type_display"),
        col("resource.period.start").cast("timestamp").alias("period_start"),
        col("resource.period.end").cast("timestamp").alias("period_end"),
        col("resource.serviceProvider.reference").alias("service_provider_ref"),
        col("extraction_timestamp")
    ).dropDuplicates(["encounter_id"])
    
    return silver_df

# Write Silver Encounter
table_name = f"{SILVER_CATALOG}.{SILVER_SCHEMA}.silver_encounter"
build_silver_encounter().write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(table_name)

count = spark.table(table_name).count()
print(f"  ✓ Silver Encounter: {count} records")

# COMMAND ----------

# DBTITLE 1,Transform Observation to Silver
def build_silver_observation():
    """
    Transform bronze observation data to silver layer.
    Extract clinical observations and measurements.
    """
    print("\nTransforming Observation...")
    
    df = spark.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.bronze_observation") \
              .filter("is_current = true")
    
    silver_df = df.select(
        col("resource.id").alias("observation_id"),
        col("resource.subject.reference").alias("patient_ref"),
        col("resource.encounter.reference").alias("encounter_ref"),
        col("resource.status").alias("status"),
        col("resource.category")[0]["coding"][0]["code"].alias("category_code"),
        col("resource.code.coding")[0]["code"].alias("observation_code"),
        col("resource.code.coding")[0]["display"].alias("display"),
        col("resource.valueQuantity.value").alias("value_quantity"),
        col("resource.valueQuantity.unit").alias("unit"),
        col("resource.effectiveDateTime").cast("timestamp").alias("effective_date"),
        col("extraction_timestamp")
    ).dropDuplicates(["observation_id"])
    
    return silver_df

# Write Silver Observation
table_name = f"{SILVER_CATALOG}.{SILVER_SCHEMA}.silver_observation"
build_silver_observation().write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(table_name)

count = spark.table(table_name).count()
print(f"  ✓ Silver Observation: {count} records")

# COMMAND ----------

# DBTITLE 1,Transform Condition to Silver
def build_silver_condition():
    """
    Transform bronze condition data to silver layer.
    Extract diagnoses and health conditions.
    """
    print("\nTransforming Condition...")
    
    df = spark.table(f"{BRONZE_CATALOG}.{BRONZE_SCHEMA}.bronze_condition") \
              .filter("is_current = true")
    
    silver_df = df.select(
        col("resource.id").alias("condition_id"),
        col("resource.subject.reference").alias("patient_ref"),
        col("resource.encounter.reference").alias("encounter_ref"),
        col("resource.clinicalStatus.coding")[0]["code"].alias("clinical_status"),
        col("resource.verificationStatus.coding")[0]["code"].alias("verification_status"),
        col("resource.category")[0]["coding"][0]["code"].alias("category_code"),
        col("resource.code.coding")[0]["code"].alias("condition_code"),
        col("resource.code.coding")[0]["display"].alias("condition_display"),
        col("resource.onsetDateTime").cast("timestamp").alias("onset_date"),
        col("resource.recordedDate").cast("timestamp").alias("recorded_date"),
        col("extraction_timestamp")
    ).dropDuplicates(["condition_id"])
    
    return silver_df

# Write Silver Condition
table_name = f"{SILVER_CATALOG}.{SILVER_SCHEMA}.silver_condition"
build_silver_condition().write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(table_name)

count = spark.table(table_name).count()
print(f"  ✓ Silver Condition: {count} records")

# COMMAND ----------

# DBTITLE 1,Summary
print("\n" + "="*60)
print("Silver Layer Transformation Complete!")
print("="*60)
print("\nSummary:")
for table in ["patient", "encounter", "observation", "condition"]:
    count = spark.table(f"{SILVER_CATALOG}.{SILVER_SCHEMA}.silver_{table}").count()
    print(f"  silver_{table}: {count:,} records")