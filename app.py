from fastapi import FastAPI, HTTPException
from dags.scripts.SongInput import SongInput
from dags.scripts.model import KMeans
from dags.scripts.load_model import load_model

app = FastAPI()

# 글로벌 모델과 스케일러 로드
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