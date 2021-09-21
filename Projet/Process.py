from pyeventbus3.pyeventbus3 import *
from Message import Token
from Com import Com
from time import sleep

class Process(Thread):
    def __init__(self, me, receivers):
        # Instance of bus listener
        Thread.__init__(self)
        self.setName(me)
        PyBus.Instance().register(self, self)

        # Self parameters
        self.me = me
        self.receivers = receivers

        self.state = None
        self.com = Com(0, self)

        # Starting to listen the bus
        self.alive = True
        self.start()

    def stop(self):
        self.alive = False
        self.com.stop()
        self.join()

    def run(self):
        loop = 0
        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            
            sleep(1)

            # # Broadcast
            # if(loop == 2):
            #     self.com.broadcast("bonjour")

            # if(loop == 4):
            #     print(self.com.getFirstMessage().payload)

            # # Send to
            # if(loop == 2 and self.me == 1):
            #     self.com.sendTo("bonjour", self.receivers[0])
            
            # if(loop == 4 and self.me == 2):
            #     print(self.com.getFirstMessage().payload)

            # Token
            if(loop == 0 and self.me == 3):
                t = Token(1)
                self.com.sendTokenTo(t)

            if(loop == 2 and self.me == 0):
                self.com.requestSC()
                print("enterin CS")
                sleep(2)
                print("leaving CS")
                self.com.releaseSC()

            
            loop += 1
        print(self.getName() + " stopped")