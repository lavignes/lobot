.. _plugins-ref:

Plugins Reference
=================

.. module:: lobot.plugins
.. currentmodule:: lobot.plugins

Plugin
------

When LoBot loads a module, it looks for all subclasses of :class:`Plugin` and creates instances of them.

.. class:: Plugin()

    .. attribute:: nick

       :return: (str) The current nickname of the bot.

       A read-only property.

    .. attribute:: config

       :return: (dict) The plugin-specific config from ``config.json``.

       A read-only property.

    .. method:: say(target: str, message: str)

        Sends a non-blocking message to a target.

        :param str target: Where to send the message. This can either be another user's nickname
                           or the name of a channel.

        :param str message: The message to send.

    .. method:: reply(nick: str, target: str, message: str)

        Helper method to send a reply to the channel or person addressing the bot.
        Usually used when writing :ref:`plugin-decorators`.

        :param str nick: A user's nickname. Usually received as the **nick** parameter to a callback.

        :param str target: A received message target. Usually received as the **target** parameter to a callback.

        :param str message: The message to send.

    .. method:: on_load()

        **async**: Called when the plugin is fully loaded and ready to perform actions.

    .. method:: on_connected()

        **async**: Called when the bot has established a connection to the server.

    .. method:: on_disconnected()

        **async**: Called when the bot has lost connection to the server.

    .. method:: on_command(nick: str, target: str, message: str)

        **async**: Called when a command message is received.

        :param str nick: A user's nickname.

        :param str target: The message target. Either the bot's nick or a channel name.

        :param str message: The message.

    .. method:: on_msg(nick: str, channel: str, message: str)

        **async**: Called when a message is received on a channel.

        :param str nick: A user's nickname.

        :param str channel: The channel name.

        :param str message: The message.

    .. method:: on_private_msg(nick: str, message: str)

        **async**: Called when a private message is received.

        :param str nick: A user's nickname.

        :param str message: The message.

    .. method:: on_join(channel: str)

        **async**: Called when the bot joins a channel.

        :param str channel: The channel name.

    .. method:: on_they_join(nick: str, channel: str)

        **async**: Called when someone else joins a channel.

        :param str nick: A user's nickname.

        :param str channel: The channel name.

.. _plugin-decorators:

Event Decorators
----------------

The plugins module also contains helpful decorators to make it easy to make your bot watch special message events.

The decorated methods are **async** and should have this signature::

    async def method(self, nick: str, target: str, message: str, match):
        pass

.. function:: listen(pattern: str, flags: str='')

    Use this decorator to create callbacks that will run when a regular expression is matched.

    :param str pattern: The regular expression to match against.

    :param str flags: A string of characters representing regex flags (optional):

        - 'i' to enable case-insensitivity.
        - 's' to enable "DOTALL" mode, that is the '.' regex will match even whitespace.

    Usage::

        @listen('(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)')
        async def url_listener(self, nick: str, target: str, message: str, match):
            self.reply(nick, target, 'I just saw a URL: ' + match.group(1))

.. function:: command(pattern: str, flags: str='')

    Similar to :func:`listen` but only triggers when a message is addressed specifically to the bot.
    This includes private messages to the bot or messages in that look like:

        * ``LoBot: this is a command message``
        * ``LOBOT this is a command message``
        * ``@Lobot this is a command message``
