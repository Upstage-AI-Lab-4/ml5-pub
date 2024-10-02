import subprocess
import os
import zipfile

def loader():
    # Kaggle dataset 다운로드 명령어 실행
    try:
        download_path = '../data'
        os.makedirs(download_path, exist_ok=True)
        
        print("Downloading 30000-spotify-songs dataset...")
        subprocess.run(['kaggle', 'datasets', 'download', '-d', 'joebeachcapital/30000-spotify-songs', '-p', download_path], check=True)
        
        print("Downloading spotifyclassification dataset...")
        subprocess.run(['kaggle', 'datasets', 'download', '-d', 'geomack/spotifyclassification', '-p', download_path], check=True)
        
        print("Download complete.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during download: {e}")
    finally:
        unzip()
        
def unzip():
    # 현재 작업 디렉토리 경로를 가져옴
    data_dir = '../data'
    os.makedirs(data_dir, exist_ok=True)

    # 현재 디렉토리 내의 모든 파일을 검색
    for file_name in os.listdir(data_dir):
        # 확장자가 .zip인 파일만 처리
        if file_name.endswith('.zip'):
            # 파일 경로 생성
            zip_file_path = os.path.join(data_dir, file_name)

            # zip 파일을 열고 압축 해제
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(data_dir)

            print(f"'{zip_file_path}'가 '{data_dir}'로 압축 해제되었습니다.")