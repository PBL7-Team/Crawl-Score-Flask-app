FROM python:3.11-slim

WORKDIR /flask-app

COPY Crawler_Here/ Model_Here/ .env.sample app.py requirements.txt //flask-app/
COPY Crawler_Here/ /api-flask/Crawler_Here/
COPY Model_Here/ /flask-app/Model_Here/
COPY .env.sample app.py requirements.txt  /flask-app/

RUN mv /flask-app/.env.sample /flask-app/.env

RUN pip install torch==1.11.1 torchvision==0.17.2 torchaudio==1.11.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080", "-w", "4"]