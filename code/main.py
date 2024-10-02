from load.loader import loader
from model.model import model

def main(song_name):
    loader()
    df = model(song_name)
    if df is not None:
        print("Recommended music")
        print(df)

if __name__ =='__main__':
    # 도커파일 만들기 이전이므로 현재는 실행 이전에 pip install -r requirements.txt를 진행해주시면 됩니다.
    # 실행 : python main.py
    song_name = "Christmas"
    main(song_name)