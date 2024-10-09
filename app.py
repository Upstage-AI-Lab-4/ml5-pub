from fastapi import FastAPI
# from dags.scripts.load_model import load_or_train_model
from dags.scripts.model import KMeans
import pandas as pd
import sklearn
import pickle

app = FastAPI()

# 글로벌 모델과 스케일러 로드
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
    recommend = KMeans(song_name, knn_model, data)
    recommended_songs = recommend.recommend_songs_by_knn()
    
    # recommended_songs가 dict일 경우 바로 반환
    if isinstance(recommended_songs, dict):
        return recommended_songs
    
    # recommended_songs가 DataFrame일 경우 to_dict 호출
    return {"recommendations": recommended_songs.to_dict(orient="records")}