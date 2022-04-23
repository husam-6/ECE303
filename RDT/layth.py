# import sys
# import time
# import threading

# # data = sys.stdin.read()
# # packetSize = 100
# # chunks = [data[i:i+packetSize] for i in range(0, len(data), packetSize)]
# def gfg(name):
#     print(name)

# timers = []
# for i in range(5):
#     timer = threading.Timer(2.0, gfg, [i])
#     timer.start()
#     timers.append(timer)

# print(timers)

# timers[0].cancel()
# timers.pop(0)
# print(timers)
# # print("Cancelling timer\n")
# # timer.cancel()
# # print("Exit\n")





import threading
import time

def test(i):
    print(i)
for i in range(10):
    threading.Timer(1, test, [i]).start()
    time.sleep(1e-3)