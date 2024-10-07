FROM continuumio/miniconda3

# MLflow 설치
RUN pip install mlflow

# 디렉토리 생성 및 권한 설정
RUN mkdir -p /mlflow/db

# 환경 변수 설정
ENV MLFLOW_TRACKING_URI=http://0.0.0.0:5000
ENV MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow/db/mlflow.db

# 컨테이너 실행 시 MLflow 서버 실행
ENTRYPOINT ["mlflow", "server"]
CMD ["--host", "0.0.0.0", "--port", "5000", "--backend-store-uri", "sqlite:///mlflow/db/mlflow.db"]

# docker build -t custom-mlflow .

# docker run -d -p 5001:5000 --name mlflow-test \
# -v $(pwd)/mlflow/db:/mlflow/db \
# -v $(pwd)/mlartifacts:/mlartifacts \
# custom-mlflow