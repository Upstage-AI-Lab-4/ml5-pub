from fastapi import FastAPI
from scripts.load_model import load_or_train_model
from scripts.model import KMeans
import pandas as pd
from tabulate import tabulate

app = FastAPI()

# 글로벌 모델과 스케일러 로드
kmeans_model, data = load_or_train_model()

@app.post("/recommend")
def recommend_songs(song_name: str):
    if not song_name.strip():
        return {"error": "Song name cannot be empty."}
    
    # 추천 실행
    kmeans_setting = KMeans(song_name, kmeans_model, data)
    recommended_songs = kmeans_setting.recommend_songs_by_knn(top_n=10)
    
    if recommended_songs is not None:
        print("Recommended tracks:")
        print(tabulate(recommended_songs, 
                    headers=['track_name', 'artist_name', 'release_year', 'final_score', 'cluster'],
                    tablefmt='psql', showindex=False))