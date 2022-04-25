import logging
import socket
import threading
import channelsimulator
import utils
import sys
import time


# data = bytearray(sys.stdin.read())
# # data = sys.stdin.read()
# packetSize = 100
# chunks = [data[i:i+packetSize] for i in range(0, len(data), packetSize)]
# print(chunks)

# def gfg(name):
#     print(name)

# timers = [0]*5
# for i in range(5):
#     timer = threading.Timer(2.0, gfg, [i])
#     timer.start()
#     timers[i] = timer

# print(timers)
# timers[0].cancel()
# timers[0] = threading.Timer(2.0, gfg, [0])
# timers[0].start()
# print(timers)







# import threading
# import time

# def test(i):
#     print(i)
# for i in range(10):
#     threading.Timer(1, test, [i]).start()
#     time.sleep(1e-3)


# TODO: VERY SEXY BACKUP CODE
# def checkSumAdler16(msg):
#     A = 1
#     B = 0
#     lengthOfMsg = len(msg)
    
#     for i in range(lengthOfMsg):
#         A += ord(msg[i])
#         B += A
    
#     A = A%251
#     B = B%251
    
#     adler6969 = B*256 + A
#     return adler6969

# print(checkSumAdler16("PENIS")


    # const int p = 31;
    # const int m = 1e9 + 9;
    # unsigned hash_value = 0;
    # long long p_pow = 1;
    # for (char c : key) {
    #     hash_value = (hash_value + (c - 'a' + 1) * p_pow) % m;
    #     p_pow = (p_pow * p) % m;
    # }
    # return (hash_value % capacity);

def sexyChecksum(data):
    p = 31
    m = 1e9 + 9    
    hash_value = 0 # make unsigned
    p_pow = 1
    
    data = str(data)
    for c in data:
        hash_value = (hash_value + (ord(c) - ord('a') + 1) * p_pow) % m
        p_pow = (p_pow * p) % m

    tmp = hash_value % 9e8
    tmp = int(tmp)
    tmp = str(tmp)
    tmp = "0"*(9-len(tmp)) + tmp
    

    return tmp

print(sexyChecksum("PENIS"))

# print(str(bytes(123)))
# print(sexyChecksum(bytes("penis").decode("ascii")))
# print(sexyChecksum("penit"))
# tmp = "13PerthnWF3cRnA7/pkj6YdiWaUhxUG+d7oN1KmZ+gNQAIRBftLnej6Uvep3hI1/7UHtt0omU2YFv9VOAMEhnPQIiA7YCE3BITN3000"
# tmp = bytearray(tmp, encoding="utf8")
# print(tmp)
# print(tmp.decode())

