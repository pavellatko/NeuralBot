import server
from config import *
from server import worker_thread
server.rest.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
worker_thread.start()
server.rest.app.run(port=5005)

try:
    while worker_thread.is_alive:
        worker_thread.join(0.1)
except KeyboardInterrupt:
    print "Ctrl-c received! Sending kill to threads..."
    server.worker_thread.stop()