import logging

from elasticapm.contrib.flask import ElasticAPM
from prometheus_flask_exporter import PrometheusMetrics
from flask import Flask, Response, request
from flask_httpauth import HTTPTokenAuth

from .handlers import webhook_handler, list_events_handler
from .logging_config import LOGGING_CONFIG
from .utils import is_verified_signature, is_verified_prometheus_token


logging.config.dictConfig(LOGGING_CONFIG)

log = logging.getLogger(__name__)


app = Flask(__name__)
auth = HTTPTokenAuth()

app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': 'docbot',
}
apm = ElasticAPM(app, logging=True)

metrics = PrometheusMetrics(app, group_by='endpoint', metrics_decorator=auth.login_required)


@auth.verify_token
def verify_token(token):
    return is_verified_prometheus_token(token)

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
    if not is_verified_signature(
        request.data,
        request.headers.get('X-Hub-Signature-256', None)
    ):
        return Response(status=403)
    data: dict = request.json
    event: str = request.headers.get('X-GitHub-Event')
    extra = {
        'X-GitHub-Delivery': request.headers.get('X-GitHub-Delivery')
    }
    log.info('Accepted webhook from GitHub service', extra=extra)
    return webhook_handler(data, event, extra)
