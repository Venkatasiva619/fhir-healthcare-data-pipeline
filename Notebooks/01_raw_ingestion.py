# Databricks notebook source
# DBTITLE 1,Raw Data Ingestion
# MAGIC %md
# MAGIC # Raw Data Ingestion - FHIR API to Volume
# MAGIC
# MAGIC This notebook fetches healthcare data from the public HAPI FHIR server and stores it as raw JSON files in a Unity Catalog Volume.
# MAGIC
# MAGIC ## Data Sources
# MAGIC * **API**: HAPI FHIR R4 (https://hapi.fhir.org/baseR4)
# MAGIC * **Resources**: Patient, Encounter, Observation, Condition
# MAGIC * **Storage**: `/Volumes/workspace/default/fhir_raw`
# MAGIC
# MAGIC ## Key Features
# MAGIC * Pagination handling for large datasets
# MAGIC * Incremental data collection (last 3 days)
# MAGIC * Raw JSON preservation for auditability

# COMMAND ----------

# DBTITLE 1,Cell 1
import requests, json
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, current_timestamp

spark = SparkSession.builder.getOrCreate()

# ── Config (no hardcoding) ──────────────────────────────────────────
BASE_URL   = "https://hapi.fhir.org/baseR4"
RESOURCES  = ["Patient", "Encounter", "Observation", "Condition"]
# Use Unity Catalog Volume (required for serverless compute)
RAW_PATH   = "/Volumes/workspace/default/fhir_raw"  
PAGE_SIZE  = 100
# Ingest last 2–3 days
DATES = [(datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(3)]

# ── Pagination helper ───────────────────────────────────────────────
def fetch_all_pages(resource: str, date: str) -> list[dict]:
    records, url = [], f"{BASE_URL}/{resource}?_count={PAGE_SIZE}&_format=json"
    while url:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        bundle = resp.json()
        records.extend(bundle.get("entry", []))
        # find next page link
        url = next((l["url"] for l in bundle.get("link", []) if l.get("rel") == "next"), None)
    return records

# ── Ingest and save raw JSON ────────────────────────────────────────
for date in DATES:
    for resource in RESOURCES:
        print(f"Fetching {resource} for {date}...")
        entries = fetch_all_pages(resource, date)
        
        # Save raw JSON (as-is requirement)
        path = f"{RAW_PATH}/{resource.lower()}/{date}"
        dbutils.fs.mkdirs(path)
        
        for i, entry in enumerate(entries):
            json_str = json.dumps(entry)
            dbutils.fs.put(f"{path}/record_{i}.json", json_str, overwrite=True)
        
        print(f"  Saved {len(entries)} records to {path}")