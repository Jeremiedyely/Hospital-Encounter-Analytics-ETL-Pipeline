
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from utils import calc_bmi, flag_abnormal_vitals, zscore_outliers, identify_30d_readmissions, icd10_group

BASE = Path(__file__).resolve().parents[1]
DB_PATH = BASE / "data" / "hospital.db"
OUT_DIR = BASE / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_tables():
    con = sqlite3.connect(DB_PATH)
    patients = pd.read_sql_query("SELECT * FROM patients", con, parse_dates=["dob"])
    providers = pd.read_sql_query("SELECT * FROM providers", con)
    encounters = pd.read_sql_query("SELECT * FROM encounters", con, parse_dates=["admit_ts","discharge_ts"])
    diagnoses = pd.read_sql_query("SELECT * FROM diagnoses", con)
    procedures = pd.read_sql_query("SELECT * FROM procedures", con)
    con.close()
    return patients, providers, encounters, diagnoses, procedures

def transform(patients, providers, encounters, diagnoses, procedures):
    # BMI on patients
    patients["bmi"] = patients.apply(lambda r: round(calc_bmi(r["height_cm"], r["weight_kg"]), 1), axis=1)

    # Keep primary diagnosis
    primary_dx = diagnoses.sort_values(["encounter_id","dx_rank"]).drop_duplicates("encounter_id", keep="first")
    primary_dx["dx_group"] = primary_dx["icd10"].apply(icd10_group)

    # Abnormal vitals flags
    abn = encounters.apply(lambda r: pd.Series(flag_abnormal_vitals(r["systolic_bp"], r["diastolic_bp"], r["heart_rate"])), axis=1)
    encounters = pd.concat([encounters, abn], axis=1)

    # 30-day readmissions
    encounters = identify_30d_readmissions(encounters)

    # Cost outliers via z-score
    encounters["cost_outlier"] = zscore_outliers(encounters["total_cost"], zcut=2.5)

    # Join
    joined = (encounters
              .merge(patients[["patient_id","sex","dob","height_cm","weight_kg","bmi"]], on="patient_id", how="left")
              .merge(providers[["provider_id","specialty"]], on="provider_id", how="left")
              .merge(primary_dx[["encounter_id","icd10","description","dx_group"]], on="encounter_id", how="left")
    )

    # Derived fields
    joined["age_at_admit"] = (joined["admit_ts"].dt.date - joined["dob"].dt.date).apply(lambda d: d.days/365.25)
    joined["age_at_admit"] = joined["age_at_admit"].round(1)

    # Columns order
    cols = [
        "encounter_id","patient_id","provider_id","admit_ts","discharge_ts","admit_type","discharge_disposition",
        "total_cost","cost_outlier",
        "systolic_bp","diastolic_bp","heart_rate","abn_sbp","abn_dbp","abn_hr","abn_any",
        "sex","dob","age_at_admit","height_cm","weight_kg","bmi",
        "specialty","icd10","description","dx_group","readmission_30d"
    ]
    joined = joined[cols]
    return joined

def make_reports(joined, diagnoses, procedures):
    # Top diagnoses (by primary code)
    top_dx = (joined["icd10"]
              .value_counts()
              .reset_index()
              .rename(columns={"index":"icd10","icd10":"count"}))
    top_dx = top_dx.merge(joined[["icd10","description"]].drop_duplicates(), on="icd10", how="left")

    # Utilization by specialty and admit_type
    util = (joined.groupby(["specialty","admit_type"])
            .size()
            .reset_index(name="encounters"))

    # Cost outliers details
    outliers = joined.loc[joined["cost_outlier"]].copy()
    outliers = outliers.sort_values("total_cost", ascending=False)

    # Dx group distribution
    dx_group = (joined.groupby("dx_group").size().reset_index(name="encounters")
                .sort_values("encounters", ascending=False))

    # Simple procedure spend summary (not primary deliverable but helpful)
    proc_spend = procedures.groupby("description", as_index=False)["proc_cost"].sum().sort_values("proc_cost", ascending=False)

    return {
        "top_diagnoses": top_dx,
        "utilization": util,
        "cost_outliers": outliers,
        "dx_group_distribution": dx_group,
        "procedure_spend": proc_spend
    }

def save_txt(df: pd.DataFrame, path: Path):
    # Save as CSV-formatted text with .txt extension
    df.to_csv(path, index=False)

def load_stage(joined, reports):
    # Main cleaned dataset
    save_txt(joined, OUT_DIR / "cleaned_encounters.txt")
    # Reports
    save_txt(reports["top_diagnoses"], OUT_DIR / "report_top_diagnoses.txt")
    save_txt(reports["utilization"], OUT_DIR / "report_utilization.txt")
    save_txt(reports["cost_outliers"], OUT_DIR / "report_cost_outliers.txt")
    save_txt(reports["dx_group_distribution"], OUT_DIR / "report_dx_group_distribution.txt")
    save_txt(reports["procedure_spend"], OUT_DIR / "report_procedure_spend.txt")

def main():
    patients, providers, encounters, diagnoses, procedures = extract_tables()
    joined = transform(patients, providers, encounters, diagnoses, procedures)
    reports = make_reports(joined, diagnoses, procedures)
    load_stage(joined, reports)

if __name__ == "__main__":
    main()
