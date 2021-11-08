from bottle import run, post, get, request, default_app
import requests
import json
import datetime
import os

doc_requests = [' document\r\n', ' document\n']
bot_name = '@TarantoolBot'
title_header = 'Title:'
doc_repo_url = 'https://api.github.com/repos/tarantool/doc'

if os.getenv('GITHUB_TOKEN'):
    token = os.getenv('GITHUB_TOKEN')
else:
    with open('credentials.json') as f:
        credentials = json.loads(f.read())
        token = credentials['GitHub']['token']

LAST_EVENTS_SIZE = 30
last_events = []

##
# Log an event at the end of the events queue. Once the queue
# reaches size LAST_EVENTS_SIZE, the oldest event is deleted.
# @param author GitHub login of the author.
# @param action What to log.
# @param body Message body.


def create_event(author, action, body):
    time = datetime.datetime.now().strftime('%b %d %H:%M:%S')
    result = '<tr>'
    result += '<td>{}</td>'.format(time)
    result += '<td>{}</td>'.format(author)
    result += '<td>{}</td>'.format(action)
    result += '<td>{}</td>'.format(body)
    result += '</tr>'
    last_events.append(result)
    if len(last_events) > LAST_EVENTS_SIZE:
        last_events.pop(0)

##
# Bot to track documentation update requests
# and open issues in doc repository with a
# specified body and title, when an issue is
# closed.
#

##
# Parse a comment content. Try to
# extract title and body.
# @param body String comment.
#
# @retval None, None - @A body is not a request.
# @retval None, not None - @A body is a request,
#         but an error occured. The second retval
#         is the error string.
# @retval not None - @A body is a well-formatted
#         request. Returned value is a dictionary
#         with 'title' and 'description'.


def parse_comment(body):
    if not body.startswith(bot_name):
        return None, None
    offset = len(bot_name)
    for dr in doc_requests:
        if body.startswith(dr, offset):
            offset += len(dr)
            break
    else:
        return None, 'Invalid request type.'
    if not body.startswith(title_header, offset):
        return None, 'Title not found.'
    offset += len(title_header)
    pos = body.find('\n', offset)
    if pos == -1:
        pos = len(body)
    return {'title': body[offset:pos],
            'description': body[pos:]}, None
##
# Send a comment to an issue. Sent comment is either
# parser error message, or notification about accepting
# a request.


def send_comment(body, issue_api, to):
    create_event(to, 'send_comment', body)
    body = {'body': '@{}: {}'.format(to, body)}
    url = '{}/comments'.format(issue_api)
    headers = {
        'Authorization': 'token {}'.format(token),
    }
    r = requests.post(url, json=body, headers=headers)
    r.raise_for_status()
    print('Sent comment: {}'.format(r.status_code))

##
# Get all the comments of an issue.


def get_comments(issue_api):
    body = {'since': '1970-01-01T00:00:00Z'}
    url = '{}/comments'.format(issue_api)
    headers = {
        'Authorization': 'token {}'.format(token),
    }
    r = requests.get(url, json=body, headers=headers)
    r.raise_for_status()
    return r.json()

##
# Open a new issue in a documentation repository.
# @param title Issue title.
# @param description Issue description.
# @param src_url Link to a webpage with the original issue or
#        commit.
# @param author Github login of the request author.


def create_issue(title, description, src_url, author):
    create_event(author, 'create_issue', title)
    description = '{}\nRequested by @{} in {}.'.format(description, author,
                                                       src_url)
    body = {'title': title, 'body': description}
    url = '{}/issues'.format(doc_repo_url)
    headers = {
        'Authorization': 'token {}'.format(token),
    }
    r = requests.post(url, json=body, headers=headers)
    r.raise_for_status()
    print('Created issue: {}'.format(r.status_code))

##
# Check that a new or edited comment for an issue is the request.
# If it is, then try to parse it and send to a caller
# notification about a result.
# @param body GitHub hook body.
# @param issue_state Issue status: closed, open, created.
# @param issue_api URL of the commented issue. Here a
#        response is wrote.
#
# @retval Response to a GitHub hook.


def process_issue_comment(body, issue_state, issue_api):
    action = body['action']
    if (action != 'created' and action != 'edited') or \
       issue_state != 'open':
        return 'Not needed.'
    comment = body['comment']
    author = comment['user']['login']
    comment, error = parse_comment(comment['body'])
    if error:
        print('Error during request processing: {}'.format(error))
        send_comment(error, issue_api, author)
    elif comment:
        print('Request is processed ok')
        if action == 'edited':
            send_comment('Accept edited.', issue_api, author)
        else:
            send_comment('Accept.', issue_api, author)
    else:
        print('Ignore non-request comments')
    return 'Doc request is processed.'

##
# Check that a just closed issue contains contains
# a well-formatted doc update request. If it does, then
# open a new issue in doc repository. For multiple doc requests
# multiple issues will be created.
# @param body GitHub hook body.
# @param issue_state Issue status: closed, open, created.
# @param issue_api API URL of the original issue.
# @param issue_url Public URL of the original issue.
#
# @retval Response to a GitHub hook.


def process_issue_state_change(body, issue_state, issue_api, issue_url):
    action = body['action']
    if action != 'closed':
        return 'Not needed.'
    comments = get_comments(issue_api)
    comment = None
    for c in comments:
        comment, error = parse_comment(c['body'])
        if comment:
            create_issue(comment["title"], comment["description"],
                         issue_url, c['user']['login'])
    return 'Issue is processed.'

##
# Process a commit event, triggered on any push. If in the commit
# message a request is found, then parse it and create an issue on
# documentation, if the push is done into master.
# @param c Commit object.
# @param is_master_push True if the commit is pushed into the
#        master branch.


def process_commit(c, is_master_push):
    body = c['message']
    request_pos = body.find(bot_name)
    if request_pos == -1:
        return
    request = body[request_pos:]
    author = c['author']['username']
    comment, error = parse_comment(request)
    if error:
        print('Error during request processing: {}'.format(error))
        create_event(author, 'process_commit', error)
    else:
        create_event(author, 'process_commit', 'Accept')
        if is_master_push:
            create_issue(comment['title'], comment['description'],
                         c['url'], author)


@post('/')
def index_post():
    r = request.json
    t = request.get_header('X-GitHub-Event')
    if 'issue' in r:
        issue = r['issue']
        if not 'state' in issue:
            return 'Event is not needed.'
        issue_state = issue['state']
        issue_api = issue['url']
        issue_url = issue['html_url']

        if t == 'issue_comment':
            return process_issue_comment(r, issue_state, issue_api)
        elif t == 'issues':
            return process_issue_state_change(r, issue_state,
                                              issue_api, issue_url)
        else:
            return 'Event "{}" is not needed.'.format(t)
    elif t == 'push':
        repo = r['repository']
        # Strip 'refs/heads/' from beginning.
        branch = '/'.join(r['ref'].split('/')[2:])
        is_master_push = repo['master_branch'] == branch
        for c in r['commits']:
            process_commit(c, is_master_push)
    else:
        return 'Event is not needed.'


@get('/')
def index_get():
    return ('<h1>{}</h1><table border="1" cellspacing="2" ' +
            'cellpadding="2">{}</table>').format('TarantoolBot Journal',
                                                 ' '.join(last_events))


print('Starting bot')
if __name__ == "__main__":
    run(host='0.0.0.0', port=5000)

# allow to run under gunicorn
app = default_app()
