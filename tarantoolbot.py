from bottle import run, post, request
import requests
import json

doc_label = 'doc update'
doc_request = ' document\r\n'
bot_name = '@TarantoolBot'
title_header = 'Title:'
doc_repo_url = 'https://api.github.com/repos/tarantool/doc'

f = open('credentials.json')
credentials = json.loads(f.read())
f.close()
token = credentials['GitHub']['token']

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
	if not body.startswith(doc_request, offset):
		return None, 'Invalid request type.'
	offset += len(doc_request)
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
def send_comment(body, issue_url, to):
	body = {'body': '@{}: {}'.format(to, body)}
	url = '{}/comments?access_token={}'.format(issue_url, token)
	r = requests.post(url, json=body)
	print('Sent comment: {}'.format(r.status_code))

##
# Get all the comments of an issue.
def get_comments(issue_url):
	body = {'since': '1970-01-01T00:00:00Z'}
	url = '{}/comments?access_token={}'.format(issue_url, token)
	r = requests.get(url, json=body)
	return r.json()

##
# Open a new issue in a documentation repository.
# @param title Issue title.
# @param description Issue description.
# @param author Github login of the request author.
def create_issue(title, description, author):
	description = '{}\nRequested by @{}.'.format(description, author)
	body = {'title': title, 'body': description}
	url = '{}/issues?access_token={}'.format(doc_repo_url, token)
	r = requests.post(url, json=body)
	print('Created issue: {}'.format(r.status_code))

##
# Check that a new comment for an issue is the request.
# If it is, then try to parse it and send to a caller
# notification about a result.
# @param body GitHub hook body.
# @param issue_state Issue status: closed, open, created.
# @param issue_url URL of the commented issue. Here a
#        response is wrote.
#
# @retval Response to a GitHub hook.
def process_issue_comment(body, issue_state, issue_url):
	action = body['action']
	if action != 'created' or issue_state != 'open':
		return 'Not needed.'
	comment = body['comment']
	author = comment['user']['login']
	comment, error = parse_comment(comment['body'])
	if error:
		print('Error during request processing: {}'.format(error))
		send_comment(error, issue_url, author)
	elif comment:
		print('Request is processed ok')
		send_comment('Accept.', issue_url, author)
	else:
		print('Ignore non-request comments')
	return 'Doc request is processed.'

##
# Check that a just closed issue contains contains
# a well-formatted doc update request. If it does, then
# open a new issue in doc repository.
# @param body GitHub hook body.
# @param issue_state Issue status: closed, open, created.
# @param issue_url URL of the closed issue from which
#        comments are got.
def process_issue_state_change(body, issue_state, issue_url):
	action = body['action']
	if action != 'closed':
		return 'Not needed.'
	comments = get_comments(issue_url)
	comment = None
	author = None
	for c in comments:
		comment, error = parse_comment(c['body'])
		if comment:
			author = c['user']['login']
			break
	else:
		return 'Not found formatted comments.'
	create_issue(comment["title"], comment["description"], author)
	return 'Issue is processed.'

@post('/')
def index_post():
	r = request.json
	t = request.get_header('X-GitHub-Event')
	issue_state = r['issue']['state']
	issue_url = r['issue']['url']
	labels = r['issue']['labels']
	# Process only specially labeled issues.
	for label in labels:
		if label['name'] == doc_label:
			break
	else:
		return 'Needed label was not found.'

	if t == 'issue_comment':
		return process_issue_comment(r, issue_state, issue_url)
	elif t == 'issues':
		return process_issue_state_change(r, issue_state,
						  issue_url)
	else:
		return 'Event "{}" is not needed.'.format(t)

print('Starting bot')
run(host='0.0.0.0', port=8888)
