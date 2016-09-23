# -*- coding: utf-8 -*-

import sqlite3
import logging
from constant import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('today.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def connect_database(database):
    conn = sqlite3.connect(database)
    return conn

def close_database(conn):
    conn.close()

def init_database(database):
    try:
        conn = connect_database(database)
        with open('today.sql', 'r') as f:
            conn.cursor().executescript(f.read())
        conn.commit()
        close_database(conn)
        status_code = 0
    except Exception, e:
        # print e
        status_code = 4
        
    return status_code

def select_table_all(database, table, params=None):
    conn = connect_database(database)
    cur = conn.cursor()
    if params:
        sql = "SELECT %s FROM '%s' ORDER BY status ASC, timestamp DESC" % (params, table)
    else:
        sql = "SELECT * FROM '%s' ORDER BY status ASC, timestamp DESC" % table

    status = ''
    result = list()
    
    try:
        cur.execute(sql)
        status = DATABASE_STATUS[0]
        result = [list(value) for value in cur.fetchall()]
    except Exception, e:
        status = DATABASE_STATUS[2]
        logger.error('Failed to selete table %s', table, exc_info=True)

    conn.close()

    return {'status': status, 'result': result}

def insert_table_one(database, table, params, values):
    sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, params, values)
    try:
        conn = connect_database(database)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        status_code = 0
    except Exception, e:
        print e
        conn.rollback()
        status_code = 3
        logger.error('Failed to insert value into table %s', table, exc_info=True)
    conn.close()

def update_status_done(database, table, timestamps):
    timestamps_tuple = tuple(timestamps)
    if len(timestamps) == 1:
        timestamps = "('%s')" % timestamps[0]
    else:
        timestamps = tuple(timestamps)
    sql = "UPDATE %s SET status=1 WHERE timestamp IN %s" % (table, timestamps)
    try:
        conn = connect_database(database)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        status_code = 0
    except Exception, e:
        print e
        conn.rollback()
        status_code = 5
        logger.error('Failed to update status to done in table %s', table, exc_info=True)
    conn.close()

def update_status_undone(database, table, timestamps):
    timestamps_tuple = tuple(timestamps)
    if len(timestamps) == 1:
        timestamps = "('%s')" % timestamps[0]
    else:
        timestamps = tuple(timestamps)
    sql = "UPDATE %s SET status=0 WHERE timestamp IN %s" % (table, timestamps)
    try:
        conn = connect_database(database)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        status_code = 0
    except Exception, e:
        print e
        conn.rollback()
        status_code = 5
        logger.error('Failed to update status to undone in table %s', table, exc_info=True)
    conn.close()

def delete_items(database, table, timestamps):
    timestamps_tuple = tuple(timestamps)
    if len(timestamps) == 1:
        timestamps = "('%s')" % timestamps[0]
    else:
        timestamps = tuple(timestamps)
    sql = "DELETE FROM %s WHERE timestamp IN %s" % (table, timestamps)
    try:
        conn = connect_database(database)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        status_code = 0
    except Exception, e:
        print e
        conn.rollback()
        status_code = 6
        logger.error('Failed to delete items in table %s', table, exc_info=True)
    conn.close()

def update_items(database, table, data):
    print data
    sqls = list()
    for key, value in data.items():
        sql = "UPDATE %s SET content='%s' WHERE timestamp='%s'" % (table, value, key)
        sqls.append(sql)

    try:
        conn = connect_database(database)
        cur = conn.cursor()
        for sql in sqls:
            cur.execute(sql)
        conn.commit()
        status_code = 0
    except Exception, e:
        print e
        conn.rollback()
        status_code = 5
        logger.error('Failed to update items in table %s', table, exc_info=True)
    conn.close()