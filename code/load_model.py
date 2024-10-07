import pickle
import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from code.preprocess import preprocess, features
# import mlflow
# import mlflow.sklearn 
from datetime import datetime


# 모델을 로드하거나 새로 학습하는 함수
def load_or_train_model():
    kmeans_model_path = "model/kmeans_model.pkl"
    knn_model_path = "model/knn_model.pkl"
    train_data_path = "data/train.csv"
    
    # mlflow.set_tracking_uri("http://127.0.0.1:5001")
    
    # 모델과 스케일러 로드
    if os.path.exists(kmeans_model_path) and os.path.exists(knn_model_path):
        with open(kmeans_model_path, 'rb') as f:
            kmeans_model = pickle.load(f)
        with open(knn_model_path, 'rb') as f:
            knn_model = pickle.load(f)
            
        data = pd.read_csv(train_data_path)
        print(">>> Models loaded.")
    else:
        # mlflow.autolog()
        
        print(">>> Training models and scaler...")
        raw_data = pd.read_csv("data/spotify_songs.csv")
        data = raw_data.dropna(subset=['track_name'])

        # 데이터 전처리 및 스케일링
        X, scaler = preprocess(data)
        # mlflow.log_param("num_features", len(features))

        # KMeans 학습 및 저장 (별도의 start_run 필요 없음)
        kmeans_model = KMeans(n_clusters=3, random_state=42)
        kmeans_model.fit(X)
        # mlflow.sklearn.log_model(kmeans_model, "kmeans_model")
        with open(kmeans_model_path, 'wb') as f:
            pickle.dump(kmeans_model, f)
        
        # KNN 학습 및 저장
        knn_model = NearestNeighbors(n_neighbors=30)
        knn_model.fit(X)
        # mlflow.sklearn.log_model(knn_model, "knn_model")
        with open(knn_model_path, 'wb') as f:
            pickle.dump(knn_model, f)
        
        data.to_csv("data/train.csv", index=False)
        print(">>> Models saved.")
    
    return kmeans_model, knn_model, data
