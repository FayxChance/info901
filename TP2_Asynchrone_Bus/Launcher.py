from time import sleep
from Process import Process

if __name__ == '__main__':

    #bus = EventBus.getInstance()

    p1 = Process(1, 4, None)
    p2 = Process(2, 10, None)
    p3 = Process(3, 10, None)

    sleep(5)

    p1.stop()
    p2.stop()
    p3.stop()

    #bus.stop()
