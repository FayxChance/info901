from Process import Process
from time import sleep

if __name__ == "__main__":
    processes = []
    receivers = [0,1,2,3]
    for i in receivers:
        r = receivers.copy()
        r.remove(i)
        p = Process(i, r)
        processes.append(p)

    sleep(20)

    for p in processes:
        p.stop()
