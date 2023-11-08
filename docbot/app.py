import logging

from elasticapm.contrib.flask import ElasticAPM
from prometheus_flask_exporter import PrometheusMetrics
from flask import Flask, request

from .handlers import webhook_handler, list_events_handler
from .logging_config import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)

log = logging.getLogger(__name__)


app = Flask(__name__)

app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': 'docbot',
}
apm = ElasticAPM(app, logging=True)

metrics = PrometheusMetrics(app, group_by='endpoint')

@app.route("/", methods=['GET'])
@metrics.do_not_track()
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
    extra = {
        'X-GitHub-Delivery': request.headers.get('X-GitHub-Delivery')
    }
    log.info('Accepted webhook from GitHub service', extra=extra)
    return webhook_handler(data, event, extra)
