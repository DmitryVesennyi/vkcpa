# -*- coding: utf-8 -*-
import redis
import threading
from subprocess import Popen, PIPE
import os
import time
from vkcpa.models import Users, Groups, UserGroup, StaticGroups
from datetime import datetime, timedelta
from random import random

SIGN_LIMIT = 100#Лимит подписываний
DELTA_SIGN_LIMIT = 20#Для рандомного вывода лимита
WAITING = 24#Время ожидания после превышения лимита - часы

class Serena(threading.Thread):
    def __init__(self, execut = None):
        threading.Thread.__init__(self)
        self.execut = execut
        self.daemon = True
        self.setName('SereNa')
    def run(self):
        try:
            r = redis_connect()
            r.set('robot',os.getpid())
        except:
            command = 'service redis-server start'.split()
            p = Popen(command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
            p.communicate()
            if p.returncode == 0:
                r = redis_connect()
                r.set('robot',os.getpid)
            else:
                print 'error server redis'
                return 500
        while True:
            if r.get('robot') == '0':
                break
            time.sleep(3)
            if self.execut:
                try:
                    self.execut(r)
                except:
                    if r.get('robot_error'):
                        r.set('robot_error', int(r.get('robot_error')) + 1)
                    else:
                        r.set('robot_error', '1')

def redis_connect(host = 'localhost', port=6379, db=0):
    return redis.StrictRedis(host=host, port=port, db=db)

def conductor(redis):
    groups = list(StaticGroups.objects.all()) + map(lambda x:x.group_info, Groups.objects.filter(behavior =1))
    for group in groups:
        if redis.get(group.group_id):
            day = datetime.utcnow()
            data_delta = timedelta(hours = 24)
            if group.impression == False and int(redis.get(group.group_id)) >= group.limit_impressions and day - data_delta >= group.end_limit.replace(tzinfo=None):
                redis.set(group.group_id, '0')
                group.limit_impressions = random_generate()
                group.save()
                continue
            if group.impression == False and int(redis.get(group.group_id)) >= group.limit_impressions:
                group.impression = True
                group.save()
                redis.set(group.group_id, '0')
                continue
            if group.impression == True:
                delta = timedelta(hours = WAITING)
                if day - delta >= group.end_limit.replace(tzinfo=None):
                    group.impression = False
                    group.limit_impressions = random_generate()
                    group.save()
            else:
                continue

def random_generate():
    m1 = SIGN_LIMIT + DELTA_SIGN_LIMIT/2
    m2 = SIGN_LIMIT - DELTA_SIGN_LIMIT/2
    return int(round(random()*(m1-m2)+m2))
