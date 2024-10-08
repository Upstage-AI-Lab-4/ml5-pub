from fastapi import FastAPI
from dags.scripts.load_model import load_or_train_model
from dags.scripts.model import recommend_songs_by_knn
import pandas as pd

app = FastAPI()

# 글로벌 모델과 스케일러 로드
kmeans_model, knn_model, data = load_or_train_model()

@app.post("/recommend")
def recommend_songs(song_name: str):
    if not song_name.strip():
        return {"error": "Song name cannot be empty."}
    
    # 추천 실행
    recommended_songs = recommend_songs_by_knn(song_name, knn_model, data)
    
    # recommended_songs가 dict일 경우 바로 반환
    if isinstance(recommended_songs, dict):
        return recommended_songs
    
    # recommended_songs가 DataFrame일 경우 to_dict 호출
    return {"recommendations": recommended_songs.to_dict(orient="records")}