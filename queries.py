import datetime

import fleschkincaid


def get_lines_by_nick(executor, nick):
    sql = '''select full_text from text where nick=? order by date asc'''
    return exector.query(sql, (nick,))


def get_distinct_lines_by_nick(executor, nick):
    sql = '''select distinct full_text from text where nick=? order by date asc'''
    return executor.query(sql, (nick,))


def get_line_count_by_nick(executor, nick):
    sql = '''select count(full_text) from text where nick=?'''
    return executor.query_one_row(sql, (nick,))[0]


def get_line_count_like_pattern(executor, nick, pattern):
    sql = '''select count(full_text) from text where nick=? and full_text like ?'''
    return executor.query_one_row(sql, (nick,pattern,))[0]


def get_distinct_line_count_since_date(executor, nick, date):
    sql = '''select count(distinct full_text) from text where nick=? and date>?'''
    return executor.query_one_row(sql, (nick,date,))[0]


def get_distinct_line_count_by_nick(executor, nick):
    sql = '''select count(distinct full_text) from text where nick=?'''
    return executor.query_one_row(sql, (nick,))[0]


def reading_level(executor, nick):
    sql = '''select avg(pretentious) from text where nick=?'''
    return executor.query_one_row(sql, (nick,))[0]


def get_random_line(executor, nick, source):
    sql = '''select distinct full_text from text where nick=? and target=? order by random() limit 1'''
    row = executor.query_one_row(sql, (nick,source,))
    if row != None:
        return row[0]
    else:
        return None


def get_random_lines_like(executor, nick, source, like,count):
    sql = ('''select distinct full_text from text where nick=? and ''' +
           '''target=? and full_text like ? order by random() limit ?''')
    rows = executor.query_all_rows(sql, (nick,source,like,count,))
    return [row[0] for row in rows]


def get_random_line_like(executor, nick, source, like):
    sql = ('''select distinct full_text from text where nick=? and ''' +
           '''target=? and full_text like ? order by random() limit 1''')
    row = executor.query_one_row(sql, (nick,source,like,))
    if row is not None:
        return row[0]
    else:
        return None


def add_line(executor, nick, target, full_text):
    sql = '''insert into text values (?,?,?,?,?)'''
    now = datetime.datetime.utcnow().isoformat()
    rl = _sentence_reading_level(full_text)
    executor.execute(sql, (now,nick,target,full_text,rl,))


def _sentence_reading_level(s):
    return max(0.0, fleschkincaid.grade_level(s))


def all_nicks(executor):
    sql = '''select distinct(nick) from text order by nick'''
    return [nick[0] for nick in executor.query_all_rows(sql)]


def all_active_nicks(executor):
    time = datetime.timedelta(weeks=1)
    date = datetime.datetime.utcnow()
    date = (date - time).isoformat()


    sql = '''select nick from text where date>? group by nick having count(nick)>15 order by nick'''
    return [nick[0] for nick in executor.query_all_rows(sql, (date,))]
