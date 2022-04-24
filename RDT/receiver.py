# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoReceiver(Receiver):
    ACK_DATA = bytes(123)

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                data = self.simulator.u_receive()  # receive data
                self.logger.info("Got data from socket: {}".format(data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                sys.stdout.write(data)
                self.simulator.u_send(BogoReceiver.ACK_DATA)  # send ACK
            except socket.timeout:
                sys.exit()


class SexyReceiver(Receiver):
    def __init__(self):
        super(SexyReceiver, self).__init__()
    
    N = 5       # Window size

    def receive(self):
        packetSize = 100
        nextseqnum = 0
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True: 
            try:    
                data = self.simulator.u_receive()  # receive possibly corrupted data
                self.logger.info("Got sequence number: {}. Full data received: {}".format(data[-3:], data))  # note that ASCII will only decode bytes in the range 0-127
            except socket.timeout:
                sys.exit()

            packetseq = data[-3:]
            if nextseqnum == int(packetseq):
                sys.stdout.write(data[:-3])
                self.simulator.u_send(bytes(packetseq))  # send ACK
                nextseqnum += 1
                nextseqnum = nextseqnum%self.N
            else:
                self.logger.info("Out of order. Resending ack {}".format(nextseqnum-1))
                self.simulator.u_send(bytes(nextseqnum-1))  # send ACK



if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = SexyReceiver()
    rcvr.receive()