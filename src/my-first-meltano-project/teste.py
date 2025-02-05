import os
import subprocess

os.environ["MELTANO_AIRFLOW_TIMESTAMP"] = "2025-02-03"
os.environ["MELTANO_AIRFLOW_TABLE"] = "categories"

env = os.environ.copy()

result = subprocess.run(["meltano", "run", "tap-postgres", "target-duckdb-postgres"], env=env, text=True,  capture_output=True)

print(result)

