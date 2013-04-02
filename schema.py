import fleschkincaid

LATEST_VERSION = 3

def version(executor):
    sql = '''select count(type) from sqlite_master where type='table' and name=?'''
    row = executor.query_one_row(sql, ('text',))
    exists = row[0] == 1

    if not exists:
        return 0

    row = executor.query_one_row(sql, ('version',))
    version_exists = row[0] == 1

    if not version_exists:
        return 1

    sql = '''select version from version'''
    version, = executor.query_one_row(sql)

    return int(version)


# upgrade funcs
def v0_to_v1(executor):
    sql = '''create table text (date text, nick text, target text, full_text text)'''
    executor.execute(sql)


def v1_to_v2(executor):
    sql = '''create table version (version integer)'''
    executor.execute(sql)
    _insert_version(executor, 2)


def v2_to_v3(executor):
    def reading_level(s):
        rl = fleschkincaid.grade_level(s)
        return max(0.0, rl)

    sql = '''alter table text add column pretentious real'''
    executor.execute(sql)
    sql = '''select distinct full_text from text'''
    rows = executor.query_all_rows(sql)
    for row in rows:
        text = row[0]
        rl = reading_level(text)
        sql = '''update text set pretentious = ? where full_text = ?'''
        executor.execute(sql, (rl,text))

    _insert_version(executor, 3)


def _insert_version(executor, version):
    sql = '''delete from version'''
    executor.execute(sql)

    sql = '''insert into version values (?)'''
    executor.execute(sql, (version,))
