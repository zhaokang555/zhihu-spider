#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
import requests
import utils
import time
import codecs
import json
import os
import sqlite3
import sys
import logging
import cgi
import copy

ID_ARR = sys.argv[1:]

def main(id, timestr):
    try:
        os.mkdir('temp/%s' % id)
    except Exception, e:
        pass

    # 创建session
    s = requests.session()

    # 发送请求，得到response
    r = s.get(config.url.get(id), timeout=(10, 10), headers=config.HEADER)
    # print r.content
    rawJson = r.json()
    with codecs.open('temp/%s/2.json' % id, 'w', 'utf-8') as f:
        json.dump(rawJson, f, ensure_ascii=False, indent=4)
    lst = []
    # print json.dumps(rawJson, indent=4, encoding="UTF-8", ensure_ascii=False)
    for data in rawJson.get('data'):
        tDict = {}
        tDict['action_time_sec'] = data.get('created_time')
        tDict['action'] = data.get('action_text')

        title = ''
        fav = ''
        if tDict['action'] == u'收藏了回答':
            title = data.get('target').get('question').get('title')
            fav = data.get('extra_object').get('title')
        elif tDict['action'] == u'关注了话题':
            title = data.get('target').get('name')
        elif tDict['action'] == u'收藏了文章':
            title = data.get('target').get('title')
            fav = data.get('extra_object').get('title')
        elif data.get('target').get('question'):
            title = data.get('target').get('question').get('title')
        elif data.get('target').get('title'):
            title = data.get('target').get('title')
        tDict['title'] = title
        tDict['fav'] = fav

        tDict['content'] = data.get('target').get('content')
        tDict['excerpt'] = data.get('target').get('excerpt')
        lst.append(tDict)
    # print lst
    with codecs.open('temp/%s/2.json' % id, 'w', 'utf-8') as f:
        json.dump(lst, f, ensure_ascii=False, indent=4)

    # 从2.json文件中读取数据，存入list, 并按时间顺序排列
    lst = []
    with codecs.open('temp/%s/2.json' % id, 'r', encoding='utf-8') as f:
        lst = json.load(f)
    for d in lst:
        timeSec = d['action_time_sec']
        lt = time.localtime(timeSec)
        action_timestr = '%d_%02d_%02d__%02d_%02d_%02d' % (lt[0], lt[1], lt[2], lt[3], lt[4], lt[5])
        # print action_timestr
        d['action_timestr'] = action_timestr
    lst.reverse()
    # print lst
    # print json.dumps(lst, encoding="UTF-8", ensure_ascii=False)


    # 连接数据库
    conn = sqlite3.connect(id + '.db')
    cursor = conn.cursor()
    try:
        # 截取需要存入数据库的list
        cursor.execute('select max(action_time_sec) from activity')
        rArr = cursor.fetchall()
        # print 'rArr', rArr
        latestActionTimeSec = 0
        if rArr[0][0]:
            latestActionTimeSec = rArr[0][0]
        print 'latestActionTimeSec', latestActionTimeSec

        for i in range(len(lst)):
            # print i, len(lst)
            if latestActionTimeSec == lst[i].get('action_time_sec'):
                lst = lst[i+1:]
                break


        # 输出是否更新的信息
        print 'len(lst)', len(lst)
        if len(lst):
            print 'updated'
            # lstCopy = copy.deepcopy(lst)
            # for item in lstCopy:
            #     item.pop('content')
            #     item.pop('action_time_sec')

            emailMsg = json.dumps(lst, indent=4, encoding="UTF-8", ensure_ascii=False)
            emailMsg = emailMsg.encode("GBK", "ignore").decode("GBK")
            # print emailMsg
            # utils.sendEmail('updated %s records' % len(lst), id + ' zhihu')
            lst.reverse()
            utils.sendEmailFromDictLst(lst, id + ' zhihu updated')
            lst.reverse()

        else:
            print 'not modified'


        # 把数据存入数据库
        i = 0
        while i < len(lst):
            cursor.execute(
                '''insert into activity
                    (action_time_sec, action_timestr, action, fav, title, excerpt, content)
                    values (?,?,?,?,?,?,?)''',
                (
                    lst[i].get('action_time_sec'),
                    lst[i].get('action_timestr'),
                    lst[i].get('action'),
                    lst[i].get('fav'),
                    lst[i].get('title'),
                    lst[i].get('excerpt'),
                    lst[i].get('content'),
                 )
            )
            # print i, 'line:', cursor.rowcount
            i += 1

        if len(lst):
            cursor.execute('''insert into activity (action_time_sec, action_timestr, action, fav, title, excerpt, content) values (?,?,?,?,?,?,?)''',
                (0, timestr, 'updated', '===============', '===============', '===============', '===============')
            )
    finally:
        cursor.close()
        conn.commit()
        conn.close()


errorCnt = 0
while True:
    try:
        print '========================='
        sec, timestr = utils.init_time(time.localtime())
        print timestr
        for id in ID_ARR:
            print '==='
            print id
            main(id, timestr)
        print 'sleep %5d sec...' % sec
        errorCnt = 0
        time.sleep(sec)
    except Exception, e:
        errorCnt += 1
        print u'遇到错误'
        logging.exception(e)
        if errorCnt <= 5:
            print 'sleep 60 sec...'
            time.sleep(60)
        else:
            msg = id + ' zhihu errorCnt > 5, stopped'
            print msg
            utils.sendEmail(msg)
            break
    finally:
        pass
        
    

