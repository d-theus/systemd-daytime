#!/usr/bin/env python2
import datetime
import socket
import signal
import os
import sys
import time

pidfile_name = '/tmp/daytime.pid'

def read_pidfile():
    pidfile = open(pidfile_name, 'r')
    string = pidfile.read()
    pidfile.close()
    return(int(string))

def write_pidfile():
    pidfile = open(pidfile_name, 'w')
    pidfile.write(str(os.getpid()))
    pidfile.close()

def rm_pidfile():
    if os.path.isfile(pidfile_name): 
        os.remove(pidfile_name)

def shutdown(signum, frame):
    global s
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    rm_pidfile()
    os._exit(0)

def routine():
    write_pidfile()

    global s 
    s = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
            )

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while 1:
        try:
            s.bind(('0.0.0.0', 13))
            break
        except socket.error:
            sys.stderr.write('Port 13 already in use. Retrying in 20 seconds\n')
            time.sleep(20)
            pass

    s.listen(10)

    sys.stderr.write('Daytime server listening on port 13...\n')

    while 1:
        (cs, addr) = s.accept()
        dt = datetime.datetime.now()
        cs.send(dt.strftime('%m%d%H%M%y.%S'))
        cs.close()

action = 'start'
if len(sys.argv) > 1:
    action = sys.argv[1]
    if action != 'start' and action != 'stop':
        sys.exit('ERROR: specify valid action: start or stop')

if action == 'start' and os.path.isfile(pidfile_name):
    sys.exit('WARNING: already running')

if action == 'stop':
    if not os.path.isfile(pidfile_name):
        sys.exit('ERROR: no process found')
    else:
        os.kill(read_pidfile(), signal.SIGINT)
        rm_pidfile()
        os._exit(0)

# action == start and no running server found
serverpid = os.fork()
if serverpid == 0:
    routine()
else:
    os._exit(0)
