from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import subprocess
import time

def train_model():
    subprocess.run(['python', '/opt/airflow/scripts/model.py'])

def fetch_new_data():
    print("Fetching new data... (currently a placeholder)")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 1),
    'retries': 1,
}

with DAG(
    'model_pipeline',
    default_args=default_args,
    description='A simple model training and serving DAG',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    t1 = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
    )

    t3 = PythonOperator(
        task_id='fetch_new_data',
        python_callable=fetch_new_data,
    )

    t1 >> t3