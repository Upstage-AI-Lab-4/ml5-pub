import mlflow
import mlflow.sklearn
import pandas as pd
from load_model import load_or_train_model
from model import recommend_songs_by_knn

def preprocess_data(data):
    # 데이터 전처리 로직 (예: 결측치 처리)
    data = data.dropna(subset=['track_name'])
    return data

def main_pipeline(song_name: str):
    with mlflow.start_run(run_name="full_pipeline_run") as run:
        # 데이터 로드 또는 전처리
        data = pd.read_csv('data/spotify_songs.csv')  # CSV 파일 경로
        data = preprocess_data(data)
        
        # 모델 로드 또는 학습
        kmeans_model, knn_model, data = load_or_train_model()

        # 추천 실행
        recommended_songs = recommend_songs_by_knn(song_name, knn_model, data)

        # 결과 반환
        if isinstance(recommended_songs, dict):
            raise ValueError(recommended_songs.get("error", "Unknown error"))

        # 예측 결과 저장
        mlflow.log_param("number_of_predictions", len(recommended_songs))
        return recommended_songs