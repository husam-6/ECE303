# Written by S. Mevawala, modified by Husam Almanakly and Layth Yassin

## TODO Two bugs to fix - 1) bug when stuck at base = seqnum-5 and 2) fix minor bug at output (diff failing, maybe problem with our checksums)

import logging
import socket
import threading
import channelsimulator
import utils
import sys
from checksum import sexyChecksum, window
import math

class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port, debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    def send(self, data):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoSender(Sender):

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.u_send(data)  # send data
                ack = self.simulator.u_receive()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(ack.decode()))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass

class SexySender(Sender):

    def __init__(self):
        super(SexySender, self).__init__()

    N = window                   # Window size
    # timers = [0]*2*N
    timers = threading.Timer(1, True)
    timers.daemon = True 
    packetSize = 2*window        # Size of packets
    timeout = 0.05

    base = 0
    nextseqnum = 0

    def makePacket(self, data, nextseqnum):
        #Ensure sequence number is 3 bytes (zero pad)
        
        tmp = str(nextseqnum)
        tmp = "0"*(5-len(tmp)) + tmp
        check = sexyChecksum(data+tmp)
        
        return data + bytearray(tmp + check, encoding="utf8")

    # FIXME: potential race condition
    def resend(self, data, arg):
        # for i in range(base, nextseqnum+1):
        #     item = data[base]
        # print("TIMEOUT ON BASE = {}".format(self.base))
        
        self.logger.info("Resending packet: {} to {}.\nReason: {}".format(self.base, self.nextseqnum, arg))

        for i in range(self.base, self.nextseqnum):
            # print("Resending packet {}".format(i))
            tmp = self.makePacket(data[i], i)
            self.simulator.u_send(tmp)  # resend data"

        self.timers = threading.Timer(self.timeout, self.resend, [data, "Timeout"])
        self.timers.daemon = True 
        self.timers.start()
        # print("RESENDING DATA: {} to {}".format(self.base, min(self.base+self.N, len(data))))
        sys.exit()

    def send(self, data):
        chunks = [data[i:i+self.packetSize] for i in range(0, len(data), self.packetSize)]    # Dividing data into packets of 100 bytes
        while True:
            print("base: {}, nextseq #: {}".format(self.base, self.nextseqnum))
            if self.base >= len(chunks) and self.nextseqnum == self.base:# or self.nextseqnum == len(chunks):
                print("HUGE COCK")
                break
            

            #If we are within the window...
            if self.nextseqnum < self.base + self.N and self.nextseqnum<len(chunks):
                packet = self.makePacket(chunks[self.nextseqnum], self.nextseqnum)
                self.simulator.u_send(packet)  # send data in window of size N
                self.logger.info("Sending packet: {}".format(packet))
                if self.base == self.nextseqnum:
                    self.timers.cancel()
                    self.timers = threading.Timer(self.timeout, self.resend, [chunks, "Timeout"])
                    self.timers.daemon = True 
                    self.timers.start()       
                self.nextseqnum+=1

            try:
                ack = self.simulator.u_receive()  # receive ACK
                check = ack[-9:]
                comp = sexyChecksum(str(ack[:-9]))
                if str(check) != comp:
                    continue
                
                # print("ACK RECEIVED: {}, expecting {} ".format(int(str(ack[:-9])), self.base))
                self.logger.info("Got ACK {} from socket, expecting {}".format(int(str(ack[:-9])), self.base))
                decAck = int(str(ack[:-9]))
                if decAck >= self.base:
                    self.base = decAck + 1
                if self.base == self.nextseqnum:
                    self.timers.cancel()
                else: 
                    self.timers.cancel()
                    self.timers=threading.Timer(self.timeout, self.resend, [chunks, "Timeout"])
                    self.timers.daemon = True 
                    self.timers.start()     
            except:
                print("Error or no acks received")
                continue
        
        self.timers.cancel()
        print(threading.active_count())
        sys.exit()

if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read(), encoding='utf8')
    sndr = SexySender()
    sndr.send(DATA)
