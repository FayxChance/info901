# void diffusionAnneau(from, msg) {
#     last = (from + nbNodes-1) % nbNodes
#     next = myId + 1 % nbNodes
#     prev = (myId - 1 + nbNodes) % nbNodes

#     if (myId == from) {
#         send(next, msg)
#     } else {
#         recieve(prev, msg)
#         if (myId != last)
#             send(next, msg)
#     }
# }


from mpi4py import MPI
import sys

comm = MPI.COMM_WORLD
me = comm.Get_rank()
size = comm.Get_size()

def broadcast(_from, msg):

    last = (_from + size-1) % size
    next = (me + 1) % size
    prev = (me - 1 + size) % size

    if (me == _from):
        comm.send(msg, dest=next, tag=42)
        print("<" + str(me) +"> sent : "+str(msg))
    else:
        buf = comm.recv(source=prev, tag=42)
        print("<" + str(me) +"> recieved : "+str(buf))
        if(me != last):
            comm.send(buf, dest=next, tag=42)
            print("<" + str(me) +"> sent : "+str(buf))

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        broadcast(int(sys.argv[1]), sys.argv[2])
