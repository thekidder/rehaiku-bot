import queries
import datetime


def active_users(executor):
    nicks = queries.all_nicks(executor)
    filtered_nicks = list()

    for nick in nicks:
        if is_user_active(executor, nick) and not is_user_a_bot(nick):
            filtered_nicks.append(nick)

    return filtered_nicks


def is_user_active(executor, nick):
    time = datetime.timedelta(weeks=1)
    date = datetime.datetime.utcnow()
    date = date - time

    num = queries.get_distinct_line_count_since_date(executor, nick, date.isoformat())

    return num > 15


def is_user_a_bot(nick):
    return nick[-1] == '^'
