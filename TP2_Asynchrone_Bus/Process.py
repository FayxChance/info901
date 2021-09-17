from time import sleep

from pyeventbus3.pyeventbus3 import *

# from EventBus import EventBus
from TP2_Asynchrone_Bus.Message import Message


# from geeteventbus.subscriber import subscriber
# from geeteventbus.eventbus import eventbus
# from geeteventbus.event import event

class Process(Thread):

    def __init__(self, name, cpt):
        Thread.__init__(self)

        self.setName(name)

        PyBus.Instance().register(self, self)

        self.compteur = cpt
        self.alive = True
        self.start()

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Message)
    def receive(self, event):
        if event.dest == self.getName():
            self.compteur = self.compteur + 1 if self.compteur > event.cpt else event.cpt + 1
            print(f"Worker {self.getName()} received message {event.msg}")

    def run(self):
        loop = 0
        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            print(f"{self.getName()} cpt : {self.compteur}")
            sleep(1)

            if self.getName() == "P1":
                b1 = Message(self.compteur, f"Message  {loop}", "P2")
                self.publish(b1)

            loop += 1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.join()

    def publish(self, message):
        self.compteur += 1
        PyBus.Instance().post(Message(message.cpt + 1, message.msg, message.dest))
