from .utils import last_events
from . import settings
from .processors import process_issue_comment, process_issue_state_change, \
    process_commit


def webhook_handler(data: dict, event: str) -> str:
    if event is None or data is None:
        return 'Event or data was not found'

    if 'issue' in data:
        issue = data['issue']
        if 'state' not in issue:
            return 'Event is not needed.'
        issue_state = issue['state']
        issue_api = issue['url']
        issue_url = issue['html_url']
        issue_repo = data['repository']['full_name']

        if event == 'issue_comment':
            return process_issue_comment(data, issue_state,
                                         issue_api)
        elif event == 'issues':
            doc_repo_url = settings.doc_repo_urls.get(issue_repo)
            return process_issue_state_change(data, issue_api,
                                              issue_url, doc_repo_url)
        else:
            return 'Event "{}" is not needed.'.format(event)
    elif event == 'push':
        repo = data['repository']
        branch = '/'.join(data['ref'].split('/')[2:])
        is_master_push = repo['master_branch'] == branch
        issue_repo = settings.doc_repo_urls.get(repo['full_name'])
        for c in data['commits']:
            process_commit(c, is_master_push, issue_repo)
        return 'Webhook was processed'
    else:
        return 'Event is not needed.'


def list_events_handler() -> str:
    return ('<h1>{}</h1><table border="1" cellspacing="2" ' +
            'cellpadding="2">{}</table>').format('TarantoolBot Journal',
                                                 ' '.join(last_events))
