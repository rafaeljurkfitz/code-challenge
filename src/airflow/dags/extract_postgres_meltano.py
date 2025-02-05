from airflow.datasets import Dataset
from airflow.decorators import dag, task, task_group
from airflow.operators.empty import EmptyOperator
from pendulum import datetime
from docker.types import Mount
import os

POSTGRES_TABLES = ['us_states', 
                    'shippers', 
                    'region', 
                    'categories', 
                    'employees', 
                    'suppliers', 
                    'employee_territories',
                    'customer_demographics',
                    'products',
                    'territories',
                    'customer_customer_demo',
                    'customers',
                    'orders']

@dag(
    start_date=datetime(2025, 2, 4),
    schedule="@daily",
    catchup=True,
    default_args={"owner": "Astro", "retries": 3},
    tags=["meltano"],
)
def extract_postgres_meltano():
    
    t0 = EmptyOperator(task_id='start')
    
    @task_group(group_id="tap_postgres")
    def tap_posgres_meltano(extract_table: str):
        @task.docker(
            api_version='auto',
            auto_remove='force',
            docker_url='tcp://host.docker.internal:2375',
            image='meltano-demo-project:dev',
            network_mode='bridge',
            mount_tmp_dir=False,
            working_dir="/project",
            mounts=[Mount(source="data_inicial_pipeline", target="/project/data", type="volume"),
                Mount(source="dataset_filesystem", target="/project/output/data", type="volume")
                ],
            entrypoint="",
        )
        def create_output_postgres(date: str, table: str):
            import os
            
            output_data_directory = f"/project/output/data/postgres/{table}/{date}"
            os.makedirs(output_data_directory, exist_ok=True)
            print(f"Nova pasta criada para CSV: {output_data_directory}")
        
        
        @task.docker(
            api_version='auto',
            auto_remove='force',
            image='meltano-demo-project:dev',
            docker_url='tcp://host.docker.internal:2375',
            mount_tmp_dir=False,
            environment={
                "TAP_POSTGRES_DATABASE": os.environ['TAP_POSTGRES_DATABASE'],
                "TAP_POSTGRES_PORT":os.environ['TAP_POSTGRES_PORT'],
                "TAP_POSTGRES_HOST":os.environ['TAP_POSTGRES_HOST'],
                "TAP_POSTGRES_USER":os.environ['TAP_POSTGRES_USER'],
                "TAP_POSTGRES_PASSWORD":os.environ['TAP_POSTGRES_PASSWORD']},
            working_dir="/project",
            network_mode='bridge',
            mounts=[Mount(source="data_inicial_pipeline", target="/project/data", type="volume"),
                Mount(source="dataset_filesystem", target="/project/output/data", type="volume")
                ],
            entrypoint=""
        )
        def extract_postgres(date: str, table: str):
            import os
            import subprocess
            
            os.environ["MELTANO_AIRFLOW_TIMESTAMP"] = date
            os.environ["MELTANO_AIRFLOW_TABLE"] = table

            env = os.environ.copy()
            
            result = subprocess.run(["meltano", "run", "tap-postgres", "target-csv"], env=env, text=True)
            
            if result.returncode == 1:
                raise Exception("Failed to completed load data to duckdb")
            
        create_output_postgres("{{ds}}", extract_table) >> extract_postgres("{{ds}}", extract_table)
    
    tpm_object = tap_posgres_meltano.expand(extract_table=POSTGRES_TABLES)
    
    t3 = EmptyOperator(task_id='end', outlets=[Dataset("pg_tables:dataset_filesystem")])
    
    t0 >> tpm_object >> t3
   
extract_postgres_meltano()
