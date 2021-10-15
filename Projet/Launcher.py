from Process import Process
from time import sleep
import sys

if __name__ == "__main__":
    print('Number of arguments: ' + str(len(sys.argv)))
    print('Argument List: ' + str(sys.argv))

    processes = []
    leader = False
    for i in range(6):
        p = Process(sys.argv)
        if not leader:
            sleep(5)
            leader = True
        processes.append(p)

    sleep(20)

    for p in processes:
        p.stop()
