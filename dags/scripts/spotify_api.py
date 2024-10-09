import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from requests.exceptions import HTTPError
from spotipy.exceptions import SpotifyException
import threading
import pandas as pd
import numpy as np
import ast
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
# from dotenv import load_dotenv
import os


# 스포티파이 api키 입력
# load_dotenv()
client_id = '9138c9fe66ce41dfa7ab1b83ecf6f650'
client_secret = '9521407805044cb7a9573a36519197c1'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



# 스포티파이 위클리 차트 csv파일 저장
class Spotify_Weekly_Chart:
    def __init__(self, countries, download_directory="/app/dags/data/spotify_charts/"): #다운로드 경로는 도커 만들고나서 절대경로로 설정해야함
        self.countries = countries
        self.download_directory = download_directory
        self.options = Options()
        self.options.binary_location = '/usr/bin/chromium'  # Chromium 실행 파일 경로 지정
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-extensions")
        self.options.add_experimental_option("prefs", {
            "download.default_directory": self.download_directory,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        self.driver = None

    def download_charts(self, username, password):
        service = Service('/usr/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=self.options)
        self.driver.get("https://charts.spotify.com/charts/view/regional-global-weekly/latest")

        # 쿠키 배너 처리
        try:
            cookie_banner = self.driver.find_element(By.ID, 'onetrust-policy-text')
            if cookie_banner:
                self.driver.execute_script("arguments[0].style.display = 'none';", cookie_banner)
                print("Policy text hidden.")
        except Exception as e:
            print(f"Policy text not found or already hidden: {e}")

        try:
            self.driver.execute_script("document.getElementById('onetrust-policy-text').style.display = 'none';")
            print("Policy text hidden.")
        except Exception as e:
            print(f"Policy text not found or already hidden: {e}")

        # 로그인 하기
        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Log in'))
        )
        login_button.click()

        id_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'login-username'))
        )
        id_input.send_keys(username)

        password_input = self.driver.find_element(By.ID, 'login-password')
        password_input.send_keys(password)

        login_button = self.driver.find_element(By.ID, 'login-button')
        login_button.click()

        #로그인 후 로딩대기
        WebDriverWait(self.driver, 20).until(
            EC.url_contains('charts.spotify.com/charts')
        )

        before_files = set(os.listdir(self.download_directory)) #변경 전 파일이름들 확인

        #나라별 200차트 다운로드
        for country in self.countries:
            self.driver.get(f"https://charts.spotify.com/charts/view/regional-{country}-weekly/latest")
            time.sleep(2) # 다운로드 버튼 로딩 대기
            
            try:
                csv_download_button = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-labelledby='csv_download']"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", csv_download_button)
                self.driver.execute_script("arguments[0].click();", csv_download_button)
                print("CSV download button clicked.")
                time.sleep(2)
            except Exception as e:
                print(f"Error clicking CSV download button: {e}")

        # 크롬 셀레늄 끝내기
        if self.driver:
            self.driver.quit()

        #이전파일과 비교해 업데이트된 파일 찾기
        after_files = set(os.listdir(self.download_directory))
        new_files = after_files - before_files
        new_files = list(new_files)

        # 업데이트된 파일들 합치고 저장하기
        new_chart = []
        for file in new_files:
            df = pd.read_csv(f'{self.download_directory + file}')
            new_chart.append(df)

        combined_chart = pd.concat(new_chart, ignore_index=True)
        combined_chart['id'] = combined_chart['uri'].str.split(':').str[2]
        file_name = new_files[0].split('-')[3:]
        file_name = ''.join(file_name[:-1]) + file_name[-1]
        combined_chart.to_csv(f'{self.download_directory}combined_{file_name}', index=False)

        #중복 삭제후 추가된곡만 저장
        exist_songs = pd.read_csv('/app/dags/data/spotify_songs.csv') #도커 올리고 나서 경로수정 해야함
        exist_id = set(exist_songs['track_id'])
        new_songs = combined_chart[~combined_chart['id'].isin(exist_id)]
        new_songs.to_csv('/app/dags/data/new_songs.csv', index=False) #도커 올리고 나서 경로수정 해야함




# Rate limit에 맞추어 요청 수 제한
class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            current_time = time.time()
            # 기간 내의 호출만 남김
            self.calls = [call for call in self.calls if current_time - call < self.period]
            if len(self.calls) >= self.max_calls:
                # 기간이 끝날 때까지 대기
                sleep_time = self.period - (current_time - self.calls[0])
                print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
                # 대기 후 호출 리스트 갱신
                self.calls = [call for call in self.calls if time.time() - call < self.period]
            # 호출 기록 추가
            self.calls.append(time.time())



# 새로운 위클리차트 기반으로 데이터베이스 업데이트 #방화벽 열어주기
class Get_Info:
    def __init__(self):
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.ids= pd.read_csv('/app/dags/data/new_songs.csv')['id'].tolist() #도커 올리고 나서 경로수정 해야함
        self.rate_limiter = RateLimiter(max_calls=5, period=30)

    def chunk_ids(self, chunk_size):
        """IDs를 chunk_size 크기로 분할하는 제너레이터 함수"""
        for i in range(0, len(self.ids), chunk_size):
            yield self.ids[i:i + chunk_size]
    
    def get_audio_features(self):
        audio_features = []
        id_chunks = list(self.chunk_ids(100))
        total_chunks = len(id_chunks)
        for idx, chunk in enumerate(id_chunks):
            self.rate_limiter.acquire()  # 호출 전에 RateLimiter를 통해 제한 관리
            try:
                features = self.sp.audio_features(chunk)
                print(f"Response for chunk {idx+1}/{total_chunks}: {features}")
                if features is not None:
                    audio_features.extend(features)
                else:
                    print(f"Chunk {idx+1}/{total_chunks}: Received None for features.")
                print(f"Chunk {idx+1}/{total_chunks} processed.")
            except Exception as e:
                print(f"Error fetching audio features for chunk {idx+1}/{total_chunks}: {e}")
        print(f"Total audio features fetched: {len(audio_features)}")
        return audio_features
    
    def get_track_info(self):
        track_info = []
        id_chunks = list(self.chunk_ids(50))
        total_chunks = len(id_chunks)
        for idx, chunk in enumerate(id_chunks):
            self.rate_limiter.acquire()  # 호출 전에 RateLimiter를 통해 제한 관리
            try:
                response = self.sp.tracks(chunk)
                print(f"Response for chunk {idx+1}/{total_chunks}: {response}")
                if response is not None:
                    track_info.extend(response['tracks'])
                else:
                    print(f"Chunk {idx+1}/{total_chunks}: Received None for features.")
                print(f"Chunk {idx+1}/{total_chunks} processed.")
            except Exception as e:
                print(f"Error fetching track_info for chunk {idx+1}/{total_chunks}: {e}")
        print(f"Total audio features fetched: {len(track_info)}")
        return track_info
    
    def fetch(self):
        df = pd.read_csv('/app/dags/data/spotify_songs.csv')
        new_songs = pd.read_csv('/app/dags/data/new_songs.csv')

        if new_songs.empty:
            print('신곡이 없읍니다')
            return
        else:
            audio_features = self.get_audio_features()
            features = pd.DataFrame(audio_features)
            print(features.head())

            track_infos = self.get_track_info()
            infos = pd.DataFrame(track_infos)
            print(infos.head())

            # infos['artists'] = infos['artists'].apply(ast.literal_eval)
            # infos['album'] = infos['album'].apply(ast.literal_eval)    #필요없는듯?

            infos['track_artist'] = infos['artists'].apply(lambda x: ', '.join([artist['name'] for artist in x]))
            infos['track_album_id'] = infos['album'].apply(lambda x: x['id'])
            infos['track_album_name'] = infos['album'].apply(lambda x: x['name'])
            infos['track_album_release_date'] = infos['album'].apply(lambda x: x['release_date'])

            features.rename(columns={'id': 'track_id'}, inplace=True)
            infos.rename(columns={'id': 'track_id', 'name': 'track_name', 'popularity': 'track_popularity'}, inplace=True)

            # 필요한거 골라서 합치기
            df1_selected = features[['track_id', 'danceability', 'energy', 'key', 'loudness', 'mode',
                                'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                                'valence', 'tempo', 'duration_ms']]

            df2_selected = infos[['track_id', 'track_name', 'track_artist', 'track_popularity',
                                'track_album_id', 'track_album_name', 'track_album_release_date']]

            df_combined = pd.merge(df1_selected, df2_selected, on='track_id', how='inner')

            # 순서 맞추기
            if 'Unnamed: 0' in df.columns:
                df = df.drop(columns=['Unnamed: 0'])
            df_combined = df_combined[df.columns]

            # 원본 뒤에 붙이고 저장하기
            df_merged = pd.concat([df, df_combined], ignore_index=True)
            df_merged.drop_duplicates(subset='track_id', inplace=True)
            df_merged.to_csv('/app/dags/data/spotify_songs.csv', index=False)


# 위 클래스들 사용법

# 위클리차트 업데이트
countries = ['kr', 'us', 'global']
downloader = Spotify_Weekly_Chart(countries)
downloader.download_charts('sejin_kwon@naver.com', 'qykfab-5reZqu-pafhug') #아이디, 패스워드 입력

# 업데이트한 차트 기반으로 데이터베이스 업데이트
spotify_api = Get_Info()
spotify_api.fetch()