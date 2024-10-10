from fastapi import FastAPI
# from dags.scripts.load_model import load_or_train_model
from fastapi.responses import JSONResponse
from dags.scripts.SongResponse import RecommendationItem, RecommendationResponse
from dags.scripts.model import KMeans
import pandas as pd
import numpy as np
import os
import sklearn
import pickle

app = FastAPI()

# 글로벌 모델과 스케일러 로드
kmeans_model_path = "/app/dags/model/kmeans_model.pkl"
train_data_path = "/app/dags/data/train.csv"
backup_data_path = "/app/dags/data/spotify_songs.csv"  # 백업 경로 추가

# KMeans 모델 로드
with open(kmeans_model_path, 'rb') as file:
    knn_model = pickle.load(file)

# 데이터 경로 확인 및 데이터 로드
if os.path.exists(train_data_path):
    data = pd.read_csv(train_data_path)
else:
    print(f"{train_data_path} not found. Loading from {backup_data_path}")
    data = pd.read_csv(backup_data_path)

@app.post("/recommend", response_model=RecommendationResponse)
def recommend_songs(song_name: str):
    if not song_name.strip():
        return JSONResponse(content={"error": "Song name cannot be empty."}, status_code=400)
    
    # 추천 실행
    recommend = KMeans(song_name, knn_model, data)
    recommended_songs = recommend.recommend_songs_by_knn()

    
    if recommended_songs is not None:
        recommendations = [
            RecommendationItem(
                track_name=str(row['track_name']),
                track_artist=str(row['track_artist']),
                release_year=int(row['release_year']),
                final_score=float(row['final_score'])
            )
            for row in recommended_songs  # 리스트이므로 iterrows()가 필요 없음
        ]
        return RecommendationResponse(recommendations=recommendations)
    else:
        return JSONResponse(content={"error": "No recommendations found"}, status_code=404)
    