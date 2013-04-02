import queries
import textutils


calculations = ['stats', 'spammy', 'percentlol', 'pretentious']

def stats(executor, nick):
    return queries.get_distinct_line_count_by_nick(executor, nick)


def pretentious(executor, nick):
    return queries.reading_level(executor, nick)


def spammy(executor, nick):
    t = queries.get_line_count_by_nick(executor, nick) * 1.0
    d = queries.get_distinct_line_count_by_nick(executor, nick)

    if d == 0:
        return 0.0

    return t / d


def percentlol(executor, nick):
    total = queries.get_line_count_by_nick(executor, nick)

    if total == 0:
        return 0.0

    lol = queries.get_line_count_like_pattern(executor, nick, 'lol')
    return (lol / total) * 100.0
