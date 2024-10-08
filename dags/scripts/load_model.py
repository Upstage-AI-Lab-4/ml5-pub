import pickle
import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from scripts.preprocess import preprocess, features
import mlflow
import mlflow.sklearn
from datetime import datetime


def save_model(model, model_path):
    """모델을 파일로 저장하는 함수"""
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f">>> Model saved at {model_path}")


def load_model(model_path):
    """모델을 파일에서 로드하는 함수"""
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print(f">>> Model loaded from {model_path}")
    return model

def train_kmeans(X, features, current_time, kmeans_model_path):
    """KMeans 모델 학습 및 저장"""
    mlflow.autolog()  # autolog 활성화
    with mlflow.start_run(run_name=f"kmeans_model_{current_time}", nested=True) as run:
        print(">>> Training KMeans model...")
        kmeans_model = KMeans(n_clusters=2, random_state=42)
        kmeans_model.fit(X)
        mlflow.log_param("use_features", features)

        save_model(kmeans_model, kmeans_model_path)

    return kmeans_model


def load_or_train_model():
    """모델을 로드하거나 새로 학습하는 함수"""
    kmeans_model_path = "/usr/local/airflow/dags/model/kmeans_model.pkl"
    train_data_path = "/usr/local/airflow/dags/data/train.csv"

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment(experiment_name='music_recommendation')

    # 모든 활성화된 실행 종료
    # while mlflow.active_run():
    #     print(">>> Forcibly ending all active MLflow runs....")
    #    mlflow.end_run()

    # 이미 학습된 모델이 있는지 확인
    if os.path.exists(kmeans_model_path):
        kmeans_model = load_model(kmeans_model_path)
        data = pd.read_csv(train_data_path)
    else:
        print(">>> Training models and scaler...")

        # 현재 시간
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")

        # 데이터 로드 및 전처리
        raw_data = pd.read_csv("data/spotify_songs.csv")
        data = raw_data.dropna(subset=['track_name'])
        X, scaler = preprocess(data)

        # KMeans와 KNN 학습 및 저장
        kmeans_model = train_kmeans(X, features, current_time, kmeans_model_path)

        # 학습 데이터 저장
        data.to_csv(train_data_path, index=False)
        print(">>> Train data saved.")

    return kmeans_model, data
