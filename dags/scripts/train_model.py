from dags.scripts.preprocess import features
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from sklearn.preprocessing import StandardScaler
from dags.scripts.preprocess import preprocess_data
from app import knn_model, data, train_data_path, kmeans_model_path

def train_model():
    preprocess_data(data, knn_model)

    # CSV로 저장 (경로 수정)
    data.to_csv(train_data_path, index=False)
    # 모델 저장
    with open(kmeans_model_path, 'wb') as f:
        pickle.dump(knn_model, f)
    print(f">>> Model saved at {kmeans_model_path}")