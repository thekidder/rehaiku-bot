import calculations


def nick_command(fn):
    def wrapped(self, respond_target, cmd, arguments, e, nick=None):
        if nick is None:
            nick = _get_cmd_nick(arguments, e)
        if nick == None:
            return

        command = '{} {}'.format(cmd, arguments)
        executor = self.db.create_executor(command)
        r =  fn(self, executor, respond_target, cmd, arguments, e, nick)
        executor.print_stats()
        return r

    return wrapped


def stats_command(string):
    def decorator(fn):
        def wrapped(self, executor, respond_target, cmd, arguments, e, nick):
            stat_name = fn(self, respond_target, cmd, arguments, e, nick)
            if stat_name != None:
                answer = getattr(calculations, stat_name)(executor, nick)
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
