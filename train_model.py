from dags.scripts.preprocess import features
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler


def train_model(data, model):
    # track_name을 소문자로 변환
    data['track_name_lower'] = data['track_name'].str.lower()
    
    # 수치형 특성 정규화
    scaler = StandardScaler()
    data[features] = scaler.fit_transform(data[features])
        
    # TF-IDF 벡터화 (소문자로 변환된 track_name 사용)
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['track_name_lower'])
        
    # K-means 클러스터링
    data['cluster'] = model.predict(data[features])
        
    # 클러스터 중심 계산
    cluster_centers = model.cluster_centers_

    # CSV로 저장 (경로 수정)
    data.to_csv(r'dags/train_data.csv', index=False)
        
    return tfidf, tfidf_matrix, cluster_centers