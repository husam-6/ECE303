# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket
import threading
import channelsimulator
import utils
import sys
import time

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
                self.logger.info("Got ACK from socket: {}".format(ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass

class SexySender(Sender):

    def __init__(self):
        super(SexySender, self).__init__()

    timers = [0]*5

    N = 5           # Window size
    def makePacket(self, data, nextseqnum):
        #Ensure sequence number is 3 bytes (zero pad)
        tmp = str(nextseqnum%self.N)
        while len(tmp) < 3:
            tmp = "0" + tmp
        return data + tmp

    # FIXME: potential race condition
    def resend(self, data, base, nextseqnum):
        for i in range(base, nextseqnum+1):
            item = data[base]
            tmp = self.makePacket(item, i)
            print("RESENDING DATA: {}".format(i))
            self.simulator.u_send(tmp)  # resend data
            self.logger.info("Resending packet: {}, seqnum: {}.".format(i, i%self.N))

    def send(self, data):
        packetSize = 100        # Size of packets
        chunks = [data[i:i+packetSize] for i in range(0, len(data), packetSize)]    # Dividing data into packets of 100 bytes
        base = 0
        nextseqnum = 0
        timeout = 1
        # waitTime = threading.Timer(2*timeout, self.resend, [chunks, base, nextseqnum]).start()
        while True:
            print("base: {}, nextseq #: {}".format(base, nextseqnum))
            if base == len(chunks):
                break
            if nextseqnum < base + self.N:
                # TODO: add a checksum for bit errors
                packet = self.makePacket(chunks[nextseqnum], nextseqnum)
                self.simulator.u_send(packet)  # send data in window of size N
                self.logger.info("Sending packet: {} with seqnum: {}".format(nextseqnum, nextseqnum%self.N))
                timer = threading.Timer(timeout, self.resend, [chunks, base, nextseqnum])        # sending all N in window for now...
                timer.start()
                self.timers[nextseqnum%self.N] = timer
                nextseqnum+=1
                # print(base)

            try:
                ack = self.simulator.u_receive()  # receive ACK
                # waitTime.cancel()
                print("ACK RECEIVED: {}, expecting {} ".format(ack.decode('ascii'), base%self.N))
                if int(ack.decode('ascii')) == base%self.N: # FIXME: possible need to worry about > condition if not handled correctly in receiver
                    self.timers[base%self.N].cancel()
                    self.logger.info("Got ACK {} from socket".format(ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                    base+=1
                # elif int(ack.decode('ascii')) < base%self.N:
                #     self.resend(chunks, base, nextseqnum)
                # else:
                #     waitTime = threading.Timer(2*timeout, self.resend, [chunks, base, nextseqnum]).start()
            except: 
                print("No acks received")
                continue

if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = SexySender()
    sndr.send(DATA)
