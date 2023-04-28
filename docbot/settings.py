import os

token = os.environ.get('GITHUB_TOKEN')
assert token is not None
doc_requests = [' document\r\n', ' document\n']
bot_name = '@TarantoolBot'
title_header = 'Title:'
api = 'https://api.github.com/repos/tarantool/'
doc_repo_urls = {
    'tarantool/tarantool': f'{api}doc',
    'tarantool/vshard': f'{api}doc',
    'tarantool/tarantool-ee': f'{api}enterprise_doc',
    'tarantool/sdk': f'{api}enterprise_doc',
    'tarantool/tdg': f'{api}tdg-doc',
    'tarantool/tdg2': f'{api}tdg-doc',
    'tarantool/tt': f'{api}doc',
    'tarantool/tt-ee': f'{api}enterprise_doc',
}
LAST_EVENTS_SIZE = 30
