from Message import Message, DestinatedMessage, BroadcastMessage, Token, Synchronization
from State import State
from pyeventbus3.pyeventbus3 import *
from time import sleep
import threading

class Com(Thread):
    def __init__(self, clock, process) -> None:
        # Instance of bus listener
        Thread.__init__(self)
        self.setName(process.me)
        PyBus.Instance().register(self, self)

        # Self parameters
        self.owner = process.me
        self.receivers = process.receivers
        self.clock = clock
        self.sem = threading.Semaphore()
        self.mailbox = []
        self.process = process

        # Starting to listen the bus
        self.alive = True
        self.start()

    def stop(self):
        self.alive = False
        self.join()

    def __inc_clock(self):
        self.sem.acquire()
        self.clock += 1
        self.sem.release()

    def __get_name(self):
        """
            Transform a str getName() into an int
        """
        return int(self.getName())


    # FIFO Mailbox
    def getFirstMessage(self) -> Message:
        return self.mailbox.pop(0)

    def __addMessageToMailbox(self, msg: Message):
        self.mailbox.append(msg)


    # Asynchronous communication methods
    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        """
            Read the message on the bus
        """
        if event.src != self.__get_name():
            if self.clock > event.stamp:
                self.__inc_clock()
            else:
                self.clock = event.stamp
            self.__addMessageToMailbox(event)
            print(f"Worker {self.__get_name()} received broadcasted message {event.payload}")

    def broadcast(self, payload: object):
        """
            Send a message on the bus to everyone
        """
        self.__inc_clock()
        PyBus.Instance().post(BroadcastMessage(src=self.__get_name(), payload=payload, stamp=self.clock))


    @subscribe(threadMode=Mode.PARALLEL, onEvent=DestinatedMessage)
    def onReceive(self, event):
        """
            Find a message of type Message on the bus
            If i'm the reciever i read the message
        """
        if event.dest == self.__get_name():
            if self.clock > event.stamp:
                self.__inc_clock()
            else:
                self.clock = event.stamp
            self.__addMessageToMailbox(event)
            print(f"Worker {self.__get_name} received message {event.payload}")

    def sendTo(self, payload, dest: int):
        """
            Send a message on the bus to a specific receiver (dest)
        """
        self.__inc_clock()
        PyBus.Instance().post(DestinatedMessage(src=self.__get_name(), payload=payload, dest=dest, stamp=self.clock))


    # Token
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def on_token(self, event):
        """
            Find a Token on the bus
            If i'm the reciever and i'm in request state, then i get the Token and set state to Critical Section (SC)
            I can use the Token i get the release state
            Then i send the Token to the next process
        """
        if self.__get_name() == event.dest and self.process.alive:
            # sleep(1)
            if self.process.state == State.REQUEST:
                self.process.state = State.SC
                while self.process.state != State.RELEASE:
                    sleep(1)
            self.sendTokenTo(Token((event.dest + 1) % (len(self.receivers)+1)))
            self.process.state = State.NONE

    def requestSC(self):
        """Set state to request and wait for a Token"""
        self.process.state = State.REQUEST
        while self.process.state != State.SC:
            sleep(1)

    def releaseSC(self):
        """Set state to release"""
        self.process.state = State.RELEASE

    def sendTokenTo(self, token: Token):
        """
            Send a token on the bus to the next receiver (dest)
        """
        PyBus.Instance().post(token)



    # Synchronization
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Synchronization)
    def onSynchronize(self, event):
        """
            Find a message of type Synchronization
            If not the message sender, then decrement a counter
        """
        if event.src != self.get_name():
            self.process.cptSynchronize -= 1

    def synchronize(self):
        """
            Send a message of type Synchronization on the bus
            and wait for my counter to reach 0

            Reaching 0 means that every process is in synchronization
        """
        PyBus.Instance().post(Synchronization(self.get_name()))
        while self.process.cptSynchronize > 0:
            sleep(1)
        self.process.cptSynchronize = len(self.receivers)-1
    ###
    