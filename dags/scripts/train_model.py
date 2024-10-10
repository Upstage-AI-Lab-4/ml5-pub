from dags.scripts.preprocess import features
from dags.scripts.load_model import save_model
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from dags.scripts.preprocess import preprocess_data
from app import knn_model, data, train_data_path, kmeans_model_path

def train_model():
    preprocess_data(data, knn_model)

    # CSV로 저장 (경로 수정)
    data.to_csv(train_data_path, index=False)
    save_model(knn_model, kmeans_model_path)