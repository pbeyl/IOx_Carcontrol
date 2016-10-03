#!/usr/bin/python
import serial
import time
import multiprocessing
import os
import logging
import signal


logger = logging.getLogger("carcontrol")


## Change this to match your local settings
#SERIAL_PORT = '/dev/ttyACM0'
#SERIAL_BAUDRATE = 115200

SERIAL_PORT = os.getenv("HOST_DEV2")
if SERIAL_PORT is None:
    SERIAL_PORT="/dev/ttyS1"    #/dev/ttyS1


class SerialProcess(multiprocessing.Process):
 
    def __init__(self, input_queue, output_queue, baud_rate):
        
        logger.debug("Serial Settings")
        logger.debug("Port: %s" % SERIAL_PORT)
        logger.debug("BAUD Rate: %s" % baud_rate)
        
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        for i in range(3):
            logger.info("Initializing serial worker...")
            try:
                self.sp = serial.Serial(SERIAL_PORT, baud_rate)
                self.sp.bytesize = serial.EIGHTBITS #number of bits per bytes
                self.sp.parity = serial.PARITY_NONE #set parity check: no parity
                self.sp.stopbits = serial.STOPBITS_ONE #number of stop bits
                self.sp.timeout = 0.05
                
                break
            except Exception as e:
                logger.exception("Unexpected error: %s" % e)
        logger.info("Initialized")
 
    def close(self):
        self.sp.close()
 
    def writeSerial(self, data):
        self.sp.write(data)
        # time.sleep(1)
        
    def readSerial(self):
        return self.sp.readline().replace("\n", "")

    def run(self):

        # Gracefully handle SIGTERM and SIGINT
        def handle_signal(signum, stack):
            logger.info('Serialworker Received Signal: %s', signum)
            # Raise a KeyboardInterrupt so that the main loop catches this and shuts down
            raise KeyboardInterrupt

        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)
        
        self.sp.flushInput()
 
        while True:
            try:
                time.sleep(0.01)
                # look for incoming tornado request
                if not self.input_queue.empty():
                    data = self.input_queue.get()
 
                    # send it to the serial device
                    self.writeSerial(data.encode('utf-8'))
                    logger.debug("writing to serial: %s" % data)
 
                # look for incoming serial data
                if (self.sp.inWaiting() > 0):
                    data = self.readSerial()
                    logger.debug("reading from serial: %s" % data)
                    # send it back to tornado
                    self.output_queue.put(data)
            except KeyboardInterrupt:
                logger.debug("Stopping serialworker thread...")
                self.close()
