# !C:\Python27\python.exe
# -*- coding: UTF-8 -*-
import uuid
from com.baipan.util.DictUtil import Dict
from DBConnection import *

__author__ = '5y'

'''BaseDao类'''


def next_id(t=None):
    if t is None:
        t = time.time()
    return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)


def _select(sql, first, *args):
    ' execute select SQL and return unique result or list results.'
    global _db_ctx
    cursor = None
    sql = sql.replace('?', '%s')
    logging.info('SQL: %s, 参数: %s' % (sql, args))
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        if cursor.description:
            names = [x[0] for x in cursor.description]
        if first:
            values = cursor.fetchone()
            if not values:
                return None
            return Dict(names, values)
        return [Dict(names, x) for x in cursor.fetchall()]
    finally:
        if cursor:
            cursor.close()


@with_connection
def select_one(sql, *args):
    '''
    Execute select SQL and expected one result.
    If no result found, return None.
    If multiple results found, the first one returned.

    >>> u1 = dict(id=100, name='Alice', email='alice@test.org', passwd='ABC-12345', last_modified=time.time())
    >>> u2 = dict(id=101, name='Sarah', email='sarah@test.org', passwd='ABC-12345', last_modified=time.time())
    >>> insert('user', **u1)
    1
    >>> insert('user', **u2)
    1
    >>> u = select_one('select * from user where id=?', 100)
    >>> u.name
    u'Alice'
    >>> select_one('select * from user where email=?', 'abc@email.com')
    >>> u2 = select_one('select * from user where passwd=? order by email', 'ABC-12345')
    >>> u2.name
    u'Alice'
    '''
    return _select(sql, True, *args)


@with_connection
def select_int(sql, *args):
    '''
    Execute select SQL and expected one int and only one int result.

    >>> n = update('delete from user')
    >>> u1 = dict(id=96900, name='Ada', email='ada@test.org', passwd='A-12345', last_modified=time.time())
    >>> u2 = dict(id=96901, name='Adam', email='adam@test.org', passwd='A-12345', last_modified=time.time())
    >>> insert('user', **u1)
    1
    >>> insert('user', **u2)
    1
    >>> select_int('select count(*) from user')
    2
    >>> select_int('select count(*) from user where email=?', 'ada@test.org')
    1
    >>> select_int('select count(*) from user where email=?', 'notexist@test.org')
    0
    >>> select_int('select id from user where email=?', 'ada@test.org')
    96900
    >>> select_int('select id, name from user where email=?', 'ada@test.org')
    Traceback (most recent call last):
        ...
    MultiColumnsError: Expect only one column.
    '''
    d = _select(sql, True, *args)
    if len(d) != 1:
        raise ErrorException("-1", "Expect only one column.")
    return d.values()[0]


@with_connection
def select(sql, *args):
    '''
    Execute select SQL and return list or empty list if no result.

    >>> u1 = dict(id=200, name='Wall.E', email='wall.e@test.org', passwd='back-to-earth', last_modified=time.time())
    >>> u2 = dict(id=201, name='Eva', email='eva@test.org', passwd='back-to-earth', last_modified=time.time())
    >>> insert('user', **u1)
    1
    >>> insert('user', **u2)
    1
    >>> L = select('select * from user where id=?', 900900900)
    >>> L
    []
    >>> L = select('select * from user where id=?', 200)
    >>> L[0].email
    u'wall.e@test.org'
    >>> L = select('select * from user where passwd=? order by id desc', 'back-to-earth')
    >>> L[0].name
    u'Eva'
    >>> L[1].name
    u'Wall.E'
    '''
    return _select(sql, False, *args)


@with_connection
def _update(sql, *args):
    global _db_ctx
    cursor = None
    sql = sql.replace('?', '%s')
    logging.info('SQL: %s, ARGS: %s' % (sql, args))
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        r = cursor.rowcount
        if _db_ctx.transactions == 0:
            # no transaction enviroment:
            logging.info('auto commit')
            _db_ctx.connection.commit()
        return r
    finally:
        if cursor:
            cursor.close()


def insert(table, **kw):
    '''
    Execute insert SQL.

    >>> u1 = dict(id=2000, name='Bob', email='bob@test.org', passwd='bobobob', last_modified=time.time())
    >>> insert('user', **u1)
    1
    >>> u2 = select_one('select * from user where id=?', 2000)
    >>> u2.name
    u'Bob'
    >>> insert('user', **u2)
    Traceback (most recent call last):
      ...
    IntegrityError: 1062 (23000): Duplicate entry '2000' for key 'PRIMARY'
    '''
    cols, args = zip(*kw.iteritems())
    sql = 'insert into `%s` (%s) values (%s)' % (
        table, ','.join(['`%s`' % col for col in cols]), ','.join(['?' for i in range(len(cols))]))
    return _update(sql, *args)


def update(sql, *args):
    r'''
    Execute update SQL.

    >>> u1 = dict(id=1000, name='Michael', email='michael@test.org', passwd='123456', last_modified=time.time())
    >>> insert('user', **u1)
    1
    >>> u2 = select_one('select * from user where id=?', 1000)
    >>> u2.email
    u'michael@test.org'
    >>> u2.passwd
    u'123456'
    >>> update('update user set email=?, passwd=? where id=?', 'michael@example.org', '654321', 1000)
    1
    >>> u3 = select_one('select * from user where id=?', 1000)
    >>> u3.email
    u'michael@example.org'
    >>> u3.passwd
    u'654321'
    >>> update('update user set passwd=? where id=?', '***', '123\' or id=\'456')
    0
    '''
    return _update(sql, *args)
