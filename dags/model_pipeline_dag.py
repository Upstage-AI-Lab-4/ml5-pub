# import sys
# import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
# 현재 파일의 경로를 기준으로 scripts 폴더 추가
# sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.load_model import load_model
from scripts.spotify_api import Spotify_Weekly_Chart, Get_Info


def train_model():
    # 모델 훈련 및 MLflow 로깅
    load_model()
    
def fetch_new_data():
    try:
        countries = ['kr', 'us', 'global']
        downloader = Spotify_Weekly_Chart(countries)
        downloader.download_charts('sejin_kwon@naver.com', 'qykfab-5reZqu-pafhug')

        spotify_api = Get_Info()
        spotify_api.fetch()
    
    except Exception as e:
        print(f"Error in fetch_new_data: {e}, Probably no new songs updated in the chart")
        raise



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
    schedule_interval='@weekly',
    catchup=False,
) as dag:

    t1 = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
    )

    t2 = DockerOperator(
        task_id='fetch_spotify_data',
        image='mlops-spotify_api',  # 빌드된 도커 이미지 이름
        auto_remove=True,
        command="python /app/dags/script/spotify_api.py",  # 스크립트를 실행하는 명령어
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge'
    )

t2 >> t1