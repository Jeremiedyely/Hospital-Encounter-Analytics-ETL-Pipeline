# 🏥 Healthcare ETL Mini Project — Problem Statement & Overview

## 📘 Project Title
**Hospital Encounter Analytics ETL Pipeline**

---

## 🎯 Problem Statement
A large hospital network needs a **clean, unified, and analytics-ready dataset** combining patients, providers, encounters, diagnoses, and procedures.  
Currently, this data is scattered across multiple SQL tables, making it difficult for analysts in the **Billing** and **Quality Management** teams to extract insights.

You’ve been assigned as a **junior data engineer - Jeremie Dyely** to build a **Python-based ETL pipeline** that automates this process and produces a set of summary reports.

---

## 💡 Objective
Design and implement a **5-hour hands-on ETL project** using the **pandas** library that:
1. **Extracts** mock data from a local SQLite database.
2. **Transforms** it by cleaning, joining, and enriching clinical data with calculated metrics.
3. **Loads** the cleaned data and reports into `.txt` files ready for Kaggle-style analytics.

---

## 🧠 Business Requirements
The hospital team requires:
- A combined **encounter-level dataset** including patient demographics, diagnosis info, BMI, abnormal vitals, readmission flags, and provider specialty.
- A set of text-based reports for quality and cost analytics.

**Required metrics:**
- Body Mass Index (BMI)
- Abnormal vitals (systolic/diastolic BP, heart rate)
- 30-day readmission detection
- Cost outlier identification (z-score > 2.5)
- ICD-10 diagnosis grouping by category

---

## 🏗️ ETL Stages

### 1. Extract
- Read from a **SQLite database** (`hospital.db`) containing 5 tables:
  - `patients`, `providers`, `encounters`, `diagnoses`, `procedures`
- Use `pandas.read_sql_query()` for data extraction.

### 2. Transform
- Calculate derived features (BMI, abnormal vitals, readmission, outliers).
- Join tables using patient and encounter IDs.
- Clean missing values and standardize formats.

### 3. Load
- Save the final cleaned dataset and reports as **CSV-formatted text files** under `/output`.

---

## 📂 Deliverables
```
healthcare_mini_project/
├─ data/
│  └─ hospital.db
├─ output/
│  ├─ cleaned_encounters.txt
│  ├─ report_top_diagnoses.txt
│  ├─ report_utilization.txt
│  ├─ report_cost_outliers.txt
│  ├─ report_dx_group_distribution.txt
│  └─ report_procedure_spend.txt
├─ src/
│  ├─ setup_db.py
│  ├─ etl.py
│  └─ utils.py
├─ run_all.py
└─ requirements.txt
```

---

## 📊 Generated Reports
| Report File | Description |
|--------------|--------------|
| **cleaned_encounters.txt** | Fully joined, transformed dataset with BMI, readmission, outliers |
| **report_top_diagnoses.txt** | Most common primary ICD-10 diagnoses |
| **report_utilization.txt** | Encounter counts by specialty × admit type |
| **report_cost_outliers.txt** | High/low cost outlier patients |
| **report_dx_group_distribution.txt** | Encounter counts by ICD-10 group |
| **report_procedure_spend.txt** | Total spend by procedure description |

---

## 🧩 Learning Goals
- Use **variables, data types, and data structures** (lists, dicts, sets)
- Build **reusable functions** for transformations
- Read/write **CSV-formatted text files**
- Apply **Pandas ETL concepts** from extraction to load
- Simulate a **real-world healthcare data engineering** scenario

---

## ⏱️ Estimated Time to Complete
**~5 hours total** (2 hours setup, 3 hours hands-on coding and testing)

---

## ✅ Outcome
After completing this project, you will have:
- A realistic **portfolio-ready data engineering project**
- Experience designing a pandas-based **ETL pipeline**
- A solid understanding of how healthcare data is structured and transformed for analytics
