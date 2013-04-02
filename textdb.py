import datetime
import logging
import sqlite3
import sqlutils


logger = logging.getLogger(__name__)

class TextDb:
    def __init__(self, db_name='text.db'):
        self.db_name = db_name
        self._connect()


    def _connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        if not self._exists():
            self._create()


    def _create(self):
        sql = '''create table text (date text, nick text, target text, full_text text)'''
        self.cursor.execute(sql)


    def _exists(self):
        sql = '''select count(type) from sqlite_master where type='table' and name=?'''
        self.cursor.execute(sql, ('text',))
        return self.cursor.fetchone()[0] == 1


    def __del__(self):
        self.cursor.close
        self.connection.close()


    def create_executor(self, command):
        return sqlutils.QueryExecutor(command, self.cursor)
