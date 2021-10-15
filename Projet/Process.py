from sys import argv
from threading import Thread

from pyeventbus3.pyeventbus3 import *
from Message import Token
from Com import Com
from time import sleep

class Process(Thread):
    def __init__(self, me, receivers, argv):
        # Instance of bus listener
        Thread.__init__(self)
        self.setName(me)
        PyBus.Instance().register(self, self)

        # Self parameters
        self.me = me
        self.receivers = receivers
        self.argv = argv


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
            
            # Switch case for tests
            {
                'broadcast': self.broadcast(loop),
                'sendTo ': self.sendTo(loop, self.argv[2]) if len(self.argv) >= 3 else self.sendTo(loop, 2),
                'token': self.token(loop),
                'synchronize': self.synchronize(loop),
                'sync_bcast': self.sync_bcast(loop),
                'sync_sendto': self.sync_sendto(loop, self.argv[2]) if len(self.argv) >= 3 else self.sync_sendto(loop, 2)
            }[self.argv[1]]
            
            loop += 1
        print(self.getName() + " stopped")


### Asynchronous communication tests
    def broadcast(self, loop):
        # Broadcast test
        if(loop == 2 and self.me == 0):
            self.com.broadcast("bonjour")

        if(loop == 4):
            if len(self.com.mailbox) > 0:
                print(self.com.getFirstMessage().payload)

    def sendTo(self, loop, to):
        # Send to test
        if(loop == 2 and self.me == 0):
            self.com.sendTo("bonjour", to)
        
        if(loop == 4 and self.me == to):
            if len(self.com.mailbox) > 0:
                print(self.com.getFirstMessage().payload)

    def token(self, loop):
        # Token test
        if(loop == 0 and self.me == 3):
            t = Token(1)
            self.com.sendTokenTo(t)

        if(loop == 2 and self.me == 0):
            self.com.requestSC()
            print("enterin CS")
            sleep(2)
            print("leaving CS")
            self.com.releaseSC()

    def synchronize(self, loop):
        # Synchronize test
        if (loop == 2 and self.me == 0):
            self.com.synchronize()

        if (loop == 4 and self.me == 1):
            self.com.synchronize()

        if (loop == 6 and self.me == 2):
            self.com.synchronize()

        if (loop == 8 and self.me == 3):
            self.com.synchronize()

### Synchonous communication tests
    def sync_bcast(self, loop):
        # Synchronized broadcast test
        # The first process send a message and wait for the other process to receive it
        if (loop == 2 and self.me == 0):
            self.com.broadcastSync(self.me, "coucou")
        
        # The process 1 check if he received it and wait for everyone to receive it
        if(loop == 4 and self.me == 1):
            self.com.broadcastSync(0)
            print(self.com.getFirstMessage())

        # The other process receive the message and unlock everyone
        if(loop == 10 and self.me != 0 and self.me != 1):
            self.com.broadcastSync(0)
            print(self.com.getFirstMessage())
    
    def sync_sendto(self, loop, to):
        # Synchronized send to test
        if loop == 2 and self.me == 0:
            self.com.sendToSync(to, "Bonjour !")

        if loop == 6 and self.me == to:
            self.com.receivFromSync()
            print(self.com.getFirstMessage().payload)

        if loop == 8 and self.me == to:
            self.com.receivFromSync()
            print(f"message received : {self.com.getFirstMessage().payload}")

        if loop == 12 and self.me == 0:
            self.com.sendToSync(to, "Bonjour !")
