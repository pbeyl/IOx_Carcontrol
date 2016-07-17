#!/usr/bin/python
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
from tornado.options import define, options
import os
import time
import multiprocessing
import serialworker
import json
import signal
 
define("port", default=8080, help="run on the given port", type=int)
root = os.getenv('CAF_APP_PATH')
 
clients = [] 

input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()

def _sleep_handler(signum, frame):
    print "SIGINT Received. Stopping CarControl"
    raise KeyboardInterrupt

def _stop_handler(signum, frame):
    print "SIGTERM Received. Stopping CarControl"
    raise KeyboardInterrupt

signal.signal(signal.SIGTERM, _stop_handler)
signal.signal(signal.SIGINT, _sleep_handler)

 
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(os.path.join(root, 'index.html'))

class StaticFileHandler(tornado.web.RequestHandler):
	def get(self):
		self.render(os.path.join(root, 'main.js'))
		self.render(os.path.join(root, 'main.css'))
		self.render(os.path.join(root, 'Cisco_Logo.png'))
 
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        clients.append(self)
        self.write_message("connected")
 
    def on_message(self, message):
        print 'tornado received from client: %s' % json.dumps(message)
        #self.write_message('ack')
        input_queue.put(message)
 
    def on_close(self):
        print 'connection closed'
        clients.remove(self)


## check the queue for pending messages, and rely that to all connected clients
def checkQueue():
	if not output_queue.empty():
		message = output_queue.get()
		for c in clients:
			c.write_message(message)


if __name__ == '__main__':
    try: 
        ## start the serial worker in background (as a deamon)
        sp = serialworker.SerialProcess(input_queue, output_queue)
        sp.daemon = True
        sp.start()
        
        tornado.options.parse_command_line()
        app = tornado.web.Application(
            handlers=[
                (r"/", IndexHandler),
                (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=root)),
                (r"/ws", WebSocketHandler)
            ]
        )
        httpServer = tornado.httpserver.HTTPServer(app)
        httpServer.listen(options.port)
        print "Listening on port:", options.port

        mainLoop = tornado.ioloop.IOLoop.instance()
        ## adjust the scheduler_interval according to the frames sent by the serial port
        scheduler_interval = 1
        scheduler = tornado.ioloop.PeriodicCallback(checkQueue, scheduler_interval, io_loop = mainLoop)
        scheduler.start()
        mainLoop.start()
    except KeyboardInterrupt:
        print "Keyboard Interrupt Detected: Stopping services..."
        mainLoop.stop()
