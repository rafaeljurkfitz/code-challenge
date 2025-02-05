from airflow.datasets import Dataset
from airflow.decorators import dag, task
from pendulum import datetime
from docker.types import Mount
from airflow.providers.docker.operators.docker import DockerOperator


@dag(
    start_date=datetime(2025, 2, 4),
    schedule="@daily",
    catchup=True,
    default_args={"owner": "Astro", "retries": 3},
    tags=["meltano"],
)
def extract_csv_meltano():
   
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
        entrypoint=""
    )
    def create_output_csv(date: str = "{{ds}}"):
        import os
        output_data_directory = f"/project/output/data/csv/{date}"
        os.makedirs(output_data_directory, exist_ok=True)
        print(f"Nova pasta criada para CSV: {date}")
      
    extract_csv = DockerOperator(
        task_id="extract_csv",
        api_version='auto',
        auto_remove='force',
        image='meltano-demo-project:dev',
        docker_url='tcp://host.docker.internal:2375',
        mount_tmp_dir=False,
        environment={"MELTANO_AIRFLOW_TIMESTAMP": "{{ ds }}"},
        working_dir="/project",
        network_mode='bridge',
        mounts=[Mount(source="data_inicial_pipeline", target="/project/data", type="volume"),
               Mount(source="dataset_filesystem", target="/project/output/data", type="volume")
               ],
        entrypoint="meltano run tap-csv target-duckdb",
        outlets=[Dataset("csv_file:dataset_filesystem")]
    )
    
    create_output_csv("{{ds}}") >> extract_csv
   
extract_csv_meltano()
