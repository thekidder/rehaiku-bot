#!/usr/bin/env python
import logging
import signal
import ssl

import irc.connection

import config
import rehaikubot


logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.DEBUG)

    if config.ssl:
        factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
    else:
        factory = irc.connection.Factory()

    bot = rehaikubot.RehaikuBot(
        config.servers,
        config.nick,
        config.name,
        config.channels,
        60,
        connect_factory=factory)

    def cleanup(signal, frame):
        bot.disconnect()
        logger.info("Killed. Exiting.")
        exit()

    signal.signal(signal.SIGINT, cleanup)

    bot.start()


if __name__ == "__main__":
    main()
