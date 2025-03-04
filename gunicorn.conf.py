import multiprocessing
import os

# Set the correct working directory
chdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app'))

# Gunicorn configuration
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True
daemon = False
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Set the Python path to include app directory
pythonpath = chdir