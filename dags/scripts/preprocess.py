from sklearn.preprocessing import StandardScaler
import pandas as pd

features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']

# 데이터 전처리 및 스케일링 함수
def preprocess_data(data, model):
    data['duration_minutes'] = data['duration_ms'] // 60000  # 분
    data['duration_seconds'] = (data['duration_ms'] % 60000) // 1000  # 초

    # 분과 초를 결합하여 mm:ss 형식으로 변환
    data['duration_formatted'] = data.apply(
        lambda x: f"{int(x['duration_minutes'])}:{int(x['duration_seconds']):02}", axis=1
    )
    data = data.drop(['duration_minutes', 'duration_seconds'], axis=1)
    # track_name을 소문자로 변환
    data['track_name_lower'] = data['track_name'].str.lower()
    
    # NaN 값 처리: NaN 값을 빈 문자열로 대체
    data['track_name_lower'] = data['track_name_lower'].fillna('')
    
    scaler = StandardScaler()

    # 수치형 특성 정규화
    data[features] = scaler.fit_transform(data[features])
    
    # K-means 클러스터링
    data['cluster'] = model.predict(data[features])
    
    # 1. track_album_release_date를 날짜 형식으로 변환
    data['track_album_release_date'] = pd.to_datetime(data['track_album_release_date'], format='%Y-%m-%d', errors='coerce')

    # 2. 년도만 추출하고, NaT 값을 처리한 후 int로 변환하여 새로운 컬럼 'release_year'로 저장
    # Find the minimum value in the 'track_album_release_date' column
    min_release_year = data['track_album_release_date'].min().year

    # Create the 'release_year' column, filling NaN with the minimum release year
    data['release_year'] = data['track_album_release_date'].dt.year.fillna(min_release_year).astype(int)
    
    return data, model