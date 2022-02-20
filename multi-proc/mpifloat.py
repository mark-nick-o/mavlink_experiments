#
# Example to send the information using MPI between 2 process ranks
#
# https://keichi.dev/post/mpi4py/
# https://np2lkoo.hatenablog.com/entry/2020/11/07/221119
#
#
# run program as :- mpirun -np 2 python3 mpifloat.py
#
from mpi4py import MPI
import numpy as np

import time

tagValues = [ 123.678, 0.00064, 0.0000000006776, 0.09854, 346789012.04, 562, 52.00000019 ]
tag_list = [ "S_STILL_CAP", "S_APERTURE", "S_ISO", "S_EX_PRO", "S_FOCUS", "S_FOCUS_MODE", "S_FOCUS_AREA" ]
        
NUMBER_OF_ITEMS = len(tag_list)
LOOP_ITERATOR = NUMBER_OF_ITEMS - 1

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
# if we need to see how many workers there are (we define as 2 from our run command)
# size = comm.Get_size()

# master process
if rank == 0:

    # if you need to go through the ranks of all worker processes
    #    for i in range(1, size):
    #
    # we only have one.

    # master process sends data to worker No.1 processes by MPI send
    #
    loop = 0
    while loop <= LOOP_ITERATOR:
        # ======= send the string tag first =======
        tag_name = tag_list[loop] 
        #
        # convert string to ascii list and make numpy array from it.
        #
        vn = []
        k = 0
        for k in range(len(tag_name)):
            vn.append(ord(tag_name[k]))
        u8_tag_name = np.array(vn, np.uint8)
        data = np.array(u8_tag_name, dtype="float64")
        comm.Send(data, dest=1, tag=0)
        print('\033[33m Process {} sent string data: \033[9m'.format(rank), data)
    
        #
        # followed by the data as 64 bit floating point, its value then the indexNumber.
        # 
        tagValue = tagValues[loop]
        tagIndexNo = loop + 1
        list1 = []
        list1.append(tagValue)
        list1.append(tagIndexNo)     
        data = np.array(list1, dtype="float64")
        comm.Send(data, dest=1, tag=0)
        print('\033[35m Process {} sent data: \033[0m'.format(rank), data)
        time.sleep(0.2)
        loop += 1
        
# worker processes is rank1 by our start-up definition, there are no more ranks
elif rank == 1:

    loop = 0
    while loop <= LOOP_ITERATOR:    
        # initialize the receiving buffer to 20 elements max char size for tag
        #
        data = np.zeros(20)
        
        # receive data from master process (first its the tag as a string)
        #
        comm.Recv(data, source=0, tag=0)
        
        # convert the object recieved back to a list and then convert it to a string
        #
        list1 = data.tolist()
        tagName = ""
        for s in range(0,len(list1)):
            tagName = tagName + chr(int(list1[s]))
        print(f"\033[32m Process {rank} received the tagname \033[31;46m {tagName} \033[0m")

        # receive data from master process (second its the values associated as floating point numbers) 
        #        
        comm.Recv(data, source=0, tag=0)
        
        # convert it back to a list and parse its values to the variables
        #
        list1 = data.tolist()
        print('Process {} received data index number :'.format(rank), int(list1[1]))
        print('Process {} received data value :'.format(rank), list1[0])
        #time.sleep(0.6)
        time.sleep(10)
        loop += 1
else:
    print("this process slot is not being used")