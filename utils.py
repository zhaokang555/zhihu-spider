#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import config
import random
import codecs
import json
import re
import os
import requests
import cgi

# ====================
# 工具函数
# ====================

HEADER = config.HEADER
TIMEOUT = config.TIMEOUT

def init_time(lt):
    # 0. init
    wait_sec = 86400
    random_sec = 999
    time_str = ''

    # 1. random_sec
    random_sec = random.randint(0, 100) - 60

    # 2. wait_sec
    # print lt[3]
    # if lt[3] in range(2, 9):
    #     wait_sec = 250
    # elif lt[3] in range(9, 13):
    #     wait_sec = 70
    # elif lt[3] in [21, 22, 23, 0, 1]:
    #     wait_sec = 30
    # else: # [13, 21)点
    #     wait_sec = 50

    # if lt[4] % 5 == 0:
    #     wait_sec += 60

    # 3. time_str
    time_str = '%d_%02d_%02d__%02d_%02d_%02d' % (lt[0], lt[1], lt[2], lt[3], lt[4], lt[5])

    return wait_sec + random_sec, time_str


# ====================
# email
# ====================

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

FROM_ADDR = config.FROM_ADDR
PASSWORD = config.PASSWORD
TO_ADDR = config.TO_ADDR
SMTP_SERVER = config.SMTP_SERVER

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

def sendEmail(msgStr, subject='subject'):
    def main(msgStr, subject):
        msg = MIMEText(msgStr, 'plain', 'utf-8')
        msg['From'] = _format_addr(u'python <%s>' % FROM_ADDR)
        msg['To'] = _format_addr(u'zk <%s>' % TO_ADDR)
        # msg['From'] = FROM_ADDR
        # msg['To'] = TO_ADDR
        msg['Subject'] = Header(subject, 'utf-8').encode()

        server = smtplib.SMTP(SMTP_SERVER, 25)
        # server.set_debuglevel(1)
        server.login(FROM_ADDR, PASSWORD)
        server.sendmail(FROM_ADDR, [TO_ADDR], msg.as_string())
        server.quit()

    main(msgStr, subject)

def sendEmailFromDictLst(lst, subject='subject'):
    htmlStr = ''
    for d in lst:
        ul = ''
        ul += '<li>%s</li>' % d['action_timestr']
        ul += '<li>%s</li>' % d['action']
        if d['fav']:
            ul += '<li>%s</li>' % d['fav']
        ul += '<li>%s</li>' % d['title']
        if d['excerpt']:
            ul += '<li>%s</li>' % cgi.escape(d['excerpt'])
        ul = '<ul>%s</ul>' % ul
        htmlStr += ul
        htmlStr += '<hr>'
    # print htmlStr

    msg = MIMEText(htmlStr, 'html', 'utf-8')
    msg['From'] = _format_addr(u'python <%s>' % FROM_ADDR)
    msg['To'] = _format_addr(u'zk <%s>' % TO_ADDR)
    # msg['From'] = FROM_ADDR
    # msg['To'] = TO_ADDR
    msg['Subject'] = Header(subject, 'utf-8').encode()

    server = smtplib.SMTP(SMTP_SERVER, 25)
    # server.set_debuglevel(1)
    server.login(FROM_ADDR, PASSWORD)
    server.sendmail(FROM_ADDR, [TO_ADDR], msg.as_string())
    server.quit()



