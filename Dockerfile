FROM python:3.9-slim
LABEL org.opencontainers.image.source="https://github.com/xjasonlyu/avdc-api"

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt

ENV HTTP_PROXY=""
ENV HTTPS_PROXY=""

ENV AVDC_DATABASE=""
ENV AVDC_TOKEN=""

ENV GOOGLE_APPLICATION_CREDENTIALS="/key.json"

ENV PORT=5000
ENTRYPOINT exec python -m main -p $PORT
