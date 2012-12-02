import text_utils

def stats(db, nick):
    return db.get_line_count_by_nick(nick)


def pretentious(db, nick):
    return text_utils.reading_level(db, nick)
