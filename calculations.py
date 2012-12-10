import text_utils

def stats(db, nick):
    return db.get_distinct_line_count_by_nick(nick)


def pretentious(db, nick):
    return text_utils.reading_level(db, nick)


def percentlol(db, nick):
    total = db.get_line_count_by_nick(nick)
    
    if total == 0:
        return 0.0

    lol = db.get_line_count_like_pattern(nick, 'lol')
    return (lol / total) * 100.0
