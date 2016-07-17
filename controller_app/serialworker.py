#!/usr/bin/python
import serial
import time
import multiprocessing
import os

## Change this to match your local settings
#SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUDRATE = 115200

SERIAL_PORT = os.getenv("HOST_DEV2")
if SERIAL_PORT is None:
    SERIAL_PORT="/dev/ttyS1"    #/dev/ttyS1



print "Serial Setting"
print "Port: %s" % SERIAL_PORT
print "BAUD Rate: %s" % SERIAL_BAUDRATE

class SerialProcess(multiprocessing.Process):
 
    def __init__(self, input_queue, output_queue):
        
        multiprocessing.Process.__init__(self)
        self.input_queue = input_queue
        self.output_queue = output_queue
        for i in range(3):
            print "Initializing serial worker..."
            try:
                self.sp = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
                self.sp.bytesize = serial.EIGHTBITS #number of bits per bytes
                self.sp.parity = serial.PARITY_NONE #set parity check: no parity
                self.sp.stopbits = serial.STOPBITS_ONE #number of stop bits
                self.sp.timeout = 0.4
                
                break
            except Exception as e:
                print("Unexpected error:", e)
        print "Initialized"
 
    def close(self):
        self.sp.close()
 
    def writeSerial(self, data):
        self.sp.write(data)
        # time.sleep(1)
        
    def readSerial(self):
        return self.sp.readline().replace("\n", "")
 
    def run(self):
 
        self.sp.flushInput()
 
        while True:
            try:
                # look for incoming tornado request
                if not self.input_queue.empty():
                    data = self.input_queue.get()
 
                    # send it to the serial device
                    self.writeSerial(data.encode('utf-8'))
                    print "writing to serial: " + data
 
                # look for incoming serial data
                if (self.sp.inWaiting() > 0):
                    data = self.readSerial()
                    print "reading from serial: " + data
                    # send it back to tornado
                    self.output_queue.put(data)
            except KeyboardInterrupt:
                print "Stopping serial thread..."
                self.close()
