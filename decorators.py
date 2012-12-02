import calculations


def nick_command(fn):
    def wrapped(self, respond_target, cmd, arguments, e):
        nick = _get_cmd_nick(arguments, e)
        if nick == None:
            return

        return fn(self, respond_target, cmd, arguments, e, nick)

    return wrapped


def stats_command(string):
    def decorator(fn):
        def wrapped(self, respond_target, cmd, arguments, e, nick):
            stat_name = fn(self, respond_target, cmd, arguments, e, nick)
            if stat_name != None:
                answer = getattr(calculations, stat_name)(self.db, nick)
                self.connection.privmsg(respond_target, string.format(answer, nick))

        return wrapped

    return decorator


def _get_cmd_nick(arguments, e):
    arguments = arguments.split()
    if len(arguments) > 1:
        return None
    elif len(arguments) == 1:
        return arguments[0]
    else:
        return e.source.nick
