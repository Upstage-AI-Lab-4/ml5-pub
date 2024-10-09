from fastapi import FastAPI
<<<<<<< HEAD
from dags.scripts.load_model import load_or_train_model
from dags.scripts.model import KMeans
import pandas as pd
from tabulate import tabulate
=======
# from dags.scripts.load_model import load_or_train_model
from dags.scripts.model import KMeans
import pandas as pd
import sklearn
import pickle
>>>>>>> c1d4903f95677dc58b50363ed2b5ddebd6c6040f

app = FastAPI()

# 글로벌 모델과 스케일러 로드
<<<<<<< HEAD
kmeans_model, data = load_or_train_model()
=======
kmeans_model_path = "/app/dags/model/kmeans_model.pkl"
knn_model_path = "/app/dags/model/knn_model.pkl"
train_data_path = "/app/dags/data/train.csv"

with open(knn_model_path, 'rb') as file:
    knn_model = pickle.load(file)
data = pd.read_csv(train_data_path)
>>>>>>> c1d4903f95677dc58b50363ed2b5ddebd6c6040f

@app.post("/recommend")
def recommend_songs(song_name: str):
    if not song_name.strip():
        return {"error": "Song name cannot be empty."}
    
    # 추천 실행
<<<<<<< HEAD
    kmeans_setting = KMeans(song_name, kmeans_model, data)
    recommended_songs = kmeans_setting.recommend_songs_by_knn(top_n=10)
=======
    recommend = KMeans(song_name, knn_model, data)
    recommended_songs = recommend.recommend_songs_by_knn()
>>>>>>> c1d4903f95677dc58b50363ed2b5ddebd6c6040f
    
    if recommended_songs is not None:
        print("Recommended tracks:")
        print(tabulate(recommended_songs, 
                    headers=['track_name', 'artist_name', 'release_year', 'final_score', 'cluster'],
                    tablefmt='psql', showindex=False))