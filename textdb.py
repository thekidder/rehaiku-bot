import datetime
import logging
import sqlite3


logger = logging.getLogger(__name__)

class TextDb:
    def __init__(self, db_name='text.db'):
        self.db_name = db_name
        self.table_name = 'text'
        self._connect()


    def _connect(self):
        self.connection = sqlite3.connect(self.db_name)
        if not self._exists():
            self._create()


    def _create(self):
        sql = '''create table {} (date text, nick text, target text, full_text text)'''.format(self.table_name)
        c = self.connection.cursor()
        c.execute(sql)
        self.connection.commit()


    def _exists(self):
        sql = '''select count(type) from sqlite_master where type='table' and name=?'''
        c = self.connection.cursor()
        c.execute(sql, (self.table_name,))
        return c.fetchone()[0] == 1


    def get_lines_by_nick(self, nick):
        sql = '''select full_text from {} where nick=? order by date asc'''.format(self.table_name)
        c = self.connection.cursor()
        c.execute(sql, (nick,))
        return c


    def get_line_count_by_nick(self, nick):
        sql = '''select count(full_text) from {} where nick=?'''.format(self.table_name)
        c = self.connection.cursor()
        c.execute(sql, (nick,))
        return c.fetchone()[0]


    def get_random_line(self, nick, source):
        sql = '''select distinct full_text from {} where nick=? and target=? order by random() limit 1'''.format(self.table_name)
        c = self.connection.cursor()
        c.execute(sql, (nick,source,))

        row = c.fetchone()
        if row != None:
            return row[0]
        else:
            return None


    def add_line(self, nick, target, full_text):
        sql = '''insert into {} values (?,?,?,?)'''.format(self.table_name)
        now = datetime.datetime.utcnow().isoformat()
        c = self.connection.cursor()
        c.execute(sql, (now,nick,target,full_text,))
        self.connection.commit()
