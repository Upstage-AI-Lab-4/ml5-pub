from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from scripts.load_model import load_or_train_model


def train_model():
    # 여기에 train_model.py 함수사용해야함.
    pass
    
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
        task_id='fetch_new_data',
        python_callable=fetch_new_data,
    )
    
    t2 = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
    )


t1 >> t2