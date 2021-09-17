import sys

from mpi4py import MPI

comm = MPI.COMM_WORLD
me = comm.Get_rank()
size = comm.Get_size()


def broadcast_anneau2_sens(fr, msg):
    middle = (size / 2 + fr) % size
    if me == fr:
        comm.send(msg, (fr + 1) % size, 99)
        comm.send(msg, (fr - 1) % size, 99)
    else:
        if size % 2 == 0:
            if me <= middle:
                buff = comm.recv(source=(me - 1) % size, tag=99)
                print("Worker " + str(me) + "says " + str(buff))
                if me != middle:
                    comm.send(obj=buff, dest=(me + 1) % size, tag=99)
            else:
                buff = comm.recv(source=(me + 1) % size, tag=99)
                print("Worker " + str(me) + "says " + str(buff))
                if me > middle + 1:
                    comm.send(obj=buff, dest=(me - 1) % size, tag=99)


if __name__ == '__main__':
    broadcast_anneau2_sens(int(sys.argv[1]), sys.argv[2])
