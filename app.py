from fastapi import FastAPI, HTTPException
from dags.scripts.load_model import load_or_train_model
from dags.scripts.SongInput import SongInput
from dags.scripts.model import KMeans
from dags.scripts.load_model import load_model
import pandas as pd
from tabulate import tabulate
# from dags.scripts.load_model import load_or_train_model
from dags.scripts.model import KMeans
import pandas as pd
import sklearn
import pickle

app = FastAPI()

# 글로벌 모델과 스케일러 로드
kmeans_model, data = load_or_train_model()
kmeans_model_path = "/app/dags/model/kmeans_model.pkl"
knn_model_path = "/app/dags/model/knn_model.pkl"
train_data_path = "/app/dags/data/train.csv"

with open(knn_model_path, 'rb') as file:
    knn_model = pickle.load(file)
data = pd.read_csv(train_data_path)

@app.post("/recommend")
def recommend_songs(song_name: str):
    if not song_name.strip():
        return {"error": "Song name cannot be empty."}
    
    # 추천 실행
    kmeans_setting = KMeans(song_name, kmeans_model, data)
    recommended_songs = kmeans_setting.recommend_songs_by_knn(top_n=10)
    recommend = KMeans(song_name, knn_model, data)
    recommended_songs = recommend.recommend_songs_by_knn()

    if recommended_songs is not None:
        print("Recommended tracks:")
        print(tabulate(recommended_songs, 
                    headers=['track_name', 'artist_name', 'release_year', 'final_score', 'cluster'],
                    tablefmt='psql', showindex=False))



kmeans_model, data = load_model()

@app.post("/api/v1/recommend_songs")
def recommend_songs(input: SongInput):
    song_name = input.song_name

    # KMeans 추천 시스템 인스턴스 생성
    recommender = KMeans(song_name, kmeans_model, data)

    try:
        # 추천된 노래 목록 반환
        recommendations = recommender.recommend_songs_by_knn(top_n=10)
        return recommendations.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in recommendation: {str(e)}")

