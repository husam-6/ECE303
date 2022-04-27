# Written by S. Mevawala, modified by Husam Almanakly and Layth Yassin

## TODO Two bugs to fix - 1) bug when stuck at base = seqnum-5 and 2) fix minor bug at output (diff failing, maybe problem with our checksums)

import logging
import socket
import threading
import channelsimulator
import utils
import sys
from checksum import sexyChecksum, window

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
    timers = [0]*2*N
    packetSize = 100        # Size of packets
    timeout = 3

    def makePacket(self, data, nextseqnum):
        #Ensure sequence number is 3 bytes (zero pad)
        
        tmp = str(nextseqnum%(2*self.N))
        tmp = "0"*(3-len(tmp)) + tmp
        check = sexyChecksum(data+tmp)
        
        return data + tmp + check

    def resend(self, data, nextseqnum, arg):
        # for i in range(base, nextseqnum+1):
        #     item = data[base]
        #Set up a new time out for the resend packet
        # self.timers[nextseqnum%(2*self.N)].cancel()
        # timer = threading.Timer(self.timeout, self.resend, [data, nextseqnum, "Timeout"])       
        # timer.start()
        # self.timers[nextseqnum%(2*self.N)] = timer

        tmp = self.makePacket(data, nextseqnum)
        print("RESENDING DATA: {}".format(nextseqnum))
        self.simulator.u_send(tmp)  # resend data
        self.logger.info("Resending packet: {}, seqnum: {}.\nReason: {}".format(nextseqnum, nextseqnum%(2*self.N), arg))

    def send(self, data):
        chunks = [data[i:i+self.packetSize] for i in range(0, len(data), self.packetSize)]    # Dividing data into packets of 100 bytes
        base = 0
        nextseqnum = 0
        # waitTime = threading.Timer(timeout, self.resend, [chunks[nextseqnum], nextseqnum]).start()
        while True:
            print("base: {}, nextseq #: {}".format(base, nextseqnum))
            if base == len(chunks) or nextseqnum >= len(chunks):
                break
            if nextseqnum < base + self.N:
                packet = self.makePacket(chunks[nextseqnum], nextseqnum)
                # self.simulator.u_send(bytearray(packet, encoding="utf8"))  # send data in window of size N
                self.simulator.u_send(packet)  # send data in window of size N
                self.logger.info("Sending packet: {} with seqnum: {}".format(nextseqnum, nextseqnum%(2*self.N)))
                timer = threading.Timer(self.timeout, self.resend, [chunks[nextseqnum], nextseqnum, "Timeout"])       
                timer.start()
                self.timers[nextseqnum%(2*self.N)] = timer
                nextseqnum+=1
                # print(base)

            try:
                ack = self.simulator.u_receive()  # receive ACK
                # waitTime.cancel()
                print("ACK RECEIVED: {}, expecting {} ".format(int(ack[:3].decode()), base%(2*self.N)))
                self.logger.info("Got ACK {} from socket, expecting {}".format(int(ack[:3].decode()), base%(2*self.N)))  # note that ASCII will only decode bytes in the range 0-127

                self.logger.info("Full ACK + checksum received: {}".format(ack.decode()))
                check = ack[-9:]
                comp = sexyChecksum(ack[:3].decode())
                # self.logger.info("Checksum: {}, from receiver {}".format(comp, check.decode()))
                if check.decode() != comp:
                    # self.logger.info("Ack was corrupted. Resending packet {}".format(base))
                    self.resend(chunks[base], base, "Corrupted ACK")
                    continue
                
                decAck = int(ack[:3].decode())   # FIXME this could be causing an exception!!!!!
                if decAck == base%(2*self.N): # FIXME: I think theres a race condition, got acks ahead of expected
                    self.timers[base%(2*self.N)].cancel()
                    base+=1
                    # waitTime = threading.Timer(timeout, self.resend, [chunks[nextseqnum], nextseqnum]).start()
                
                
                # elif decAck > base%(2*self.N):
                #     base += decAck-base%(2*self.N)
                # elif decAck < base%(2*self.N):
                #     # print("Resending Packet " + str(base-decAck))
                #     self.resend(chunks[base-decAck], base-decAck)
            except:
                # if nextseqnum-base==5:
                #     self.resend(chunks[base], base) 
                print("No acks received")
                continue

if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read(), encoding='utf8')
    sndr = SexySender()
    sndr.send(DATA)
