import logging

from . import settings
from .github import GitHub
from .utils import create_event


log = logging.getLogger(__name__)

github = GitHub(settings.token)


def parse_comment(body):
    if not body.startswith(settings.bot_name):
        return None, None
    offset = len(settings.bot_name)
    for dr in settings.doc_requests:
        if body.startswith(dr, offset):
            offset += len(dr)
            break
    else:
        return None, 'Invalid request type.'
    if not body.startswith(settings.title_header, offset):
        return None, 'Title not found.'
    offset += len(settings.title_header)
    pos = body.find('\n', offset)
    if pos == -1:
        pos = len(body)
    return {'title': body[offset:pos],
            'description': body[pos:]}, None


def process_issue_comment(body, issue_state, issue_api, extra) -> str:
    action = body['action']
    if (action != 'created' and action != 'edited') or \
       issue_state != 'open':
        log.info('Not needed', extra=extra)
        return 'Not needed.'
    comment = body['comment']
    author = comment['user']['login']
    comment, error = parse_comment(comment['body'])
    if error:
        log.error('Error during request processing: %s', error, extra=extra)
        github.send_comment(error, issue_api, author, extra)
    elif comment:
        log.info('Request is processed ok', extra=extra)
        if action == 'edited':
            github.send_comment('Accept edited.', issue_api, author, extra)
        else:
            github.send_comment('Accept.', issue_api, author, extra)
    else:
        log.debug('Ignore non-request comments', extra=extra)
    log.info('Doc request is processed', extra=extra)
    return 'Doc request is processed.'


def process_issue_state_change(body, issue_api, issue_url, doc_repo_url, extra):
    action = body['action']
    if action != 'closed':
        log.info('Not needed', extra=extra)
        return 'Not needed.'
    comments = github.get_comments(issue_api, extra)
    for c in comments:
        comment, error = parse_comment(c['body'])
        if error:
            log.error('Error during request processing: %s', error, extra=extra)
        if comment:
            github.create_issue(comment["title"], comment["description"],
                                issue_url, c['user']['login'], doc_repo_url, extra)
    log.info('Issue %s is processed', comment["title"], extra=extra)
    return 'Issue is processed.'


def process_commit(c, is_master_push, doc_repo_url, extra):
    body = c['message']
    request_pos = body.find(settings.bot_name)
    if request_pos == -1:
        return
    request = body[request_pos:]
    author = c['author']['username']
    comment, error = parse_comment(request)
    if error:
        log.error('Error during request processing: %s', error, extra=extra)
        create_event(author, 'process_commit', error)
    else:
        create_event(author, 'process_commit', 'Accept')
        if is_master_push:
            log.info(
                'Trying to create issue on Github %s', comment['title'], extra=extra
            )
            github.create_issue(comment['title'],
                                comment['description'], c['url'],
                                author, doc_repo_url, extra)
