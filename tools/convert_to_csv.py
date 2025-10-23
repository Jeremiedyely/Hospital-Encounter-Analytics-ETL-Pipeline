
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "output"

def to_csv(txt_path: Path):
    csv_path = txt_path.with_suffix(".csv")
    df = pd.read_csv(txt_path)
    df.to_csv(csv_path, index=False)

def main():
    for p in OUT.glob("*.txt"):
        to_csv(p)

if __name__ == "__main__":
    main()
