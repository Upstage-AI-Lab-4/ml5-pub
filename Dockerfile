FROM python:3.10-slim

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libhdf5-dev \
    curl

WORKDIR /app
COPY ./app/requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY ./app /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]

# pip freeze > requirements.txt
# docker-compose build