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

comm = MPI.COMM_WORLD
me = comm.Get_rank()
size = comm.Get_size()

if (me == 0):
    buf = ["coucou"]
    comm.send(buf, dest=me+1, tag=42)
    print("<" + str(me) +"> sent : "+str(buf))
else:
    buf = comm.recv(source=me-1, tag=42)
    print("<" + str(me) +"> recieved : "+str(buf))
    if(me != size-1):
        comm.send(buf, dest=me+1, tag=42)
        print("<" + str(me) +"> sent : "+str(buf))


