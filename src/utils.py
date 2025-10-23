
from __future__ import annotations
from typing import Dict, Any
import pandas as pd
import numpy as np

# Simple constants to demonstrate variables & data types
ABN_SYS_HIGH: int = 140
ABN_SYS_LOW: int = 90
ABN_DIA_HIGH: int = 90
ABN_DIA_LOW: int = 60
ABN_HR_HIGH: int = 100
ABN_HR_LOW: int = 50

def calc_bmi(height_cm: float, weight_kg: float) -> float:
    """Body Mass Index = kg / m^2"""
    if height_cm is None or weight_kg is None or height_cm <= 0:
        return float("nan")
    h_m = height_cm / 100.0
    return float(weight_kg) / float(h_m * h_m)

def flag_abnormal_vitals(sbp: float, dbp: float, hr: float) -> Dict[str, bool]:
    """Return boolean flags for abnormal vitals."""
    flags = {
        "abn_sbp": False,
        "abn_dbp": False,
        "abn_hr": False,
        "abn_any": False
    }
    if pd.notna(sbp):
        flags["abn_sbp"] = (sbp >= ABN_SYS_HIGH) or (sbp <= ABN_SYS_LOW)
    if pd.notna(dbp):
        flags["abn_dbp"] = (dbp >= ABN_DIA_HIGH) or (dbp <= ABN_DIA_LOW)
    if pd.notna(hr):
        flags["abn_hr"]  = (hr >= ABN_HR_HIGH) or (hr <= ABN_HR_LOW)
    flags["abn_any"] = any(flags.values())
    return flags

def zscore_outliers(series: pd.Series, zcut: float = 2.5) -> pd.Series:
    """Return boolean mask for outliers using z-score cutoff."""
    mu = series.mean()
    sd = series.std(ddof=0)
    if sd == 0 or sd != sd:
        return pd.Series([False] * len(series), index=series.index)
    z = (series - mu) / sd
    return (z.abs() >= zcut)

def identify_30d_readmissions(encounters: pd.DataFrame) -> pd.DataFrame:
    """
    For each patient, sort encounters by discharge time. If the next admit is within 30 days,
    mark that subsequent encounter as a readmission_30d = True.
    """
    df = encounters.copy()
    df["readmission_30d"] = False

    df = df.sort_values(["patient_id", "discharge_ts", "admit_ts"])
    # shift per patient
    df["prev_discharge"] = df.groupby("patient_id")["discharge_ts"].shift(1)
    # time delta in days
    delta_days = (df["admit_ts"] - df["prev_discharge"]).dt.total_seconds() / (60*60*24)
    df.loc[(delta_days.notna()) & (delta_days <= 30), "readmission_30d"] = True
    df = df.drop(columns=["prev_discharge"])
    return df

# Demonstrate data structures: tuple lookup & dict mapping for ICD-10 chapters
ICD10_GROUPS = {
    "A": "Certain infectious and parasitic diseases",
    "B": "Certain infectious and parasitic diseases",
    "C": "Neoplasms",
    "D": "Neoplasms / Blood disorders",
    "E": "Endocrine, nutritional and metabolic diseases",
    "F": "Mental and behavioural disorders",
    "G": "Diseases of the nervous system",
    "H": "Diseases of the eye and adnexa / ear and mastoid",
    "I": "Diseases of the circulatory system",
    "J": "Diseases of the respiratory system",
    "K": "Diseases of the digestive system",
    "L": "Diseases of the skin and subcutaneous tissue",
    "M": "Diseases of the musculoskeletal system and connective tissue",
    "N": "Diseases of the genitourinary system",
    "O": "Pregnancy, childbirth and the puerperium",
    "P": "Certain conditions originating in the perinatal period",
    "Q": "Congenital malformations, deformations and chromosomal abnormalities",
    "R": "Symptoms, signs and abnormal clinical and laboratory findings",
    "S": "Injury, poisoning and certain other consequences of external causes",
    "T": "Injury, poisoning and certain other consequences of external causes",
    "V": "External causes of morbidity and mortality",
    "W": "External causes of morbidity and mortality",
    "X": "External causes of morbidity and mortality",
    "Y": "External causes of morbidity and mortality",
    "Z": "Factors influencing health status and contact with health services"
}

def icd10_group(code: str) -> str:
    if not isinstance(code, str) or len(code) == 0:
        return "Unknown"
    first = code[0].upper()
    return ICD10_GROUPS.get(first, "Other")
