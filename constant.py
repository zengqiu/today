# -*- coding: utf-8 -*-

DATABASE = 'today.db'
TABLE = 'today'
COMMANDS = ['init', 'add', 'delete', 'done', 'undone', 'update']
DATABASE_STATUS = {0: '', 1: u'数据库连接失败', 2: u'数据库查询失败', 3: u'数据库插入失败', 4: u'数据库初始化失败', 5: u'数据库更新失败', 6: u'数据库删除失败'}