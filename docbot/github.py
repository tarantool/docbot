import logging

import requests

from .metrics import Metrics
from .utils import create_event


log = logging.getLogger(__name__)


class GitHub:
    def __init__(self, token: str) -> None:
        self.token: str = token

    def send_comment(self, body, issue_api, to, extra):
        create_event(to, 'send_comment', body)
        body = {'body': '@{}: {}'.format(to, body)}
        url = '{}/comments'.format(issue_api)
        self._send_request(url, body)
        log.info('Sent comment', extra=extra)

    def get_comments(self, issue_api, extra) -> dict:
        body = {'since': '1970-01-01T00:00:00Z'}
        url = '{}/comments'.format(issue_api)
        r = self._send_request(url, body, method='get')
        log.info('Received comments', extra=extra)
        return r.json()

    def create_issue(self, title, description, src_url, author, doc_repo_url, extra):
        create_event(author, 'create_issue', title)
        description = '{}\nRequested by @{} in {}.'.format(description, author,
                                                           src_url)
        body = {'title': title, 'body': description}
        url = '{}/issues'.format(doc_repo_url)
        self._send_request(url, body)
        log.info('Created issue', extra=extra)

    @Metrics.github_latency.time()
    def _send_request(self, url, body, method='post'):
        headers = {
            'Authorization': 'token {}'.format(self.token),
        }
        r = requests.request(method, url, json=body, headers=headers)
        log.info('Response status code: %s', r.status_code)
        r.raise_for_status()
        return r
