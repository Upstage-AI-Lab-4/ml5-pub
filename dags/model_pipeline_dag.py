from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
from scripts.train_model import train_model

def retrain_model():
    # 모델 훈련 및 MLflow 로깅
    train_model()
    
# def fetch_new_data():
#     try:
#         countries = ['kr', 'us', 'global']
#         downloader = Spotify_Weekly_Chart(countries)
#         downloader.download_charts('sejin_kwon@naver.com', 'qykfab-5reZqu-pafhug')

#         spotify_api = Get_Info()
#         spotify_api.fetch()
    
#     except Exception as e:
#         print(f"Error in fetch_new_data: {e}, Probably no new songs updated in the chart")
#         raise



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
    max_active_runs=1,
) as dag:

    t1 = DockerOperator(
        task_id='fetch_spotify_data',
        image='ml-project-mlops_5-spotify_api',  # 빌드된 도커 이미지 이름
        auto_remove=True,
        command="python /app/dags/scripts/spotify_api.py",  # 스크립트를 실행하는 명령어
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge',
        mount_tmp_dir=False

    )

    t2 = PythonOperator(
        task_id='retrain_model',
        python_callable=retrain_model,
    )
t1 >> t2