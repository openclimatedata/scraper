import glob
import subprocess
from pathlib import Path

# List of Data Packages to run scraper for
dps = [
    "paris-agreement-entry-into-force",
    "doha-amendment-entry-into-force",
    "kigali-amendment-entry-into-force",
    "ndcs"
]

for dp in dps:
    path = Path(dp)
    subprocess.run([
        "python",
        "scripts/process.py"
    ], cwd=dp)

output_csv_files = glob.glob("**/data/*.csv")

subprocess.run([
    "csvs-to-sqlite",
    "--replace-tables",
    *output_csv_files,
    "data.sqlite"
])
