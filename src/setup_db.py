
import sqlite3, random
from pathlib import Path
from datetime import datetime, timedelta
import math

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "hospital.db"

random.seed(42)

def rand_date(start_year=2021, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days),
                             hours=random.randint(0, 23),
                             minutes=random.randint(0, 59))

def create_tables(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        dob TEXT,
        sex TEXT,
        height_cm REAL,
        weight_kg REAL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS providers (
        provider_id INTEGER PRIMARY KEY,
        npi TEXT,
        name TEXT,
        specialty TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS encounters (
        encounter_id INTEGER PRIMARY KEY,
        patient_id INTEGER,
        provider_id INTEGER,
        admit_ts TEXT,
        discharge_ts TEXT,
        admit_type TEXT,
        discharge_disposition TEXT,
        total_cost REAL,
        systolic_bp REAL,
        diastolic_bp REAL,
        heart_rate REAL,
        FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY(provider_id) REFERENCES providers(provider_id)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS diagnoses (
        encounter_id INTEGER,
        icd10 TEXT,
        description TEXT,
        dx_rank INTEGER,
        FOREIGN KEY(encounter_id) REFERENCES encounters(encounter_id)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS procedures (
        encounter_id INTEGER,
        cpt TEXT,
        description TEXT,
        proc_cost REAL,
        FOREIGN KEY(encounter_id) REFERENCES encounters(encounter_id)
    )""")

def seed_patients(cur, n=500):
    fnames = ["Alex","Sam","Taylor","Jordan","Casey","Riley","Avery","Jamie","Morgan","Chris"]
    lnames = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Lopez","Wilson"]
    for pid in range(1, n+1):
        first = random.choice(fnames)
        last = random.choice(lnames)
        # DOB between 1940 and 2015
        year = random.randint(1940, 2015)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        dob = f"{year:04d}-{month:02d}-{day:02d}"
        sex = random.choice(["F","M"])
        height_cm = round(random.gauss(168 if sex=="F" else 178, 7), 1)
        weight_kg = round(random.gauss(72 if sex=="F" else 84, 12), 1)
        cur.execute("""INSERT INTO patients(patient_id, first_name, last_name, dob, sex, height_cm, weight_kg)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (pid, first, last, dob, sex, height_cm, weight_kg))

def seed_providers(cur, n=50):
    specs = ["Internal Medicine","Cardiology","Pulmonology","Endocrinology","Orthopedics",
             "Emergency","Surgery","Family Medicine","Neurology","Pediatrics"]
    for pr in range(1, n+1):
        npi = "".join([str(random.randint(0,9)) for _ in range(10)])
        name = f"Dr. Provider {pr}"
        specialty = random.choice(specs)
        cur.execute("""INSERT INTO providers(provider_id, npi, name, specialty)
                       VALUES (?, ?, ?, ?)""", (pr, npi, name, specialty))

def seed_encounters(cur, n=2000, patient_n=500, provider_n=50):
    admit_types = ["ED","Elective","Urgent","Newborn"]
    dispositions = ["Home","SNF","Rehab","Expired","AMA"]
    for eid in range(1, n+1):
        pid = random.randint(1, patient_n)
        pr = random.randint(1, provider_n)
        admit = rand_date(2022, 2024)
        los_days = max(0, int(random.gauss(3, 2)))
        discharge = admit + timedelta(days=los_days, hours=random.randint(0,12))
        total_cost = max(200, random.gauss(6500, 3500))
        sbp = max(70, random.gauss(128, 20))
        dbp = max(40, random.gauss(78, 12))
        hr  = max(35, random.gauss(82, 18))
        cur.execute("""INSERT INTO encounters(encounter_id, patient_id, provider_id, admit_ts, discharge_ts,
                    admit_type, discharge_disposition, total_cost, systolic_bp, diastolic_bp, heart_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (eid, pid, pr, admit.isoformat(sep=" "), discharge.isoformat(sep=" "),
                     random.choice(admit_types), random.choice(dispositions),
                     round(total_cost, 2), round(sbp,1), round(dbp,1), round(hr,1)))

def seed_diagnoses(cur, encounter_n=2000):
    # Skew distribution: common codes appear more
    common = [
        ("I10","Essential (primary) hypertension"),
        ("E11.9","Type 2 diabetes mellitus without complications"),
        ("J18.9","Pneumonia, unspecified organism"),
        ("J44.1","COPD with (acute) exacerbation"),
        ("I50.9","Heart failure, unspecified"),
        ("K21.9","Gastro-esophageal reflux disease without esophagitis"),
        ("R07.9","Chest pain, unspecified"),
        ("N39.0","Urinary tract infection, site not specified"),
        ("M54.5","Low back pain"),
        ("R55","Syncope and collapse"),
    ]
    rare = [
        ("C34.90","Malignant neoplasm of unspecified part of unspecified bronchus or lung"),
        ("G40.909","Epilepsy, unspecified, not intractable, without status epilepticus"),
        ("D64.9","Anemia, unspecified"),
        ("E03.9","Hypothyroidism, unspecified"),
        ("K52.9","Noninfective gastroenteritis and colitis, unspecified"),
        ("L03.90","Cellulitis, unspecified"),
        ("A41.9","Sepsis, unspecified organism"),
        ("I63.9","Cerebral infarction, unspecified"),
        ("J45.901","Unspecified asthma with (acute) exacerbation")
    ]
    # generate 1-3 diagnosis rows per encounter, rank 1 is primary
    for eid in range(1, encounter_n+1):
        k = random.choices([1,2,3], weights=[0.6,0.3,0.1])[0]
        # primary more likely from common
        for rank in range(1, k+1):
            if rank == 1:
                code, desc = random.choice(common if random.random()<0.85 else rare)
            else:
                pool = common + rare
                code, desc = random.choice(pool)
            cur.execute("""INSERT INTO diagnoses(encounter_id, icd10, description, dx_rank)
                           VALUES (?, ?, ?, ?)""", (eid, code, desc, rank))

def seed_procedures(cur, encounter_n=2000):
    procs = [
        ("71020","Chest X-ray", 200),
        ("93000","Electrocardiogram", 120),
        ("99284","ED visit, moderate", 450),
        ("99285","ED visit, high severity", 700),
        ("45378","Colonoscopy", 2200),
        ("70450","Head CT", 1800),
        ("80053","Comprehensive metabolic panel", 65),
        ("85025","Complete blood count", 40),
        ("93010","EKG interpretation", 40),
    ]
    for eid in range(1, encounter_n+1):
        k = random.choices([0,1,2], weights=[0.15,0.6,0.25])[0]
        for _ in range(k):
            cpt, desc, cost = random.choice(procs)
            # allow some variability
            pcost = round(max(10, random.gauss(cost, cost*0.15)), 2)
            cur.execute("""INSERT INTO procedures(encounter_id, cpt, description, proc_cost)
                           VALUES (?, ?, ?, ?)""", (eid, cpt, desc, pcost))

def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    create_tables(cur)
    seed_patients(cur, n=500)
    seed_providers(cur, n=50)
    seed_encounters(cur, n=2000)
    seed_diagnoses(cur, encounter_n=2000)
    seed_procedures(cur, encounter_n=2000)
    con.commit()
    con.close()

if __name__ == "__main__":
    main()
