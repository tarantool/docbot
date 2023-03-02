from elasticapm.contrib.flask import ElasticAPM
from prometheus_flask_exporter import PrometheusMetrics
from flask import Flask, request

from .handlers import webhook_handler, list_events_handler


app = Flask(__name__)

app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': 'docbot',
}
apm = ElasticAPM(app)

metrics = PrometheusMetrics(app)

@app.route("/", methods=['GET'])
def index() -> str:
    return list_events_handler()


@app.route("/", methods=['POST'])
@metrics.summary(
    name='events',
    description='Summary of event from the GitHub service',
    labels={'event': lambda: request.headers.get('X-GitHub-Event', None)}
)
def webhook() -> str:
    data: dict = request.json
    event: str = request.headers.get('X-GitHub-Event')
    return webhook_handler(data, event)
