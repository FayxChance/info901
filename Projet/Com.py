import threading
from time import sleep

from pyeventbus3.pyeventbus3 import *

from Message import *
from State import State


class Com(Thread):
    def __init__(self, clock, process) -> None:
        # Instance of bus listener
        Thread.__init__(self)
        self.setName(process.me)
        PyBus.Instance().register(self, self)

        # Self parameters
        self.owner = process.me
        self.clock = clock
        self.sem = threading.Semaphore()
        self.mailbox = []
        self.process = process

        self.leaderPresent = False

        self.cptSynchronize = 0
        self.messageReceived = False

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

    def get_name(self):
        """
            Transform a str getName() into an int
        """
        return self.owner.numero

    # FIFO Mailbox
    def getFirstMessage(self) -> Message:
        return self.mailbox.pop(0)

    def __addMessageToMailbox(self, msg: Message):
        self.mailbox.append(msg)

    ### Asynchronous communication methods
    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        """
            Read the message on the bus
        """
        if event.src != self.owner:
            sleep(1)
            if self.clock > event.stamp:
                self.__inc_clock()
            else:
                self.clock = event.stamp
            if event not in self.mailbox:
                self.__addMessageToMailbox(event)
            print(f"Worker {self.get_name()} received broadcasted message {event.payload}")
            sleep(1)

    def broadcast(self, payload: object):
        """
            Send a message on the bus to everyone
        """
        self.__inc_clock()
        PyBus.Instance().post(BroadcastMessage(src=self.get_name(), payload=payload, stamp=self.clock))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=DestinatedMessage)
    def onReceive(self, event):
        """
            Find a message of type Message on the bus
            If i'm the reciever i read the message
        """
        if event.dest == self.get_name():
            if self.clock > event.stamp:
                self.__inc_clock()
            else:
                self.clock = event.stamp
            self.__addMessageToMailbox(event)
            print(f"Worker {self.get_name()} received message {event.payload}")

    def sendTo(self, payload, dest: int):
        """
            Send a message on the bus to a specific receiver (dest)
        """
        self.__inc_clock()
        PyBus.Instance().post(DestinatedMessage(src=self.get_name(), payload=payload, dest=dest, stamp=self.clock))

    # Token
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def on_token(self, event):
        """
            Find a Token on the bus
            If i'm the reciever and i'm in request state, then i get the Token and set state to Critical Section (SC)
            I can use the Token i get the release state
            Then i send the Token to the next process
        """
        if self.get_name() == event.dest and self.process.alive:
            # sleep(1)
            if self.process.state == State.REQUEST:
                self.process.state = State.SC
                while self.process.state != State.RELEASE:
                    sleep(1)
            self.sendTokenTo(Token((event.dest + 1) % (len(self.owner.annuaire))))
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
        if event.src != self.owner:
            self.cptSynchronize -= 1

    def synchronize(self):
        """
            Send a message of type Synchronization on the bus
            and wait for my counter to reach 0

            Reaching 0 means that every process is in synchronization
        """
        PyBus.Instance().post(Synchronization(src=self.owner.numero, stamp=self.clock))
        while self.cptSynchronize > 0:
            sleep(1)
        self.cptSynchronize = len(self.owner.annuaire)

    ### Synchronous communication methods
    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessageSync)
    def onBroadcastSync(self, event):
        if event.src != self.owner:
            if self.clock > event.stamp:
                self.__inc_clock()
            else:
                self.clock = event.stamp
            self.__addMessageToMailbox(event)
            self.messageReceived = True

    def broadcastSync(self, _from: int, payload: object = None):
        if self.owner.numero == _from:
            # broadcast the object
            if payload is not None:
                self.__inc_clock()
                PyBus.Instance().post(BroadcastMessageSync(src=_from, payload=payload, stamp=self.clock))
            print("message sent")
            # wait until everyone gets it
            self.synchronize()
        else:
            # wait for the message
            while not self.messageReceived:
                sleep(1)
            # notify everyone i received it
            print("message received")
            self.synchronize()
            self.messageReceived = False

    @subscribe(threadMode=Mode.PARALLEL, onEvent=DestinatedMessageSync)
    def receiveMessageSync(self, event):
        if event.dest == self.owner.numero:
            if self.clock > event.stamp:
                self.__inc_clock()
            else:
                self.clock = event.stamp
            self.messageReceived = True
            self.__addMessageToMailbox(event)

    def receivFromSync(self):
        print("waiting for message")
        while not self.messageReceived :
            sleep(1)
        lastMessage = self.mailbox[len(self.mailbox) - 1]
        PyBus.Instance().post(MessageReceivedSync(src=self.owner.numero, dest=lastMessage.src, stamp=self.clock))
        self.messageReceived = False

    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageReceivedSync)
    def destReceivedMessage(self, event):
        if event.dest == self.owner.numero:
            print("dest received message")
            if self.clock > event.stamp:
                self.__inc_clock()
            else:
                self.clock = event.stamp
            self.messageReceived = True

    def sendToSync(self, _to: int, payload: object):
        self.__inc_clock()
        PyBus.Instance().post(DestinatedMessageSync(src=self.owner.numero, payload=payload, dest=_to, stamp=self.clock))
        print("message sent")
        while not self.messageReceived:
            sleep(1)
        self.messageReceived = False

    ############################   NUMEROTATION   ############################
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Numerotation)
    def onNumerotation(self, event):
        """
            If receiving the numerotation message, send a numerotation back if I am the leader
        """
        if self.owner.AmILeader:
            PyBus.Instance().post(NumerotationBack(event.pid))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=NumerotationBack)
    def onNumerotationBack(self, event):
        """
            The leaders answer
        """
        if event.pid == self.owner.pid:
            self.leaderPresent = True

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Leader)
    def onLeader(self, event):
        """
            When a leader is elected, send my self.pid to the leader
        """
        if event.pid != self.owner.pid:
            self.owner.pidLeader = event.pid
            PyBus.Instance().post(AddAnnuaire(self.owner.pid))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=AddAnnuaire)
    def onAddAnnuaire(self, event):
        """
            When the leader received a AddAnnuaire meesage, it adds the message sender to the annuaire and update all annuaire of everyone
        """
        if self.owner.AmILeader:
            self.owner.annuaire[event.pid] = len(self.owner.annuaire) + 1
            PyBus.Instance().post(UpdateAnnuaire(self.owner.annuaire))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=UpdateAnnuaire)
    def onUpdateAnnuaire(self, event):
        """
            When a process receives from the leader UpdateAnnuaire, it takes the annuaire passed in the message
        """
        if not self.owner.AmILeader:
            self.owner.annuaire = event.annuaire
            self.owner.numero = self.owner.annuaire[self.owner.pid]

    def numerotation(self):
        """
            Every process with id 1.
            Send a numerotation message on the bus, if processes respond. Increments its own number.
        """
        PyBus.Instance().post(Numerotation(self.owner.pid))
        time.sleep(2)
        if not self.leaderPresent:
            self.owner.AmILeader = True
            self.owner.numero = 0
            self.owner.pidLeader = self.owner.pid
            PyBus.Instance().post(Leader(self.owner.pid))
        else:
            PyBus.Instance().post(AddAnnuaire(self.owner.pid))
