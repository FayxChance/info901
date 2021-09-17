import math
import sys

from mpi4py import MPI

comm = MPI.COMM_WORLD
me = comm.Get_rank()
size = comm.Get_size()


class Message:
    msg = ""
    step = None

    def __init__(self, msg, step, fr):
        self.msg = msg
        self.step = step
        self.fr = fr


def broadcast_hypercube(fr, msg):
    higher_step = math.ceil(math.log2(size))
    message = None
    if fr == me:
        message = Message(msg, 0, me)
    else:
        message = comm.recv(source=MPI.ANY_SOURCE)
        print(f"Worker {me} message {message.msg} received from {message.fr} ")
    for i in range(message.step, higher_step):
        next = (me + 2 ** i) % size
        if next < size:
            comm.send(Message(message.msg, i+1, me), next)


if __name__ == '__main__':
    broadcast_hypercube(int(sys.argv[1]), sys.argv[2])
