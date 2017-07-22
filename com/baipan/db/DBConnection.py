# !C:\Python27\python.exe
# -*- coding: UTF-8 -*-


__author__ = '5y'

'''数据库操作类'''

import functools, threading, jdbc
from com.baipan.exception.ErrorException import *

'''
Connection对象类
'''


class _LasyConnection(object):
    def __init__(self):
        self.connection = None

    def cursor(self):
        if self.connection is None:
            connection = engine.connect()
            logging.info('创建连接 <%s>...' % hex(id(connection)))
            self.connection = connection
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection:
            connection = self.connection
            self.connection = None
            logging.info('关闭连接 <%s>...' % hex(id(connection)))
            connection.close()
        return self.connection


'''
数据库连接的上下文
'''


class _DbCtx(threading.local):
    def __init__(self):
        self.connection = None
        self.transactions = 0

    # self.connection不为空 return True
    # self.connection为空 return False
    def is_init(self):
        return not self.connection is None

    def init(self):
        logging.info('打开连接中...')
        self.connection = _LasyConnection()
        self.transactions = 0

    def cleanup(self):
        self.connection = self.connection.cleanup()

    def cursor(self):
        return self.connection.cursor()


class _Engine(object):
    def __init__(self, connect):
        self._connect = connect

    def connect(self):
        return self._connect()


# global engine object:
engine = None


def create_engine(host=jdbc.host(), port=jdbc.port(), user=jdbc.username(), password=jdbc.password(),
                  database=jdbc.db(), **kw):
    import mysql.connector
    global engine
    if engine is not None:
        raise ErrorException('-1', '引擎已经初始化')
    params = dict(user=user, password=password, database=database, host=host, port=port)
    defaults = dict(use_unicode=True, charset='utf8', collation='utf8_general_ci', autocommit=False)
    for k, v in defaults.iteritems():
        params[k] = kw.pop(k, v)
    params.update(kw)
    params['buffered'] = True
    engine = _Engine(lambda: mysql.connector.connect(**params))
    logging.info('初始化引擎 <%s> ok.' % hex(id(engine)))


# thread-local db context:
_db_ctx = _DbCtx()


class _ConnectionCtx(object):
    def __enter__(self):
        global _db_ctx
        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()


def connection():
    return _ConnectionCtx()


def with_connection(func):
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        with _ConnectionCtx():
            return func(*args, **kw)

    return _wrapper


class _TransactionCtx(object):
    def __enter__(self):
        global _db_ctx
        self.should_close_conn = False
        if not _db_ctx.is_init():
            # needs open a connection first:
            _db_ctx.init()
            self.should_close_conn = True
        _db_ctx.transactions = _db_ctx.transactions + 1
        logging.info('开启事务...' if _db_ctx.transactions == 1 else 'join current transaction...')
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        _db_ctx.transactions = _db_ctx.transactions - 1
        try:
            if _db_ctx.transactions == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()

    def commit(self):
        global _db_ctx
        logging.info('提交事务...')
        try:
            _db_ctx.connection.commit()
            logging.info('提交成功.')
        except:
            logging.warning('提交失败，开始回滚事务...')
            _db_ctx.connection.rollback()
            logging.warning('回滚 ok.')
            raise ErrorException("-1", "事务回滚失败")

    def rollback(self):
        global _db_ctx
        logging.warning('回滚事务...')
        _db_ctx.connection.rollback()
        logging.info('回滚 ok.')


def transaction():
    return _TransactionCtx()


def _profiling(start, sql=''):
    t = time.time() - start
    if t > 0.1:
        logging.warning('[PROFILING] [DB] %s: %s' % (t, sql))
    else:
        logging.info('[PROFILING] [DB] %s: %s' % (t, sql))


def with_transaction(func):
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        _start = time.time()
        with _TransactionCtx():
            return func(*args, **kw)
        _profiling(_start)

    return _wrapper
