from airflow.datasets import Dataset
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from pendulum import datetime
from docker.types import Mount
import os

                     
POSTGRES_TABLES = [ 'categories',
                    'customer_customer_demo',
                    'customer_demographics',
                    'customers',
                    'employees', 
                    'employee_territories',
                    'orders',
                    'products',
                    'region', 
                    'shippers', 
                    'suppliers', 
                    'territories',
                    'us_states']

dataset_csv = Dataset("csv_file:dataset_filesystem")
dataset_postgres_tables = Dataset("pg_tables:dataset_filesystem")

@dag(
    start_date=datetime(2025, 2, 4),
    schedule=[dataset_csv, dataset_postgres_tables],
    catchup=True,
    default_args={"owner": "Astro", "retries": 3},
    tags=["meltano"],
)
def load_meltano():
    t0 = EmptyOperator(task_id='start')
    
    @task.docker(
        api_version='auto',
        auto_remove='force',
        docker_url='tcp://host.docker.internal:2375',
        image='meltano-demo-project:dev',
        network_mode='bridge',
        mount_tmp_dir=False,
        environment={
            "TARGET_POSTGRES_DATABASE": os.environ['TARGET_POSTGRES_DATABASE'],
            "TARGET_POSTGRES_PORT":os.environ['TARGET_POSTGRES_PORT'],
            "TARGET_POSTGRES_HOST":os.environ['TARGET_POSTGRES_HOST'],
            "TARGET_POSTGRES_USER":os.environ['TARGET_POSTGRES_USER'],
            "TARGET_POSTGRES_PASSWORD":os.environ['TARGET_POSTGRES_PASSWORD']},
        working_dir="/project",
        mounts=[Mount(source="data_inicial_pipeline", target="/project/data", type="volume"),
            Mount(source="dataset_filesystem", target="/project/output/data", type="volume")
            ],
        entrypoint=""
    )
    def tdm_csv(date: str):
        import os
        import subprocess
        
        os.environ["MELTANO_AIRFLOW_TIMESTAMP"] = date

        env = os.environ.copy()
        
        result = subprocess.run(["meltano", "run", "tap-duckdb", "target-postgres"], env=env, text=True)
        
        if result.returncode == 1:
            raise Exception("Failed to completed load data csv")
        
    
    t1 = tdm_csv(date="{{ds}}")
    
    @task.docker(
        api_version='auto',
        auto_remove='force',
        image='meltano-demo-project:dev',
        docker_url='tcp://host.docker.internal:2375',
        mount_tmp_dir=False,
        environment={
            "TARGET_POSTGRES_DATABASE": os.environ['TARGET_POSTGRES_DATABASE'],
            "TARGET_POSTGRES_PORT":os.environ['TARGET_POSTGRES_PORT'],
            "TARGET_POSTGRES_HOST":os.environ['TARGET_POSTGRES_HOST'],
            "TARGET_POSTGRES_USER":os.environ['TARGET_POSTGRES_USER'],
            "TARGET_POSTGRES_PASSWORD":os.environ['TARGET_POSTGRES_PASSWORD']},
        working_dir="/project",
        network_mode='bridge',
        mounts=[Mount(source="data_inicial_pipeline", target="/project/data", type="volume"),
            Mount(source="dataset_filesystem", target="/project/output/data", type="volume")
            ],
        entrypoint="",
    )
    def tdm_postgres(date: str, table: str):
        import os
        import subprocess
        
        os.environ["MELTANO_AIRFLOW_TIMESTAMP"] = date
        os.environ["MELTANO_AIRFLOW_TABLE"] = table

        env = os.environ.copy()
        
        result = subprocess.run(["meltano", "run", f"tap-csv-postgres-{table}", "target-postgres"], env=env, text=True)
        
        if result.returncode == 1:
            raise Exception("Failed to completed load data postgres")
        
    t2 = tdm_postgres.partial(date="{{ds}}").expand(table=POSTGRES_TABLES)
    
    t3 = EmptyOperator(task_id='end')
    
    t0 >> [t1, t2] >> t3
   
load_meltano()
