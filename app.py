from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from dags.scripts.SongResponse import RecommendationItem, RecommendationResponse
from dags.scripts.model import KMeans
from dags.scripts.load_model_data import load_kmeans_model, load_data

app = FastAPI()

# 글로벌 모델과 스케일러 로드
kmeans_model_path = "./dags/model/kmeans_model.pkl"
train_data_path = "./dags/data/train.csv"
backup_data_path = "./dags/data/spotify_songs.csv"  # 백업 경로 추가

# Load model and data
kmeans_model = load_kmeans_model(kmeans_model_path)
data = load_data(train_data_path, backup_data_path)

@app.get("/recommend", response_model=RecommendationResponse)
def recommend_songs(song_name: str = Query(..., description="Enter the song name to get recommendations")):
    if not song_name.strip():
        return JSONResponse(content={"error": "Song name cannot be empty."}, status_code=400)
    
    # 추천 실행
    recommend = KMeans(song_name, kmeans_model, data)
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
