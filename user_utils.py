import datetime


def active_users(db):
    nicks = db.all_nicks()
    filtered_nicks = list()

    for nick in nicks:
        if is_user_active(db, nick):
            filter_nicks.append(nick)

    return filtered_nicks


def is_user_active(db, nick):
    time = datetime.timedelta(weeks=1)
    date = datetime.datetime.utcnow()
    date = date - time

    num = db.get_distinct_line_count_since_date(nick, date.isoformat())

    return num > 15
