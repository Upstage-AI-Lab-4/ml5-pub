import streamlit as st
import requests
import urllib.parse
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# YouTube API 설정 (API 키를 .env 파일에서 가져오기)
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# YouTube 검색 함수
def get_youtube_video_id(song_name, artist_name):
    search_query = f"{song_name} {artist_name} official"
    query = urllib.parse.quote(search_query)
    
    # YouTube Data API 검색 URL 생성
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={YOUTUBE_API_KEY}"
    
    # API 요청 보내기
    response = requests.get(url)
    
    # 요청이 성공했는지 확인
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            # 첫 번째 검색 결과의 동영상 ID를 반환
            video_id = data['items'][0]['id']['videoId']
            return video_id
        else:
            return None
    else:
        st.error(f"Error fetching YouTube video ID: {response.status_code}")
        return None

# Streamlit 페이지 구성
st.title('Music Recommendation System')

# 사용자 입력 받기
song_name = st.text_input('Enter a song name:', '')

# 추천 노래 목록을 저장할 리스트
recommended_songs = []

# 버튼을 클릭했을 때 추천 결과 가져오기
if st.button('Recommend'):
    if song_name:
        # FastAPI의 추천 API 호출 (GET 방식으로 변경)
        url = f"http://127.0.0.1:8000/recommend?song_name={urllib.parse.quote(song_name)}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # HTTPError 발생 시 처리
            
            # 추천 노래 목록 파싱
            recommended_songs = response.json().get('recommendations', [])
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching recommendations: {e}")

# 추천된 노래 목록 출력 및 유튜브 동영상 삽입
if recommended_songs:
    st.subheader(f'Recommended Songs for "{song_name}":')
    
    for song in recommended_songs:
        track_name = song.get('track_name')
        track_artist = song.get('track_artist')
        
        # YouTube 동영상 ID 가져오기
        video_id = get_youtube_video_id(track_name, track_artist)
        
        if video_id:
            # 유튜브 동영상 삽입
            st.write(f'**{track_name}** by *{track_artist}*')
            st.video(f"https://www.youtube.com/embed/{video_id}")
        else:
            st.write(f"No YouTube video found for {track_name} by {track_artist}")