# Written by S. Mevawala, modified by Husam Almanakly and Layth Yassin

import logging

import channelsimulator
import utils
import sys
import socket
from checksum import sexyChecksum

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
                # self.logger.info("Got data from socket: {}".format(data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                sys.stdout.write(data)
                self.simulator.u_send(BogoReceiver.ACK_DATA)  # send ACK
            except:
                pass


class SexyReceiver(Receiver):
    def __init__(self):
        super(SexyReceiver, self).__init__()
    
    N = 5       # Window size

    def receive(self):
        packetSeen = 0
        packetSize = 100
        nextseqnum = 0
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True: 
            try:    
                data = self.simulator.u_receive()  # receive possibly corrupted data
                # self.logger.info("Full data received: {}".format(data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                # self.logger.info("Received packet with data: {}".format(data.decode()))
                packetseq = data[-12:-9]
                # self.logger.info("Expecting Packet #: {}".format(nextseqnum))
                # self.logger.info("COMPARISON: {}".format(nextseqnum == int(packetseq.decode("ascii"))))
                try:
                    decSeq = int(packetseq.decode())
                except:
                    continue
                
                check = data[-9:]
                comp = sexyChecksum(data[:-9])
                # self.logger.info("Data received: {}".format(data))
                # self.logger.info("Checksums: receiver - {}, sender {}".format(comp, check))
                if comp != check: # checks if data is corrupted
                    self.logger.info("Data was corrupted. Resending ack {}".format(nextseqnum-1))
                    self.simulator.u_send(bytearray(str(nextseqnum-1), encoding="utf8"))  # send ACK
                    continue
                    
                #If we get here then the data is not corrupted
                if nextseqnum == decSeq:
                    self.logger.info("Sending ack {}".format(nextseqnum))
                    sys.stdout.write(data[:-12])

                    #Make a checksum for the ack packet
                    check = sexyChecksum(str(packetseq))
                    packet = str(packetseq) + check
                    self.simulator.u_send(bytearray(packet, encoding='utf8'))  # send ACK
                    
                    nextseqnum += 1
                    packetSeen+=1
                    nextseqnum = nextseqnum%self.N
                else:
                    self.logger.info("Out of order. Resending ack {}".format(nextseqnum-1))
                    self.simulator.u_send(bytearray(str(nextseqnum-1), encoding="utf8"))  # send ACK
                    continue
            except socket.timeout:
                sys.exit()


if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = SexyReceiver()
    rcvr.receive()