FROM python:3.11-slim
USER root
WORKDIR /flask-app

COPY Crawler_Here/ Model_Here/ .env.sample app.py requirements.txt //flask-app/
COPY Crawler_Here/ /api-flask/Crawler_Here/
COPY Model_Here/ /flask-app/Model_Here/
COPY .env.sample app.py requirements.txt  /flask-app/
COPY entrypoint.sh /flask-app/

RUN mv /flask-app/.env.sample /flask-app/.env

RUN pip install --upgrade pip && \
    pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

# CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080"]
ENTRYPOINT ["entrypoint.sh"]

