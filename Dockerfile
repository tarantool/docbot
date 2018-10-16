FROM python:2

RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

RUN pip install --upgrade pip

COPY requirements.txt /usr/src/bot
COPY tarantoolbot.py /usr/src/bot
COPY write_credentials.sh /usr/src/bot

RUN pip install -r requirements.txt

ENV PORT=5000
EXPOSE 5000

CMD gunicorn --bind 0.0.0.0:$PORT tarantoolbot:app
