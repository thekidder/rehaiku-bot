import logging
import sqlite3

import schema
import sqlutils


logger = logging.getLogger(__name__)

class TextDb:
    def __init__(self, db_name='text.db'):
        self.db_name = db_name
        self._connect()


    def _connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        executor = self.create_executor('upgrade')
        v = schema.version(executor)
        while v < schema.LATEST_VERSION:
            fn = getattr(schema, 'v{}_to_v{}'.format(v, v+1))
            logger.info('upgrading from v{} to v{}...'.format(v, v+1))
            fn(executor)
            v += 1
        executor.print_stats()
        logger.info('db version is latest ({})'.format(schema.LATEST_VERSION))



    def __del__(self):
        logger.info('destroying connection')
        self.cursor.close()
        self.connection.commit()
        self.connection.close()


    def create_executor(self, command):
        return sqlutils.QueryExecutor(command, self.cursor)
