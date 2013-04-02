import logging


logger = logging.getLogger(__name__)

class QueryExecutor:
    def __init__(self, command, cursor):
        self.command = command
        self.cursor = cursor
        self.queries = 0
        self.rows = 0


    def query_one_row(self, sql, args=()):
        self._query_common(sql, args)
        self.rows += 1
        return self.cursor.fetchone()


    def query_all_rows(self, sql, args=()):
        self._query_common(sql, args)
        rows = self.cursor.fetchall()
        self.rows += len(rows)
        return rows


    def query(self, sql, args=()):
        self._query_common(sql, args)
        for row in self.cursor:
            self.rows += 1
            yield row


    def execute(self, sql, args=()):
        self._query_common(sql, args)


    def _query_common(self, sql, args):
        self.cursor.execute(sql, args)
        self.queries += 1


    def print_stats(self):
        logger.debug('Command "{}" resulted in {} queries and {} rows'.format(
            self.command, self.queries, self.rows))
