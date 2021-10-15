from Process import Process
from time import sleep
import sys

if __name__ == "__main__":
    print('Number of arguments: ' + str(len(sys.argv)))
    print('Argument List: ' + str(sys.argv))

    processes = []
    receivers = [0,1,2,3]
    for i in receivers:
        r = receivers.copy()
        r.remove(i)
        p = Process(i, r, sys.argv)
        processes.append(p)

    sleep(2)

    for p in processes:
        p.stop()
