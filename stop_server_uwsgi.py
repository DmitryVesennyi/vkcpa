import redis
from subprocess import Popen, PIPE
import os

def redis_connect(host = 'localhost', port=6379, db=0):
    return redis.StrictRedis(host=host, port=port, db=db)

r = redis_connect()
r.set('robot', '0')

command = 'uwsgi --stop /tmp/project-master.pid'.split()
p = Popen(command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
p.communicate()
