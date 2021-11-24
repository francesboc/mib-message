"""
Message in a Bottle
Gunicorn configuration file

This file is the configuration file for gunicorn, the
WSGI server of mib-api-gateway microservice.
"""

# the bind address
bind = '0.0.0.0:5000'
backlog = 2048

#
# Tuning the workers as specified in this article
# https://pythonspeed.com/articles/gunicorn-in-docker/
#
workers = 2
threads = 4
worker_tmp_dir = '/dev/shm'
worker_class = 'gthread'
worker_connections = 1000
timeout = 30
keepalive = 2

#
# We want to disable the trace function that spews every line of Python,
# for production purposes.
#
spew = False

#
# Daemon and permissions configuration
#
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

#
# Logging
# with docker container we should log to stdout/stderr
#
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
