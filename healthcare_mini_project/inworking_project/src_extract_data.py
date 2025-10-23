#extract stage

import pandas as pd
import sqlite3

DB_PATH = "data/hospital.db"

with sqlite3.connect(DB_PATH) as conn:
    patients   = pd.read_sql("SELECT * FROM patients", conn)
    providers  = pd.read_sql("SELECT * FROM providers", conn)
    encounters = pd.read_sql("SELECT * FROM encounters", conn)
    diagnoses  = pd.read_sql("SELECT * FROM diagnoses", conn)
    procedures = pd.read_sql("SELECT * FROM procedures", conn)

#transform stage
