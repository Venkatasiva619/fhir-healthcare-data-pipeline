# Databricks notebook source
# DBTITLE 1,Gold Layer - Analytical Views
# MAGIC %md
# MAGIC # Gold Layer - Analytical Views
# MAGIC
# MAGIC This notebook creates business-ready views for analytics and reporting:
# MAGIC
# MAGIC * **dim_patient** - Patient dimension with demographics and calculated age
# MAGIC * **fact_encounter** - Encounter facts with patient context and duration
# MAGIC * **fact_observation** - Clinical observations and measurements
# MAGIC * **fact_condition** - Patient conditions and diagnoses
# MAGIC * **patient_summary** - Aggregated patient health metrics

# COMMAND ----------

# DBTITLE 1,Create dim_patient view
# MAGIC %sql
# MAGIC -- Dimension: Patient Demographics with Age Calculation
# MAGIC CREATE OR REPLACE VIEW workspace.default.dim_patient AS
# MAGIC SELECT
# MAGIC     patient_id,
# MAGIC     family_name,
# MAGIC     given_name,
# MAGIC     CONCAT(given_name, ' ', family_name) AS full_name,
# MAGIC     gender,
# MAGIC     birth_date,
# MAGIC     CAST(DATEDIFF(CURRENT_DATE(), birth_date) / 365.25 AS INT) AS age,
# MAGIC     ingestion_date,
# MAGIC     extraction_timestamp
# MAGIC FROM workspace.default.silver_patient;
# MAGIC
# MAGIC SELECT COUNT(*) AS patient_count FROM workspace.default.dim_patient;

# COMMAND ----------

# DBTITLE 1,Create fact_encounter view
# MAGIC %sql
# MAGIC -- Fact: Encounters with Patient Demographics and Duration
# MAGIC CREATE OR REPLACE VIEW workspace.default.fact_encounter AS
# MAGIC SELECT
# MAGIC     e.encounter_id,
# MAGIC     e.patient_ref,
# MAGIC     -- Extract patient ID from reference (format: "Patient/123")
# MAGIC     REGEXP_EXTRACT(e.patient_ref, 'Patient/(.+)', 1) AS patient_id,
# MAGIC     p.full_name AS patient_name,
# MAGIC     p.gender,
# MAGIC     p.age,
# MAGIC     e.status,
# MAGIC     e.encounter_class,
# MAGIC     e.encounter_type_code,
# MAGIC     e.encounter_type_display,
# MAGIC     e.period_start,
# MAGIC     e.period_end,
# MAGIC     CAST((UNIX_TIMESTAMP(e.period_end) - UNIX_TIMESTAMP(e.period_start)) / 3600 AS DECIMAL(10,2)) AS duration_hours,
# MAGIC     e.service_provider_ref,
# MAGIC     e.extraction_timestamp
# MAGIC FROM workspace.default.silver_encounter e
# MAGIC LEFT JOIN workspace.default.dim_patient p
# MAGIC   ON REGEXP_EXTRACT(e.patient_ref, 'Patient/(.+)', 1) = p.patient_id;
# MAGIC
# MAGIC SELECT COUNT(*) AS encounter_count FROM workspace.default.fact_encounter;

# COMMAND ----------

# DBTITLE 1,Create fact_observation view
# MAGIC %sql
# MAGIC -- Fact: Clinical Observations and Measurements
# MAGIC CREATE OR REPLACE VIEW workspace.default.fact_observation AS
# MAGIC SELECT
# MAGIC     o.observation_id,
# MAGIC     o.patient_ref,
# MAGIC     REGEXP_EXTRACT(o.patient_ref, 'Patient/(.+)', 1) AS patient_id,
# MAGIC     o.encounter_ref,
# MAGIC     REGEXP_EXTRACT(o.encounter_ref, 'Encounter/(.+)', 1) AS encounter_id,
# MAGIC     p.full_name AS patient_name,
# MAGIC     p.gender,
# MAGIC     p.age,
# MAGIC     o.status,
# MAGIC     o.category_code,
# MAGIC     o.observation_code,
# MAGIC     o.display AS observation_display,
# MAGIC     o.value_quantity,
# MAGIC     o.unit,
# MAGIC     o.effective_date,
# MAGIC     o.extraction_timestamp
# MAGIC FROM workspace.default.silver_observation o
# MAGIC LEFT JOIN workspace.default.dim_patient p
# MAGIC   ON REGEXP_EXTRACT(o.patient_ref, 'Patient/(.+)', 1) = p.patient_id;
# MAGIC
# MAGIC SELECT COUNT(*) AS observation_count FROM workspace.default.fact_observation;

# COMMAND ----------

# DBTITLE 1,Create fact_condition view
# MAGIC %sql
# MAGIC -- Fact: Patient Conditions and Diagnoses
# MAGIC CREATE OR REPLACE VIEW workspace.default.fact_condition AS
# MAGIC SELECT
# MAGIC     c.condition_id,
# MAGIC     c.patient_ref,
# MAGIC     REGEXP_EXTRACT(c.patient_ref, 'Patient/(.+)', 1) AS patient_id,
# MAGIC     c.encounter_ref,
# MAGIC     REGEXP_EXTRACT(c.encounter_ref, 'Encounter/(.+)', 1) AS encounter_id,
# MAGIC     p.full_name AS patient_name,
# MAGIC     p.gender,
# MAGIC     p.age,
# MAGIC     c.clinical_status,
# MAGIC     c.verification_status,
# MAGIC     c.category_code,
# MAGIC     c.condition_code,
# MAGIC     c.condition_display,
# MAGIC     c.onset_date,
# MAGIC     c.recorded_date,
# MAGIC     c.extraction_timestamp
# MAGIC FROM workspace.default.silver_condition c
# MAGIC LEFT JOIN workspace.default.dim_patient p
# MAGIC   ON REGEXP_EXTRACT(c.patient_ref, 'Patient/(.+)', 1) = p.patient_id;
# MAGIC
# MAGIC SELECT COUNT(*) AS condition_count FROM workspace.default.fact_condition;

# COMMAND ----------

# DBTITLE 1,Create patient_summary view
# MAGIC %sql
# MAGIC -- Aggregated: Patient Health Summary
# MAGIC CREATE OR REPLACE VIEW workspace.default.patient_summary AS
# MAGIC SELECT
# MAGIC     p.patient_id,
# MAGIC     p.full_name,
# MAGIC     p.gender,
# MAGIC     p.age,
# MAGIC     COUNT(DISTINCT e.encounter_id) AS total_encounters,
# MAGIC     COUNT(DISTINCT o.observation_id) AS total_observations,
# MAGIC     COUNT(DISTINCT c.condition_id) AS total_conditions,
# MAGIC     MAX(e.period_start) AS last_encounter_date,
# MAGIC     MAX(o.effective_date) AS last_observation_date
# MAGIC FROM workspace.default.dim_patient p
# MAGIC LEFT JOIN workspace.default.fact_encounter e ON p.patient_id = e.patient_id
# MAGIC LEFT JOIN workspace.default.fact_observation o ON p.patient_id = o.patient_id
# MAGIC LEFT JOIN workspace.default.fact_condition c ON p.patient_id = c.patient_id
# MAGIC GROUP BY 
# MAGIC     p.patient_id,
# MAGIC     p.full_name,
# MAGIC     p.gender,
# MAGIC     p.age;
# MAGIC
# MAGIC SELECT * FROM workspace.default.patient_summary LIMIT 10;

# COMMAND ----------

# DBTITLE 1,Summary
# MAGIC %md
# MAGIC ## Gold Layer Summary
# MAGIC
# MAGIC All gold views have been created successfully!
# MAGIC
# MAGIC ### Available Views:
# MAGIC 1. **dim_patient** - Patient dimension
# MAGIC 2. **fact_encounter** - Encounter facts
# MAGIC 3. **fact_observation** - Observation facts
# MAGIC 4. **fact_condition** - Condition facts
# MAGIC 5. **patient_summary** - Aggregated patient metrics
# MAGIC
# MAGIC ### Usage Examples:
# MAGIC ```sql
# MAGIC -- Get all encounters for a specific patient
# MAGIC SELECT * FROM workspace.default.fact_encounter
# MAGIC WHERE patient_id = 'your-patient-id';
# MAGIC
# MAGIC -- Top 10 most common conditions
# MAGIC SELECT condition_display, COUNT(*) as count
# MAGIC FROM workspace.default.fact_condition
# MAGIC GROUP BY condition_display
# MAGIC ORDER BY count DESC
# MAGIC LIMIT 10;
# MAGIC
# MAGIC -- Patient encounter statistics by gender
# MAGIC SELECT gender, 
# MAGIC        AVG(total_encounters) as avg_encounters,
# MAGIC        AVG(total_observations) as avg_observations
# MAGIC FROM workspace.default.patient_summary
# MAGIC GROUP BY gender;
# MAGIC ```