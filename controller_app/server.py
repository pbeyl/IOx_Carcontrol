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
import logging
from logging.handlers import RotatingFileHandler


logger = logging.getLogger("carcontrol")

# Get hold of the configuration file (package_config.ini)
moduledir = os.path.abspath(os.path.dirname(__file__))
BASEDIR = os.getenv("CAF_APP_PATH", moduledir)

# If we are not running with CAF, use the BASEDIR to get cfg file
tcfg = os.path.join(BASEDIR, "package_config.ini")
CONFIG_FILE = os.getenv("CAF_APP_CONFIG_FILE", tcfg)

define("port", default=8080, help="run on the given port", type=int)
 
clients = [] 

input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()

envlist = ["CAF_APP_PATH", "CAF_APP_PERSISTENT_DIR", "CAF_APP_LOG_DIR", "CAF_APP_CONFIG_FILE", "CAF_APP_CONFIG_DIR",
           "CAF_APP_USERNAME", "CAF_HOME", "CAF_HOME_ABS_PATH", "CAF_APP_PATH", "CAF_MODULES_PATH",
           "CAF_APP_DIR", "CAF_MODULES_DIR", "CAF_APP_ID"]

from ConfigParser import SafeConfigParser
cfg = SafeConfigParser()
cfg.read(CONFIG_FILE)


def dump_caf_env():
    logger.debug("Printing CAF ENV VARIABLES")
    for l in envlist:
        logger.debug("%s: %s" % (l, os.getenv(l)))


def setup_logging():
    """
    Setup logging for the current module and dependent libraries based on
    values available in config.
    """
    # set a format which is simpler for console use
    formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")

    # Set log level based on what is defined in package_config.ini file
    loglevel = cfg.getint("logging", "log_level")
    logger.setLevel(loglevel)

    # Create a console handler only if console logging is enabled
    ce = cfg.getboolean("logging", "console")
    if ce:
        console = logging.StreamHandler()
        console.setLevel(loglevel)
        console.setFormatter(formatter)
        # add the handler to the root logger
        logger.addHandler(console)

    # The default is to use a Rotating File Handler
    log_file_dir = os.getenv("CAF_APP_LOG_DIR", "/tmp")
    log_file_path = os.path.join(log_file_dir, "carcontrol.log")

    # Lets cap the file at 1MB and keep 3 backups
    rfh = RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=3)
    rfh.setLevel(loglevel)
    rfh.setFormatter(formatter)
    logger.addHandler(rfh)


# Gracefully handle SIGTERM and SIGINT
def handle_signal(signum, stack):
    logger.info('Server Received Signal: %s', signum)
    # Raise a KeyboardInterrupt so that the main loop catches this and shuts down
    raise KeyboardInterrupt

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)


 
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render((os.path.join(BASEDIR, 'index.html')), cam_ip=cfg.get("ipcam", "ip"), cam_user=cfg.get("ipcam", "user"), cam_pass=cfg.get("ipcam", "pass"), cam_port=cfg.get("ipcam", "port"), cam_width=cfg.get("ipcam", "width"), cam_height=cfg.get("ipcam", "height"))

class StaticFileHandler(tornado.web.RequestHandler):
	def get(self):
		self.render(os.path.join(BASEDIR, 'main.js'))
		self.render(os.path.join(BASEDIR, 'main.css'))
		self.render(os.path.join(BASEDIR, 'Cisco_Logo.png'))
 
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        logger.info("new connection")
        clients.append(self)
        self.write_message("socket connected")
 
    def on_message(self, message):
        logger.info("tornado received from client: %s" % json.dumps(message))
        #self.write_message('ack')
        input_queue.put(message)
 
    def on_close(self):
        logger.info("connection closed")
        clients.remove(self)
        self.write_message("socket disconnect")


## check the queue for pending messages, and rely that to all connected clients

def checkQueue():
	if not output_queue.empty():
		message = output_queue.get()
		for c in clients:
			c.write_message(message)

if __name__ == '__main__':
    setup_logging()
    
    # Log env variables
    dump_caf_env()
    
    def terminate_self(mainLoop):
        logger.info("Stopping carcontrol services")
        try:
            mainLoop.stop()
        except Exception as ex:
            logger.exception("Error stopping the app gracefully.")
        logger.info("Killing self..")
        os.kill(os.getpid(), 9)
    
    try: 
        ## start the serial worker in background (as a deamon)
        sp = serialworker.SerialProcess(input_queue, output_queue, cfg.getint("serial", "baudrate"))
        sp.daemon = True
        sp.start()
        
        tornado.options.parse_command_line()
        app = tornado.web.Application(
            handlers=[
                (r"/", IndexHandler),
                (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=BASEDIR)),
                (r"/ws", WebSocketHandler)
            ]
        )
        httpServer = tornado.httpserver.HTTPServer(app)
        httpServer.listen(options.port)
        logger.info("Listening on port: %s" % options.port)

        mainLoop = tornado.ioloop.IOLoop.instance()
        ## adjust the scheduler_interval according to the frames sent by the serial port
        scheduler_interval = 50
        scheduler = tornado.ioloop.PeriodicCallback(checkQueue, scheduler_interval, io_loop = mainLoop)
        scheduler.start()
        mainLoop.start()
        
    except KeyboardInterrupt:
        sp.join()
        terminate_self(mainLoop)
    except Exception as ex:
        logger.exception("Caught exception! Terminating..")
        terminate_self()
