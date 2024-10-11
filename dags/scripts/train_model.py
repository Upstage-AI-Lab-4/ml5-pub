import pickle
from sklearn.preprocessing import StandardScaler
from scripts.preprocess import preprocess_data
from scripts.load_model_data import load_kmeans_model, load_data

def train_model():
    kmeans_model_path = "/app/dags/model/kmeans_model.pkl"
    train_data_path = "/app/dags/data/train.csv"
    backup_data_path = "/app/dags/data/spotify_songs.csv"
    
    kmeans_model = load_kmeans_model(kmeans_model_path)
    data = load_data(train_data_path, backup_data_path)

    preprocess_data(data, kmeans_model)

    # CSV로 저장
    data.to_csv(train_data_path, index=False)
    # 모델 저장
    with open(kmeans_model_path, 'wb') as f:
        pickle.dump(kmeans_model, f)
    print(f">>> Model saved at {kmeans_model_path}")