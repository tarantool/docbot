import datetime

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
