import mlflow
import mlflow.sklearn
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime
import numpy as np
import pytz

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment(experiment_name = "music_recommendation")

# 데이터 전처리 및 스케일링 함수
def preprocess_data(data, model):
    mlflow.sklearn.autolog()   
    with mlflow.start_run(run_name=f"kmeans_{datetime.now(KST).strftime('%Y-%m-%d_%H-%M-%S')}"):

        mlflow.log_params({
            "model_type": "KMeans",
            "n_clusters": model.n_clusters,
            "init": model.init,
            "max_iter": model.max_iter,
            "random_state": model.random_state
        })        
        data['duration_minutes'] = data['duration_ms'] // 60000  # 분
        data['duration_seconds'] = (data['duration_ms'] % 60000) // 1000  # 초

        # 분과 초를 결합하여 mm:ss 형식으로 변환
        data['duration_formatted'] = data.apply(
            lambda x: f"{int(x['duration_minutes'])}:{int(x['duration_seconds']):02}", axis=1
        )
        data = data.drop(['duration_minutes', 'duration_seconds'], axis=1)
        # Check if 'track_name_lower' column exists before creating it
        if 'track_name_lower' not in data.columns:
            # Convert 'track_name' to lowercase
            data['track_name_lower'] = data['track_name'].str.lower()
            
            # Handle NaN values by replacing with empty strings
            data['track_name_lower'] = data['track_name_lower'].fillna('')
        
        scaler = StandardScaler()

        # 수치형 특성 정규화
        data[features] = scaler.fit_transform(data[features])
        
        # Convert 'track_album_release_date' to datetime format if it exists
        if 'release_year' not in data.columns:
            # Convert 'track_album_release_date' to a date format
            data['track_album_release_date'] = pd.to_datetime(data['track_album_release_date'], format='%Y-%m-%d', errors='coerce')

            # Extract the minimum release year from 'track_album_release_date'
            min_release_year = data['track_album_release_date'].min().year

            # Create 'release_year' column by filling NaN with the minimum release year
            data['release_year'] = data['track_album_release_date'].dt.year.fillna(min_release_year).astype(int)
        
        if 'cluster' not in data.columns:
            # K-means 클러스터링
            data['cluster'] = model.predict(data[features])

        mlflow.log_metric("number_of_rows", len(data))
        mlflow.log_metric("number_of_features", len(features))
        mlflow.log_metric("number_of_clusters", model.n_clusters)

         # KMeans 모델의 각 클러스터 중심 좌표 로깅
        for i, center in enumerate(model.cluster_centers_):
            mlflow.log_metric(f"cluster_{i}_center", np.linalg.norm(center))

        # mlflow.sklearn.log_model(model, "model")

    return data, model