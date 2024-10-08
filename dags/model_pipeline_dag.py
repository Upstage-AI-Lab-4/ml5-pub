# import sys
# import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
# 현재 파일의 경로를 기준으로 scripts 폴더 추가
# sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.load_model import load_or_train_model


def train_model():
    # 모델 훈련 및 MLflow 로깅
    load_or_train_model()
    
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

    t2 = PythonOperator(
        task_id='fetch_new_data',
        python_callable=fetch_new_data,
    )

t1 >> t2