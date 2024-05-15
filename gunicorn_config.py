import os


workers = int(os.environ.get('GUNICORN_PROCESSES', '2'))
threads = int(os.environ.get('GUNICORN_THREADS', '4'))
bind = os.environ.get('GUNICORN_BIND', 'unix:gunicorn_socket/myclimbz.sock')
umask = int(os.environ.get('GUNICORN_UMASK', '007'))
forwarded_allow_ips = '*'
secure_scheme_headers = { 'X-Forwarded-Proto': 'https' }