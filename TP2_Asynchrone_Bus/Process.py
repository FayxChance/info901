from time import sleep

from pyeventbus3.pyeventbus3 import *

from BroadcastMessage import BroadcastMessage
# from EventBus import EventBus
from Message import Message
from Token import Token

# from geeteventbus.subscriber import subscriber
# from geeteventbus.eventbus import eventbus
# from geeteventbus.event import event

BROADCAST = "BROADCAST"


class Process(Thread):

    def __init__(self, name, cpt, state):
        Thread.__init__(self)

        self.setName(name)

        PyBus.Instance().register(self, self)

        self.compteur = cpt
        self.alive = True
        self.state = None
        self.start()

    def get_Name(self):
        return int(self.getName())

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Message)
    def onReceive(self, event):
        if event.dest == self.get_Name():
            self.compteur = self.compteur + 1 if self.compteur > event.cpt else event.cpt + 1
            print(f"Worker {self.get_Name()} received message {event.msg}")

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        if event.src != self.get_Name():
            self.compteur = self.compteur + 1 if self.compteur > event.cpt else event.cpt + 1
            print(f"Worker {self.get_Name()} received broadcasted message {event.msg}")


    def run(self):
        loop = 0
        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            # print(f"{self.get_Name()} cpt : {self.compteur}")
            sleep(1)

            # Creating token
            if self.get_Name() == 1 and loop == 0:
                t = Token("abcdefghijklmnopqrstuvwxyz")
                print("created token : "+str(t))
                self.sendTokenTo(t, (self.get_Name()+1)%3 )

            if self.get_Name() == 1:
                b1 = Message(self.compteur, f"Message  {loop}", 2)
                self.sendTo(b1, 2)
                # self.sendTo(b1, 3)
                # self.broadcast(BroadcastMessage(self.compteur, f"Broadcasted message  {loop}", 1))
            
            # Requesting token
            if loop == 2:
                if self.get_Name() == 1:
                    self.request()
                    print("token SC")
                    sleep(2)
                    print("releasing the beast !")
                    self.release()

            loop += 1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.join()

    def sendTo(self, message, to):
        self.compteur += 1
        PyBus.Instance().post(Message(message.cpt + 1, message.msg, to))

    def sendTokenTo(self, token, to):
        self.compteur += 1
        PyBus.Instance().post(token)

    def broadcast(self, message):
        self.compteur += 1
        PyBus.Instance().post(BroadcastMessage(message.cpt + 1, message.msg, message.src))

    # TOKEN
    def request(self):
        self.state = "request"
        while(self.state != "SC"):
            sleep()

    def release(self):
        self.state = "release"

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def onToken(self, event):
        print("found token")
        sleep(.5)
        if self.state == "request":
            print("i'm on request going on SC")
            self.state = "SC"
            while (self.state != "release"):
                sleep()
        self.sendTokenTo(event, (self.get_Name()+1)%3 )
        print("token sent to next")
        self.state = None