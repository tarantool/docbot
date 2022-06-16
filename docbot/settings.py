import os

token = os.environ.get('GITHUB_TOKEN')
doc_requests = [' document\r\n', ' document\n']
bot_name = '@TarantoolBot'
title_header = 'Title:'
api = 'https://api.github.com/repos/tarantool/'
doc_repo_urls = {
    f'{api}tarantool': f'{api}doc',
    f'{api}tarantool-ee': f'{api}enterprise_doc',
    f'{api}tdg': f'{api}tdg-doc',
}
