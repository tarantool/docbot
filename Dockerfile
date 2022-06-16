FROM python:3.10.4-alpine

COPY requirements.txt /tmp
RUN pip install --upgrade pip --no-cache-dir && \
    pip install -r tmp/requirements.txt --no-cache-dir

COPY docbot /app/docbot

ENV PORT=5000
EXPOSE 5000

WORKDIR /app
CMD gunicorn --bind 0.0.0.0:$PORT docbot.app:app
