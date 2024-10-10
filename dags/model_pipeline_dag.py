# import sys
# import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
<<<<<<< HEAD
from scripts.load_model import load_or_train_model
=======
# 현재 파일의 경로를 기준으로 scripts 폴더 추가
# sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

<<<<<<< HEAD
from scripts.load_model import load_or_train_model
=======
from scripts.load_model import load_model
from scripts.spotify_api import Spotify_Weekly_Chart, Get_Info
>>>>>>> c1d4903f95677dc58b50363ed2b5ddebd6c6040f
>>>>>>> origin/josungsu


def train_model():
    # 모델 훈련 및 MLflow 로깅
<<<<<<< HEAD
    load_or_train_model()
=======
<<<<<<< HEAD
    load_or_train_model()
=======
    load_model()
>>>>>>> c1d4903f95677dc58b50363ed2b5ddebd6c6040f
>>>>>>> origin/josungsu
    
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

<<<<<<< HEAD
t1 >> t2
=======
<<<<<<< HEAD
    t2 = PythonOperator(
        task_id='fetch_new_data',
        python_callable=fetch_new_data,
    )

    t1 >> t2
=======
    t2 = DockerOperator(
        task_id='fetch_spotify_data',
        image='mlops-spotify_api',  # 빌드된 도커 이미지 이름
        auto_remove=True,
        command="python /app/dags/script/spotify_api.py",  # 스크립트를 실행하는 명령어
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge'
    )

t2 >> t1
>>>>>>> c1d4903f95677dc58b50363ed2b5ddebd6c6040f
>>>>>>> origin/josungsu
