FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]