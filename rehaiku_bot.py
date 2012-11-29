import logging

import irc.bot

import config


logger = logging.getLogger(__name__)

class RehaikuBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server_list, nick, name, channel, recon_interval=60, **connect_params):
        super(RehaikuBot, self).__init__(server_list, nick, name, recon_interval, **connect_params)
        self.channel = channel
        self.cmds = ['numlines','haiku']


    def on_welcome(self, c, e):
        logger.info("Connected to %s", e.source)
        c.join(self.channel)


    def on_join(self, c, e):
        logger.info("Joined channel %s", e.target)


    def on_pubmsg(self, c, e):
        logger.info("Got public msg {} (from {}, to {})".format(e.arguments, e.source.nick, e.target))
        self._process_msg(e.target, e)


    def on_privmsg(self, c, e):
        logger.info("Got private msg {} (from {}, to {})".format(e.arguments, e.source.nick, e.target))
        self._process_msg(e.source.nick, e)


    def _process_msg(self, respond_target, e):
        cmd = self._get_cmd(e.arguments)
        if cmd != None:
            self._process_cmd(respond_target, cmd, e)
        elif e.arguments[:1] != config.cmd_prefix:
            self._process_text(e)
        self.connection.privmsg(respond_target, "pong!")


    def _process_text(self, e):
        logger.debug("_process_text: " + e.arguments)


    def _get_cmd(self, cmd):
        if cmd[:1] == config.cmd_prefix:
            cmd = cmd[1:]
            if cmd in self.cmds:
                return cmd

        return None


    def _process_cmd(self, respond_target, cmd, e):
        logger.debug("_process_cmd: {} ({})".format(cmd, e.arguments))
        getattr(self, '_do_' + cmd)(respond_target, cmd, e)


    def _do_numlines(self, respond_target, cmd, e):
        logger.debug("_do_numlines")


    def _do_haiku(self, respond_target, cmd, e):
        logger.debug("_do_haiku")
