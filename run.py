import server
from server import worker_thread
worker_thread.start()
server.rest.app.run(port=8080)

try:
    while worker_thread.is_alive:
        worker_thread.join(0.1)
except KeyboardInterrupt:
    print "Ctrl-c received! Sending kill to threads..."
    server.worker_thread.stop()