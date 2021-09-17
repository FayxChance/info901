from time import sleep
from Process import Process

if __name__ == '__main__':

    #bus = EventBus.getInstance()

    p1 = Process(0, 4, None)
    p2 = Process(1, 10, None)
    p3 = Process(2, 10, None)

    sleep(15)

    p1.stop()
    p2.stop()
    p3.stop()

    #bus.stop()
