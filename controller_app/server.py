#!/usr/bin/python
##
##  IOx Carcontrol ...
##
##  Begun                 2016-10-06
##  Last modified         2017-05-24
##
##  Copyright (c) 2014 Paul Beyleveld (pbeyleve@cisco.com). Distribution and modification permitted.
##	GNU General Public License v2.0
##

# THE PROGRAM IS DISTRIBUTED IN THE HOPE THAT IT WILL BE USEFUL, BUT WITHOUT ANY WARRANTY. 
# IT IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, 
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
# PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD
# THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
# 
# IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW THE AUTHOR WILL BE LIABLE TO YOU FOR DAMAGES, 
# INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR 
# INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED 
# INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE 
# WITH ANY OTHER PROGRAMS), EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
from tornado.options import define, options
import requests
import os
import time
import datetime
import multiprocessing
import serialworker
import json
import signal
import logging
import hashlib
import re
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

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
 
class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        try:
            sid
        except NameError:
            logger.info("obtaining ip cam session id")
            sid = getSessionID()
            if sid != 0:
                self.render((os.path.join(BASEDIR, 'index.html')), cam_ip=cfg.get("ipcam", "ip"), cam_port=cfg.get("ipcam", "port"), cam_width=cfg.get("ipcam", "width"), cam_height=cfg.get("ipcam", "height"), username=cfg.get("server", "user"), plugin=cfg.get("ipcam", "plugin"), session_id=sid)
            else:
                logger.warn("could not obtain session id from ip cam, verify connectivity and credentials")
                self.render((os.path.join(BASEDIR, 'index.html')), cam_ip=cfg.get("ipcam", "ip"), cam_port=cfg.get("ipcam", "port"), cam_width=cfg.get("ipcam", "width"), cam_height=cfg.get("ipcam", "height"), username=cfg.get("server", "user"), plugin="NA", session_id=sid)
        else:
            if sid != 0:
                self.render((os.path.join(BASEDIR, 'index.html')), cam_ip=cfg.get("ipcam", "ip"), cam_port=cfg.get("ipcam", "port"), cam_width=cfg.get("ipcam", "width"), cam_height=cfg.get("ipcam", "height"), username=cfg.get("server", "user"), plugin=cfg.get("ipcam", "plugin"), session_id=sid)
            else:
                logger.warn("attempting to obtain session id from ip cam")
                sid = getSessionID()
                if sid != 0:
                    self.render((os.path.join(BASEDIR, 'index.html')), cam_ip=cfg.get("ipcam", "ip"), cam_port=cfg.get("ipcam", "port"), cam_width=cfg.get("ipcam", "width"), cam_height=cfg.get("ipcam", "height"), username=cfg.get("server", "user"), plugin=cfg.get("ipcam", "plugin"), session_id=sid)
                else:
                    logger.warn("failed to obtain session id from ip cam")
                    self.render((os.path.join(BASEDIR, 'index.html')), cam_ip=cfg.get("ipcam", "ip"), cam_port=cfg.get("ipcam", "port"), cam_width=cfg.get("ipcam", "width"), cam_height=cfg.get("ipcam", "height"), username=cfg.get("server", "user"), plugin="NA", session_id=sid)

class StaticFileHandler(BaseHandler):
    def get(self):
        self.render(os.path.join(BASEDIR, 'main.js'))
        self.render(os.path.join(BASEDIR, 'jquery.min.js'))
        self.render(os.path.join(BASEDIR, 'main.css'))
        self.render(os.path.join(BASEDIR, 'Cisco_Logo.png'))
 
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    #@tornado.web.authenticated
    def check_origin(self, origin):
        return True
    
    #@tornado.web.authenticated
    def open(self):
        logger.info("new connection")
        clients.append(self)
        self.write_message("socket connected")
 
    #@tornado.web.authenticated
    def on_message(self, message):
        logger.debug("tornado received from client: %s" % json.dumps(message))
        #self.write_message('ack')
        input_queue.put(message)
 
    #@tornado.web.authenticated
    def on_close(self):
        logger.info("connection closed")
        clients.remove(self)
        self.write_message("socket disconnect")

class LoginHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        incorrect = self.get_secure_cookie("incorrect")
        if incorrect and int(incorrect) > 15:
            self.write('<center>blocked, try again later</center>')
            return
        self.render((os.path.join(BASEDIR, 'login.html')), cmd_msg="")
        
    @tornado.gen.coroutine
    def post(self):
        expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
        incorrect = self.get_secure_cookie("incorrect")
        if incorrect and int(incorrect) > 15:
            self.write('<center>blocked, try again later</center>')
            return
        
        getusername = tornado.escape.xhtml_escape(self.get_argument("username"))
        getpassword = tornado.escape.xhtml_escape(self.get_argument("password"))
        SHA256_hash = hashlib.sha256(getpassword.encode())

        if cfg.get("server", "user") == getusername and cfg.get("server", "pass") == SHA256_hash.hexdigest():
            self.set_secure_cookie("user", self.get_argument("username"))
            self.set_secure_cookie("incorrect", "0", expires=expires)
                
            self.redirect(self.reverse_url("main"))
        else:
            incorrect = self.get_secure_cookie("incorrect") or 0
            increased = str(int(incorrect)+1)
            self.set_secure_cookie("incorrect", increased, expires=expires)
            #self.write("""<center>
            #                Something Wrong With Your Data (%s)<br />
            #                <a href="/">Go Home</a>
            #              </center>""" % increased)
            self.render((os.path.join(BASEDIR, 'login.html')), cmd_msg="Invalid credentials")
                          
class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", self.reverse_url("main")))
        
## check the queue for pending messages, and rely that to all connected clients

class Application(tornado.web.Application):
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        settings = {
            "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
            "login_url": "/login",
            'debug':True,
            "xsrf_cookies": True,
        }
        
        tornado.web.Application.__init__(self, [
            tornado.web.url(r"/", IndexHandler, name="main"),
            tornado.web.url(r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=BASEDIR)),
            tornado.web.url(r'/login', LoginHandler, name="login"),
            tornado.web.url(r'/logout', LogoutHandler, name="logout"),
            tornado.web.url(r"/ws", WebSocketHandler),
        ], **settings)

## check the queue for pending messages, and rely that to all connected clients

def checkQueue():
    if not output_queue.empty():
        message = output_queue.get()
        for c in clients:
            c.write_message(message)

def getSessionID():
    url = "https://%s/login.cs" % cfg.get("ipcam", "ip")
    payload = {'version': '1.0', 'action': 'login', 'userName': cfg.get("ipcam", "user"), 'password': cfg.get("ipcam", "pass"), 'sesionTemp': ''}
    try:    
        with requests.session() as s:
            # fetch the login page
            s.get(url, verify=False, timeout=1) #timeout if unsuccessful in 1 sec

            # post to the login form
            r = s.post(url, data=payload)
            searchObj = re.search(r'(sessionID=)(\d{8})', r.content)
            sessionid = searchObj.group(2)
            #print(searchObj.group(2))
        return sessionid
    except Exception as ex:
        logger.exception("IP Cam connection failure")
        return 0

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
        Application().listen(options.port)
        app = tornado.web.Application(
            handlers=[
                (r"/", IndexHandler),
                (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=BASEDIR)),
                (r"/ws", WebSocketHandler)
            ]
        )
        
        httpServer = tornado.httpserver.HTTPServer(app)
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
