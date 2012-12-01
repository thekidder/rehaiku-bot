import logging

import irc.bot

import config
import textdb


logger = logging.getLogger(__name__)

class RehaikuBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server_list, nick, name, channel, recon_interval=60, **connect_params):
        super(RehaikuBot, self).__init__(server_list, nick, name, recon_interval, **connect_params)
        self.channel = channel
        self.cmds = ['stats','haiku', 'replay', 'pretentious']
        self.db = textdb.TextDb()


    def on_welcome(self, c, e):
        logger.info("Connected to %s", e.source)
        c.join(self.channel)


    def on_join(self, c, e):
        logger.info("Joined channel %s", e.target)


    def on_pubmsg(self, c, e):
        logger.debug("Got public msg {} (from {}, to {})".format(e.arguments, e.source.nick, e.target))
        self._process_msg(e.target, e)


    def on_privmsg(self, c, e):
        logger.debug("Got private msg {} (from {}, to {})".format(e.arguments, e.source.nick, e.target))
        self._process_msg(e.source.nick, e)


    def _process_msg(self, respond_target, e):
        full_text = e.arguments[0]
        cmd,arguments = self._get_cmd(full_text)
        if cmd != None:
            self._process_cmd(respond_target, cmd, arguments, e)
        elif full_text[:1] != config.cmd_prefix:
            self._process_text(e)


    def _process_text(self, e):
        txt = e.arguments[0]
        logger.debug("_process_text: " + txt)
        self.db.add_line(e.source.nick, e.target, txt)


    def _get_cmd(self, cmd):
        if cmd[:1] == config.cmd_prefix:
            cmd_boundary = cmd.find(' ')
            cmd = cmd[1:]
            cmd_name = cmd
            arguments = ""
            if cmd_boundary != -1:
                cmd_name = cmd[:cmd_boundary].strip()
                arguments = cmd[cmd_boundary:].strip()

            if cmd_name in self.cmds:
                logger.info("got command name " + cmd_name + " " + arguments)
                return cmd_name,arguments

        return None,None


    def _process_cmd(self, respond_target, cmd, arguments, e):
        logger.debug("_process_cmd: {} ({})".format(cmd, arguments))
        getattr(self, '_do_' + cmd)(respond_target, cmd, arguments, e)


    def _do_stats(self, respond_target, cmd, arguments, e):
        logger.debug("_do_stats")
        sender = e.source.nick

        nick = self._get_cmd_nick(arguments, e)
        if nick == None:
            return

        count = self.db.get_line_count_by_nick(nick)
        self.connection.privmsg(respond_target, 'I have collected {} lines of dialog from {}.'.format(
                count, nick))


    def _do_haiku(self, respond_target, cmd, arguments, e):
        logger.debug("_do_haiku")
        self.connection.privmsg(respond_target, "I'm sorry, Dave. I'm afraid I can't do that.")


    def _do_replay(self, respond_target, cmd, arguments, e):
        logger.debug("_do_replay")

        nick = self._get_cmd_nick(arguments, e)
        if nick == None:
            return

        line = self.db.get_random_line(nick,e.target)
        if line != None:
            self.connection.privmsg(respond_target, "<{}> {}".format(nick, line))
        else:
            self.connection.privmsg(respond_target, "{} has no history!".format(nick))


    def _do_pretentious(self, respond_target, cmd, arguments, e):
        logger.debug("_do_pretentious")

        nick = self._get_cmd_nick(arguments, e)
        if nick == None:
            return

        p = text_utils.reading_level(self.db, nick)

        self.connection.privmsg(respond_target, "{}'s pretentiousness level is {:.3}".format(nick, p))


    def _get_cmd_nick(self, arguments, e):
        arguments = arguments.split()
        if len(arguments) > 1:
            return None
        elif len(arguments) == 1:
            return arguments[0]
        else:
            return e.source.nick
