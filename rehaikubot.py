import logging
import operator
import random
import re

import irc.bot

import calculations
import config
import queries
import textdb
import userutils
from decorators import nick_command, stats_command


logger = logging.getLogger(__name__)


class RehaikuBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server_list, nick, name, channels, recon_interval=60,
                 **connect_params):
        super(RehaikuBot, self).__init__(server_list, nick, name,
                                         recon_interval, **connect_params)
        self._channels = channels
        self.cmds = ['stats', 'haiku', 'replay', 'conv', 'pretentious',
                     'leaderboard', 'loserboard', 'percentlol', 'spammy']
        self.db = textdb.TextDb()

    def on_welcome(self, c, e):
        logger.info("Connected to %s", e.source)
        for channel in self._channels:
            c.join(channel)

    def on_join(self, c, e):
        logger.info("Joined channel %s", e.target)

    def on_pubmsg(self, c, e):
        logger.debug("Got public msg {} (from {}, to {})".format(
            e.arguments, e.source.nick, e.target))
        self._process_msg(e.target, e)

    def on_privmsg(self, c, e):
        pass  # ignore PMs
        # logger.debug("Got private msg {} (from {}, to {})".format(
        #     e.arguments, e.source.nick, e.target))
        # self._process_msg(e.source.nick, e)

    def _process_msg(self, respond_target, e):
        full_text = e.arguments[0]
        cmd, arguments = self._get_cmd(full_text)
        if cmd is not None:
            self._process_cmd(respond_target, cmd, arguments, e)
        elif full_text[:1] not in config.ignore_prefixes:
            self._process_text(e)

    def _process_text(self, e):
        txt = e.arguments[0]
        logger.debug("_process_text: " + txt)
        executor = self.db.create_executor('_process_text')
        queries.add_line(executor, e.source.nick, e.target, txt)
        self.db.connection.commit()

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
                return cmd_name, arguments

        return None, None

    def _process_cmd(self, respond_target, cmd, arguments, e):
        logger.debug("_process_cmd: {} ({})".format(cmd, arguments))
        getattr(self, '_do_' + cmd)(respond_target, cmd, arguments, e)

    def _do_haiku(self, respond_target, cmd, arguments, e):
        arguments = arguments.split()

        if len(arguments) > 0:
            return

        logger.debug("_do_haiku")
        self.connection.privmsg(respond_target,
                                "I'm sorry, Dave. I'm afraid I can't do that.")

    @nick_command
    def _do_replay(self, executor, respond_target, cmd, arguments, e, nick):
        logger.debug("_do_replay")

        line = queries.get_random_line(executor, nick, e.target)
        if line is not None:
            self.connection.privmsg(respond_target,
                                    "<{}> {}".format(nick, line))
        else:
            self.connection.privmsg(respond_target,
                                    "{} has no history!".format(nick))

    @nick_command
    def _do_conv(self, executor, respond_target, cmd, arguments, e, nick):
        logger.debug("_do_conv")

        self._conv_impl(executor, respond_target, cmd, arguments, e, nick)

    def _conv_impl(self, executor, respond_target, cmd, arguments, e, nick):
        nick_match = None
        tries = 20
        while not nick_match:
            line = queries.get_random_line_like(executor, nick, e.target, '%:%')
            if line is None:  # no directed lines by the user
                logger.debug('No directed lines by the user')
                return
            nick_match = re.match('([^:]*):', line)
            if nick_match.group(1) not in queries.all_nicks(executor):
                nick_match = None  # Didn't really find a nick
            logger.debug(nick_match)
            tries -= 1
            if tries == 0:
                logger.debug(line)
                logger.warning(
                    "Something's gone horribly wrong. " +
                    "Giving up on conversation"
                )
                return

        if nick_match:
            next_nick = nick_match.group(1)
            if random.randint(0, 5) == 0:
                # 1/6 chance that we end the conversation means average
                # conversation length is 5 lines
                line = queries.get_random_line(executor, next_nick, e.target)
                self.connection.privmsg(
                    respond_target, "<{}> {}".format(next_nick, line)
                )
            else:
                self._conv_impl(executor, respond_target, cmd, arguments, e,
                                next_nick)
        else:
            logger.error(
                ('''"{}" contains a nick according to the database, ''' +
                 '''but it really doesn't''').format(line))

        self.connection.privmsg(respond_target, "<{}> {}".format(nick, line))

    def _do_leaderboard(self, respond_target, cmd, arguments, e):
        logger.debug("_do_leaderboard")
        return self._leaderboard(respond_target, arguments,  False)

    def _do_loserboard(self, respond_target, cmd, arguments, e):
        logger.debug("_do_loserboard")
        return self._leaderboard(respond_target, arguments,  True)

    def _leaderboard(self, respond_target, arguments, reverse):
        arguments = arguments.split()
        if len(arguments) != 1:
            self._leaderboard_help(respond_target)
            return

        stat_name = arguments[0]

        try:
            if stat_name not in calculations.calculations:
                raise AttributeError
            stat_func = getattr(calculations, stat_name)
        except AttributeError:
            self._leaderboard_help(respond_target)
            return

        name = 'leaderboard'
        if reverse:
            name = 'loserboard'

        command = '{} {}'.format(name, arguments)
        executor = self.db.create_executor(command)

        nicks = userutils.active_users(executor)
        stats = dict()
        for nick in nicks:
            stats[nick] = round(stat_func(executor, nick), 2)

        all = sorted(stats.items(), key=operator.itemgetter(1),
                     reverse=not reverse)
        self.connection.privmsg(respond_target,
                                "{} for {}:".format(name, stat_name))
        num = min(len(all), 5)
        logger.debug("got {} targets for leaderboard (of out total list of {})"
                     .format(num, len(all)))
        for i in range(num):
            self.connection.privmsg(respond_target,
                                    "{:20}: {:6}".format(all[i][0], all[i][1]))

        executor.print_stats()

    def _leaderboard_help(self, respond_target):
        logger.debug('_leaderboard_help')
        all = ', '.join(calculations.calculations)
        self.connection.privmsg(
            respond_target, 'Available leaderboard commands are {}'.format(all))

    @nick_command
    @stats_command('I have collected {} lines of dialog from {}.')
    def _do_stats(self, executor, respond_target, cmd, arguments, e, nick):
        logger.debug("_do_stats")
        return "stats"

    @nick_command
    @stats_command("{1}'s pretentiousness level is {0:.3}")
    def _do_pretentious(self, executor, respond_target, cmd, arguments, e,
                        nick):
        logger.debug("_do_pretentious")
        return "pretentious"

    @nick_command
    @stats_command("{1}'s lol percentage is {0:.3}")
    def _do_percentlol(self, executor, respond_target, cmd, arguments, e, nick):
        logger.debug('_do_percentlol')
        return 'percentlol'

    @nick_command
    @stats_command("{1}'s spamminess is {0:.3}")
    def _do_spammy(self, executor, respond_target, cmd, arguments, e, nick):
        logger.debug('_do_spammy')
        return 'spammy'
