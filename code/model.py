import numpy as np
from code.preprocess import features
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def find_most_similar_song(song_name, data):
    # TF-IDF 벡터화를 사용하여 제목 간 유사도 측정
    vectorizer = TfidfVectorizer()
    vectorizer.fit(data['track_name'])  # 데이터를 기준으로 벡터화 학습
    
    vectors = vectorizer.transform(data['track_name']).toarray()  # 기존 노래 제목들을 벡터화

    # 입력된 노래 제목을 벡터화하여 코사인 유사도 계산
    input_vector = vectorizer.transform([song_name]).toarray()  # 입력된 제목을 벡터화
    similarities = cosine_similarity(input_vector, vectors)

    # 가장 유사한 노래 인덱스 찾기
    most_similar_index = similarities.argsort()[0][-1]
    
    # 유사한 노래 반환
    return data.iloc[most_similar_index]

def recommend_songs_by_knn(song_name, knn_model, data):
    # song_name에 해당하는 노래의 피처를 찾아 예측에 사용
    song_row = data[data['track_name'] == song_name]
    
    if song_row.empty:
        # 정확한 노래가 없을 경우, 유사한 노래 찾기
        song_row = find_most_similar_song(song_name, data)
        print(f">>> Closest match: {song_row['track_name']} by {song_row['track_artist']}")
    
    # 노래의 피처 벡터 추출
    song_features = song_row[features].values
    song_features_reshaped = song_features.reshape(1, -1)
    
    # KNN으로 가장 가까운 노래 30개 추천
    distances, indices = knn_model.kneighbors(song_features_reshaped)
    
    # 디버깅 출력: 인덱스와 반환된 거리 정보 확인
    print(f">>> KNN distances: {distances}")
    print(f">>> KNN indices: {indices}")
    
    # 반환된 인덱스 검증 (유효 범위 내의 인덱스만 사용)
    valid_indices = [i for i in indices[0] if i < len(data)]
    if not valid_indices:
        print(f">>> No valid indices found for song: {song_name}")
        return {"message": "No valid recommendations found."}
    
    # 유효한 인덱스에 해당하는 추천 노래 반환
    recommended_songs = data.iloc[valid_indices]
    
    return recommended_songs[['track_name', 'track_artist']].head(30)
