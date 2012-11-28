import logging

import irc.bot


logger = logging.getLogger(__name__)

class RehaikuBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server_list, nick, name, channel, recon_interval=60, **connect_params):
        super(RehaikuBot, self).__init__(server_list, nick, name, recon_interval, **connect_params)
        self.channel = channel
        self.connection.add_global_handler("welcome", self._on_connect, -20)


    def _on_connect(self, c, e):
        logger.info("Connected to %s", e.source)
        self.connection.join(self.channel)


    def _on_join(self, c, e):
        super(RehaikuBot, self)._on_join(c, e)
        logger.info("Joined channel %s", e.target)
