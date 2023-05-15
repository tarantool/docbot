import datetime
import hashlib
import hmac

from . import settings

last_events = []


def create_event(author, action, body):
    time = datetime.datetime.now().strftime('%b %d %H:%M:%S')
    result = '<tr>'
    result += '<td>{}</td>'.format(time)
    result += '<td>{}</td>'.format(author)
    result += '<td>{}</td>'.format(action)
    result += '<td>{}</td>'.format(body)
    result += '</tr>'
    last_events.append(result)
    if len(last_events) > settings.LAST_EVENTS_SIZE:
        last_events.pop(0)

def is_verified_signature(body, signature):
    """Verify that the payload was sent from GitHub by validating SHA256.
    
    Returns True if the request is authorized, otherwise False.
    
    Args:
        body: original request body to verify
        signature: header received from GitHub
    """
    if not signature:
        return False
    hash_object = hmac.new(
        settings.github_signature.encode('utf-8'),
        msg=body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature):
        return False
    return True
