# void BCast(from, msg) {
#     if (myId == from) {
#         for (i = 0; i < nbNodes-1; i++ ) {
#             if (i != from)
#                 send(i, msg)
#         }
#     } else {
#         recieve(from, msg)
#     }
# }

from mpi4py import MPI
import sys

comm = MPI.COMM_WORLD
me = comm.Get_rank()
size = comm.Get_size()

def broadcast(_from, msg):
    if me == _from:
        print("<"+str(me)+">: send " + msg)
        for i in range(0, size):
            if (i != _from):
                comm.ssend(msg, dest=i, tag=99)
    else:
        buf = comm.recv(source=_from, tag=99)
        print("<"+str(me)+">: receive " + buf[0])

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        broadcast(int(sys.argv[1]), sys.argv[2])