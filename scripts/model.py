import numpy as np
from scripts.preprocess import features
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from datetime import datetime

class KMeans():
    def init(self, song_name, model, data):
        self.song_name = song_name
        self.model = model
        self.data = data
        self.scaler = StandardScaler()
    
    def preprocess_data(self):
        # track_name을 소문자로 변환
        self.data['track_name_lower'] = self.data['track_name'].str.lower()
        
        # 수치형 특성 정규화
        self.data[features] = self.scaler.fit_transform(self.data[features])
        
        # TF-IDF 벡터화 (소문자로 변환된 track_name 사용)
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(self.data['track_name_lower'])
        
        # K-means 클러스터링
        self.data['cluster'] = self.model.predict(self.data[features])
        
        # 클러스터 중심 계산
        cluster_centers = self.model.cluster_centers_
        
        return tfidf, tfidf_matrix, cluster_centers

    def find_similar_tracks(self, tfidf, tfidf_matrix):
        input_track_lower = self.song_name.lower()
        input_tfidf = tfidf.transform([input_track_lower])
        cosine_sim = cosine_similarity(input_tfidf, tfidf_matrix).flatten()
        sim_scores = list(enumerate(cosine_sim))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        return sim_scores

    def calculate_cluster_distance(self, track_features, cluster_centers):
        distances = np.linalg.norm(cluster_centers - track_features, axis=1)
        return 1 - (distances / np.max(distances))  # 정규화된 거리 점수

    def recommend_songs_by_knn(self, top_n=10):
        tfidf, tfidf_matrix, cluster_centers = self.preprocess_data()
        sim_scores = self.find_similar_tracks(tfidf, tfidf_matrix)
        most_similar_idx = sim_scores[1][0]
        reference_track = self.data.iloc[most_similar_idx]
        
        current_year = datetime.now().year
        
        self.data['year_score'] = 1 - (current_year - self.data['release_year']) / (current_year - self.data['release_year'].min())
        self.data['popularity_score'] = self.data['track_popularity'] / 100
        
        content_similarity = cosine_similarity([reference_track[features]], self.data[features])
        self.data['content_score'] = content_similarity[0]
        
        # 클러스터 거리 점수 계산
        reference_features = self.scaler.transform(reference_track[features].values.reshape(1, -1))
        cluster_distances = self.calculate_cluster_distance(reference_features, cluster_centers)
        self.data['cluster_score'] = cluster_distances[self.data['cluster']]
        
        # 최종 점수 계산 (클러스터 점수 포함)
        self.data['final_score'] = (self.data['content_score'] * 0.4 + 
                            self.data['year_score'] * 0.2 + 
                            self.data['popularity_score'] * 0.2 +
                            self.data['cluster_score'] * 0.2)
        
        self.data = self.data[self.data.index != most_similar_idx]
        self.data = self.data.drop_duplicates(subset=['track_name', 'track_artist'])
        
        recommended = self.data.nlargest(top_n, 'final_score')
        
        return recommended[['track_name', 'track_artist', 'release_year', 'final_score', 'cluster']]

# def recommend_songs_by_knn(song_name, knn_model, data):
#     # song_name에 해당하는 노래의 피처를 찾아 예측에 사용
#     song_row = data[data['track_name'] == song_name]
    
#     if song_row.empty:
#         # 정확한 노래가 없을 경우, 유사한 노래 찾기
#         song_row = find_most_similar_song(song_name, data)
#         print(f">>> Closest match: {song_row['track_name']} by {song_row['track_artist']}")
    
#     # 노래의 피처 벡터 추출
#     song_features = song_row[features].values
#     song_features_reshaped = song_features.reshape(1, -1)
    
#     # KNN으로 가장 가까운 노래 30개 추천
#     distances, indices = knn_model.kneighbors(song_features_reshaped)
    
#     # 디버깅 출력: 인덱스와 반환된 거리 정보 확인
#     print(f">>> KNN distances: {distances}")
#     print(f">>> KNN indices: {indices}")
    
#     # 반환된 인덱스 검증 (유효 범위 내의 인덱스만 사용)
#     valid_indices = [i for i in indices[0] if i < len(data)]
#     if not valid_indices:
#         print(f">>> No valid indices found for song: {song_name}")
#         return {"message": "No valid recommendations found."}
    
#     # 유효한 인덱스에 해당하는 추천 노래 반환
#     recommended_songs = data.iloc[valid_indices]
    
#     return recommended_songs[['track_name', 'track_artist']].head(30)
