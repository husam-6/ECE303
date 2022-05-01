# Written by S. Mevawala, modified by Husam Almanakly and Layth Yassin

import logging

import channelsimulator
import utils
import sys
import socket
from checksum import sexyChecksum, window
import threading

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
    
    N = window       # Window size
    packetSize = 2*window

    def receive(self):
        # packetSize = 100
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))

        nextseqnum = 0

        while True: 
            try:    
                data = self.simulator.u_receive()  # receive possibly corrupted data

                #Theres some error when swaps occur
                try: 
                    self.logger.info("Received packet with data: {}".format(data.decode()))
                except: 
                    continue
                packetseq = data[-14:-9]
                self.logger.info("Sequence number: {}".format(packetseq.decode()))
                decSeq = int(packetseq.decode())
                
                #check for corruption
                check = data[-9:]
                comp = sexyChecksum(data[:-9])
                if comp != check: # checks if data is corrupted
                    # tmp = (nextseqnum-1)%(2*self.N)
                    # #might not have to resend ack
                    # self.logger.info("Data was corrupted. Resending ack {}".format(tmp))
                    # tmp = str(tmp)
                    # tmp = "0"*(3-len(tmp)) + tmp
                    # check = sexyChecksum(tmp)
                    # self.simulator.u_send(bytes(tmp+check, encoding="utf8"))  # send ACK
                    continue
                
                if nextseqnum == decSeq:
                    #Make a checksum for the ack packet
                    self.logger.info("Sending ack {}".format(decSeq))
                    check = sexyChecksum(str(packetseq))
                    packet = str(packetseq) + check
                    self.simulator.u_send(bytes(packet))  # send ACK
                    nextseqnum+=1

                    #write output 
                    sys.stdout.write(data[:-14])


                else: 
                    self.logger.info("Out of order... Received # {} but expected {}".format(decSeq, nextseqnum))
                    tmp = (nextseqnum-1)
                    tmp = str(tmp)
                    tmp = "0"*(5-len(tmp)) + tmp
                    check = sexyChecksum(tmp)
                    self.simulator.u_send(bytearray(tmp+check, encoding="utf8"))  # send ACK
                    continue
                
                
                

            except socket.timeout:
                sys.exit()


if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = SexyReceiver()
    rcvr.receive()