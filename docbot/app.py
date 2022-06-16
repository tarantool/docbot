import os

from elasticapm.contrib.flask import ElasticAPM
from flask import Flask, request

from .handlers import webhook_handler, list_events_handler

app = Flask(__name__)

app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': 'docbot2',
}
apm = ElasticAPM(app)


@app.route("/", methods=['GET'])
def index() -> str:
    return list_events_handler()


@app.route("/", methods=['POST'])
def webhook() -> str:
    data: dict = request.json
    event: str = request.headers.get('X-GitHub-Event')
    return webhook_handler(data, event)
