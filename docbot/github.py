import requests


class GitHub:
    def __init__(self, token: str) -> None:
        self.token: str = token

    def send_comment(self, body, issue_api, to):
        # create_event(to, 'send_comment', body)
        body = {'body': '@{}: {}'.format(to, body)}
        url = '{}/comments'.format(issue_api)
        status_code = self._send_request(url, body)
        print('Sent comment: {}'.format(status_code))

    def get_comments(self, issue_api) -> dict:
        body = {'since': '1970-01-01T00:00:00Z'}
        url = '{}/comments'.format(issue_api)
        r = self._send_request(url, body, method='get')
        return r.json()

    def create_issue(self, title, description, src_url, author, doc_repo_url):
        # create_event(author, 'create_issue', title)
        description = '{}\nRequested by @{} in {}.'.format(description, author,
                                                           src_url)
        body = {'title': title, 'body': description}
        url = '{}/issues'.format(doc_repo_url)
        status_code = self._send_request(url, body)
        print('Created issue: {}'.format(status_code))

    def _send_request(self, url, body, method='post'):
        headers = {
            'Authorization': 'token {}'.format(self.token),
        }
        r = requests.request(method, url, json=body, headers=headers)
        print(r.status_code)
        r.raise_for_status()
        return r
