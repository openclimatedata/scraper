import subprocess

subprocess.run([
    "python",
    "scripts/process.py"
], cwd="paris-agreement-entry-into-force")

subprocess.run([
    "python",
    "scripts/process.py"
], cwd="doha-amendment-entry-into-force")


subprocess.run([
    "csvs-to-sqlite",
    "--replace-tables",
    ("paris-agreement-entry-into-force/data/"
     "paris-agreement-entry-into-force.csv"),
    ("doha-amendment-entry-into-force/data/"
     "doha-amendment.csv"),
    "data.sqlite"
])
