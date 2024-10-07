import mlflow
from sklearn.preprocessing import StandardScaler

features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']

# 데이터 전처리 및 스케일링 함수
def preprocess(data):
    X = data[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    mlflow.log_param("scaler", scaler)

    return X_scaled, scaler