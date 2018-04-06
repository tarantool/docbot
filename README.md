# DocBot - Tarantool Documentation pipeline bot

TarantoolBot automates a process of creating a documentation request after external behaviour is changed.
Documentation bot has its own account on mail.ru and on github.com. Its name is TarantoolBot.
It uses GitHub webhooks to track all new comments on issues, labeled with 'doc update' label.
In a comment a one can ask the bot to create a new issue on tarantool/doc, when the issue
will be closed, using the special template. The one must mention the bot, write a title and
description:
```
@TarantoolBot document
Title: one-line totle
Description that can be multiline,
contain markup and links.
```
When the bot sees its mentioning, it checks the comment syntax, and responses with either error
description or with `@<CommentAuthor>: Accept`. When the issue is closed, the bot finds
this comment, extracts the title and description, and creates a new issue on tarantool/doc
with notifying the comment author. Thanks to the bot, now no one must care about creating a doc
issue after push into trunk, changing some external behaviour.
