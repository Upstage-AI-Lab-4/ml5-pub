import numpy as np
from dags.scripts.preprocess import features
from dags.scripts.load_model import save_model
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import pandas as pd

class KMeans():
    def __init__(self, song_name, model, data):
        self.song_name = song_name
        self.model = model
        self.data = data
    
    def preprocess_data(self):
        # Check if 'track_name_lower' column exists before creating it
        if 'track_name_lower' not in self.data.columns:
            # Convert 'track_name' to lowercase
            self.data['track_name_lower'] = self.data['track_name'].str.lower()
            
            # Handle NaN values by replacing with empty strings
            self.data['track_name_lower'] = self.data['track_name_lower'].fillna('')

        scaler = StandardScaler()
        
        # 수치형 특성 정규화
        self.data[features] = scaler.fit_transform(self.data[features])
        
        # TF-IDF 벡터화 (소문자로 변환된 track_name 사용)
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(self.data['track_name_lower'])
        
        # K-means 클러스터링
        self.model.fit_predict(self.data[features])
        
        # Convert 'track_album_release_date' to datetime format if it exists
        if 'release_year' not in self.data.columns:
            # Convert 'track_album_release_date' to a date format
            self.data['track_album_release_date'] = pd.to_datetime(self.data['track_album_release_date'], format='%Y-%m-%d', errors='coerce')

            # Extract the minimum release year from 'track_album_release_date'
            min_release_year = self.data['track_album_release_date'].min().year

            # Create 'release_year' column by filling NaN with the minimum release year
            self.data['release_year'] = self.data['track_album_release_date'].dt.year.fillna(min_release_year).astype(int)
        
        if 'cluster' not in self.data.columns:
            # K-means 클러스터링
            self.data['cluster'] = self.model.predict(self.data[features])
        
        # 클러스터 중심 계산
        cluster_centers = self.model.cluster_centers_
        
        return tfidf, tfidf_matrix, cluster_centers, scaler

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
        tfidf, tfidf_matrix, cluster_centers, scaler = self.preprocess_data()
        sim_scores = self.find_similar_tracks(tfidf, tfidf_matrix)
        most_similar_idx = sim_scores[1][0]
        reference_track = self.data.iloc[most_similar_idx]
        
        current_year = datetime.now().year
        
        self.data['year_score'] = 1 - (current_year - self.data['release_year']) / (current_year - self.data['release_year'].min())
        self.data['popularity_score'] = self.data['track_popularity'] / 100
        
        # Compute content similarity
        content_similarity = cosine_similarity([reference_track[features]], self.data[features])
        self.data['content_score'] = content_similarity[0]
        
        
        # We already fit scaler in preprocess_data
        reference_features = scaler.transform(reference_track[features].values.reshape(1, -1))
        
        # Compute cluster distance score
        cluster_distances = self.calculate_cluster_distance(reference_features, cluster_centers)
        self.data['cluster_score'] = cluster_distances[self.data['cluster']]
        
        # Final score calculation (including cluster score)
        self.data['final_score'] = (self.data['content_score'] * 0.4 + 
                                    self.data['year_score'] * 0.2 + 
                                    self.data['popularity_score'] * 0.2 +
                                    self.data['cluster_score'] * 0.2)
        
        # Remove the most similar track from recommendations and drop duplicates
        self.data = self.data[self.data.index != most_similar_idx]
        self.data = self.data.drop_duplicates(subset=['track_name', 'track_artist'])
        
        # Get the top N recommendations
        recommended = self.data.nlargest(top_n, 'final_score')
        
        # Convert the DataFrame rows to a list of dictionaries (JSON objects)
        recommended_json = recommended[['track_name', 'track_artist', 'release_year', 'final_score']].to_dict(orient='records')
        
        return recommended_json