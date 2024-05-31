FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

# ENTRYPOINT ["python3", "-m", "streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
ENTRYPOINT ["python3", "-m", "streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]