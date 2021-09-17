from mpi4py import MPI
import numpy as np
import sys

comm = MPI.COMM_WORLD
me = comm.Get_rank()
size = comm.Get_size()

def getData(msg):
    # split all characters of in an array
    data = [char for char in msg]
    # regroup characters into an array of 'size' arrays of characters
    data = np.array_split(data, size)
    # join every characters of an array
    for i in range(len(data)):
        data[i] = "".join(data[i])

    print("Scattered datas : "+str(data))
    return data

def scatter(_from, msg):
    dataPt = 1

    if (me == _from):
        data = getData(msg)
        for i in range(0, size):
            if i != _from:
                comm.ssend(data[dataPt], dest=i, tag=42)
                print("<"+str(me)+"> sent to <"+str(i)+"> : "+data[dataPt])
                dataPt += 1
        print("<"+str(me)+"> have : "+data[0])
        return data[0]
    
    else:
        mydata = comm.recv(source=_from, tag=42)
        print("<"+str(me)+"> recieved from <"+str(_from)+"> : "+mydata)
        return mydata

def gather(_to, mydata):
    if(me == _to):
        data = mydata
        for i in range(0, size):
            if (me != i):
                data += comm.recv(source=i, tag=42)
                print("<"+str(me)+"> recieved from <"+str(i)+"> : "+data)
        print("\nMessage gathered : " + data)
    
    else:
        comm.send(mydata, dest=_to, tag=42)
        print("<"+str(me)+"> sent to <"+str(_to)+"> : "+mydata)

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        print("\n<"+str(me)+"> SCATTER")
        mydata = scatter(int(sys.argv[1]), sys.argv[2])
        print("\n<"+str(me)+"> GATHER")
        gather(int(sys.argv[1]), mydata)
