FROM python:2

RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

RUN  pip install --upgrade pip
RUN pip install bottle requests

COPY tarantoolbot.py /usr/src/bot
COPY write_credentials.sh /usr/src/bot

EXPOSE 8888
