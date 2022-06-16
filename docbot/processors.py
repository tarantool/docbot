from . import settings
from .github import GitHub

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


def process_issue_comment(body, issue_state, issue_api) -> str:
    action = body['action']
    if (action != 'created' and action != 'edited') or \
       issue_state != 'open':
        return 'Not needed.'
    comment = body['comment']
    author = comment['user']['login']
    comment, error = parse_comment(comment['body'])
    if error:
        print('Error during request processing: {}'.format(error))
        github.send_comment(error, issue_api, author)
    elif comment:
        print('Request is processed ok')
        if action == 'edited':
            github.send_comment('Accept edited.', issue_api, author)
        else:
            github.send_comment('Accept.', issue_api, author)
    else:
        print('Ignore non-request comments')
    return 'Doc request is processed.'


def process_issue_state_change(body, issue_api, issue_url, doc_repo_url):
    action = body['action']
    if action != 'closed':
        return 'Not needed.'
    comments = github.get_comments(issue_api)
    for c in comments:
        comment, error = parse_comment(c['body'])
        if comment:
            github.create_issue(comment["title"], comment["description"],
                                issue_url, c['user']['login'], doc_repo_url)
    return 'Issue is processed.'


def process_commit(c, is_master_push, doc_repo_url):
    body = c['message']
    request_pos = body.find(settings.bot_name)
    if request_pos == -1:
        return
    request = body[request_pos:]
    author = c['author']['username']
    comment, error = parse_comment(request)
    if error:
        print('Error during request processing: {}'.format(error))
        # create_event(author, 'process_commit', error)
    else:
        # create_event(author, 'process_commit', 'Accept')
        if is_master_push:
            github.create_issue(doc_repo_url, comment['title'],
                                comment['description'], c['url'], author)
