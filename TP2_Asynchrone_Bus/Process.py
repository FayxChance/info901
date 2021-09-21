from time import sleep

from pyeventbus3.pyeventbus3 import *

from BroadcastMessage import BroadcastMessage
# from EventBus import EventBus
from Message import Message
from Synchronization import Synchronization
from Token import Token

# from geeteventbus.subscriber import subscriber
# from geeteventbus.eventbus import eventbus
# from geeteventbus.event import event

BROADCAST = "BROADCAST"
size = 3


class Process(Thread):
    # VARS
    # Synchronize
    cptSynchronize = size - 1

    def __init__(self, name, cpt, state):
        Thread.__init__(self)

        self.setName(name)

        PyBus.Instance().register(self, self)

        # ATTRIBUTS
        # Lamport
        self.compteur = cpt
        # Section Critique
        self.state = None
        self.alive = True
        self.start()

    def get_name(self):
        """
            Transform a str getName() into an int
        """
        return int(self.getName())

    ############################   LAMPORT + BROADCAST   ############################
    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def on_broadcast(self, event):
        """
            Read the message of type BroadcastMessage on the bus
        """
        if event.src != self.get_name():
            self.compteur = self.compteur + 1 if self.compteur > event.cpt else event.cpt + 1
            print(f"Worker {self.get_name()} received broadcasted message {event.msg}")

    def broadcast(self, message):
        """
            Send a message of type BroadcastMessage on the bus
        """
        self.compteur += 1
        PyBus.Instance().post(BroadcastMessage(message.cpt + 1, message.msg, message.src))

    ############################   LAMPORT + DEDICATED   ############################
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Message)
    def on_receive(self, event):
        """
            Find a message of type Message on the bus
            If i'm the reciever i read the message
        """
        if event.dest == self.get_name():
            self.compteur = self.compteur + 1 if self.compteur > event.cpt else event.cpt + 1
            print(f"Worker {self.get_name()} received message {event.msg}")

    def send_to(self, obj):
        """
            Send a message of type Message on the bus to a specific reciever
        """
        self.compteur += 1
        PyBus.Instance().post(obj)

    ############################   TOKEN   ############################
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def on_token(self, event):
        """
            Find a Token on the bus
            If i'm the reciever and i'm in request state, then i get the Token and set state to Critical Section (SC)
            I can use the Token i get the release state
            Then i send the Token to the next process
        """
        if self.get_name() == event.dest and self.alive:
            sleep(1)
            print(f"found token in {self.getName()}")
            if self.state == "request":
                print("i'm on request going on SC")
                self.state = "SC"
                while self.state != "release":
                    sleep(1)
            self.send_to(Token(event.id, (event.dest + 1) % 3))
            print(f"token sent to next which is {(self.get_name() + 1) % 3}")
            self.state = None

    def request(self):
        """Set state to request and wait for a Token"""
        self.state = "request"
        while self.state != "SC":
            sleep(1)

    def release(self):
        """Set state to release"""
        self.state = "release"

    ############################   SYNCHRONIZE   ############################
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Synchronization)
    def onSynchronize(self, event):
        """
            Find a message of type Synchronization
            If not the message sender, then decrement a counter
        """
        if event.src != self.get_name():
            self.cptSynchronize -= 1

    def synchronize(self):
        """
            Send a message of type Synchronization on the bus
            and wait for my counter to reach 0

            Reaching 0 means that every process is in synchronization
        """
        PyBus.Instance().post(Synchronization(self.get_name()))
        while self.cptSynchronize > 0:
            sleep(1)

    ############################   RUN   ############################
    def run(self):
        loop = 0
        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            # print(f"{self.get_Name()} cpt : {self.compteur}")
            sleep(1)

            # # First process creates a Token at first loop
            # if self.get_Name() == 0 and loop == 0:
            #     t = Token("abcdefghijklmnopqrstuvwxyz", 1)
            #     print("created token : " + str(t))
            #     self.sendTo(t)

            # Send a message of type Message to the 2nd and 3rd process only
            # if self.get_Name() == 1:
            # b1 = Message(self.compteur, f"Message  {loop}", 2)
            # self.sendTo(b1, 2)
            # self.sendTo(b1, 3)
            # self.broadcast(BroadcastMessage(self.compteur, f"Broadcasted message  {loop}", 1))

            # Requesting token
            # if loop == 2:
            #     if self.get_Name() == 1:
            #         self.request()
            #         print("token SC")
            #         sleep(2)
            #         print("releasing the beast !")
            #         self.release()

            if self.get_name() == 1 and loop == 0:
                sleep(5)
            elif self.get_name() == 2 and loop == 0:
                sleep(10)
            if loop == 6:
                self.synchronize()

            loop += 1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.join()
