import logging
import operator

import irc.bot

import calculations
import config
import textdb
from decorators import nick_command, stats_command


logger = logging.getLogger(__name__)

class RehaikuBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server_list, nick, name, channel, recon_interval=60, **connect_params):
        super(RehaikuBot, self).__init__(server_list, nick, name, recon_interval, **connect_params)
        self.channel = channel
        self.cmds = ['stats', 'haiku', 'replay', 'pretentious', 'leaderboard']
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


    @nick_command
    @stats_command('I have collected {} lines of dialog from {}.')
    def _do_stats(self, respond_target, cmd, arguments, e, nick):
        logger.debug("_do_stats")
        return "stats"


    def _do_haiku(self, respond_target, cmd, arguments, e):
        arguments = arguments.split()

        if len(arguments) > 0:
            return

        logger.debug("_do_haiku")
        self.connection.privmsg(respond_target, "I'm sorry, Dave. I'm afraid I can't do that.")


    @nick_command
    def _do_replay(self, respond_target, cmd, arguments, e, nick):
        logger.debug("_do_replay")

        line = self.db.get_random_line(nick,e.target)
        if line != None:
            self.connection.privmsg(respond_target, "<{}> {}".format(nick, line))
        else:
            self.connection.privmsg(respond_target, "{} has no history!".format(nick))


    def _do_leaderboard(self, respond_target, cmd, arguments, e):
        logger.debug("_do_leaderboard")

        arguments = arguments.split()
        if len(arguments) != 1:
            return

        stat_name = arguments[0]

        try:
            stat_func = getattr(calculations, stat_name)
        except AttributeError:
            return

        nicks = self.db.all_nicks()
        stats = dict()
        for nick in nicks:
            stats[nick] = round(stat_func(self.db, nick), 2)

        all = sorted(stats.items(), key=operator.itemgetter(1), reverse=True)
        self.connection.privmsg(respond_target, "leaderboard for {}:".format(stat_name))
        num = min(len(all), 5)
        for i in range(num):
            self.connection.privmsg(respond_target, "{:20}: {:6}".format(all[i][0], all[i][1]))

    @nick_command
    @stats_command("{1}'s pretentiousness level is {0:.3}")
    def _do_pretentious(self, respond_target, cmd, arguments, e, nick):
        logger.debug("_do_pretentious")
        return "pretentious"
