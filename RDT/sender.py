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


if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = BogoSender()
    sndr.send(DATA)

class sexySender(BogoSender):
    def __init__(self):
        super(sexySender, self).__init__()

    timers = []

    # FIXME: potential race condition
    def resend(data):
        print("cock")

    def send(self, data):
        N = 5           # Window size
        packetSize = 100        # Size of packets
        chunks = [data[i:i+packetSize] for i in range(0, len(data), packetSize)]    # Dividing data into packets of 100 bytes
        base = 0
        nextseqnum = 0
        timeout = 1
        while True: 
            if nextseqnum < base + N:
                # TODO: add a checksum for bit errors 
                packet = chunks[nextseqnum]
                self.simulator.u_send(packet)  # send data in window of size N
                timer = threading.Timer(timeout, self.resend, [chunks[base:nextseqnum]])        # sending all N in window for now...
                timer.start()
                self.timers.append(timer)
                nextseqnum+=1

            ack = self.simulator.u_receive()  # receive ACK
            if ack == bytes(base): # using the sleep stuff in layth.py guarantees the order, whcih we think fixes this
                base+=1
                self.timers.pop(0)
                







