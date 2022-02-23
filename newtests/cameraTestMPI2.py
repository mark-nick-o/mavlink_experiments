#
# Example to send the information using MPI between 2 process ranks
#
# https://keichi.dev/post/mpi4py/
# https://np2lkoo.hatenablog.com/entry/2020/11/07/221119
#
#
# from multiprocessing import Process
import multiprocessing

# run program as :- mpirun -np 2 python3 cameraTestMPI.py
#
from mpi4py import MPI
import numpy as np

import time

# ===============================================================================================================================
#
# Name : NewSonyAlphaClass.py
# Desc : Communicate with new Sony Alpha Series of Camera
# Auth : AIR-obots Ai-Robots
#
# ===============================================================================================================================
import shlex, subprocess, pprint

class sonyAlphaNewCamera():

    def __init__ (self, name = 'sonyAlphaCamClass'):
        self.name = name                                                                   # name as a string
        self.error_counts = multiprocessing.Value('i', 0)
        self.loop = multiprocessing.Value('i', 0)
        
    def __del__(self):  
        class_name = self.__class__.__name__  
        print('{} Deleted'.format(class_name))
        
    def check_my_os( self ):
        if ((sys.platform=='linux2') or (sys.platform=='linux')): return 1
        elif  sys.platform=='win32': return 2
        else: return 3

    def my_timestamp( self ):
        if (self.check_my_os() == 1):
            cmd = "date +%s"
            return( int(os.popen(cmd).read()) )

    def take_a_picture_now( self,flag ):

        # run the API command in the shell and look for the descriptor for the field
        #
        if (flag == 1):
           cmd='/home/pi/cams/SonyTEST32/take_picture/RemoteCli ' 
           c = os.popen(cmd)
           print(c.read())
           flag = 2
           # fastGlobals.take_picture = 2
           print(f"\033[36m Took the picture {flag}")
           return 2
        return flag
        
    def set_sony_iso( self, isoVal ):

        # run the API command in the shell and look for the descriptor for the field
        #
        isoValArg=str(isoVal)
        #cmd='/home/pi/cams/SonyTEST32/set_iso/RemoteCli ' + isoValArg
        cmd='/bin/sh /home/mark/pipe/iso.sh ' + isoValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "ISO_Format"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(f"{output} \n returned to shell {p2.returncode}")
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []
        for xx in a:
            if xx.find('ISO_Format') > -1:
                idx = itemNo
            else:
                if (idx != 99999):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = str(0)
                        xx = xx.replace(",","")                                
                        vv = xx.strip("}")                       # caters for a case in testing where i have closing bracket 34}                                
                        answers.append(vv)
                        idx = 99999
            itemNo += 1
        return answers

    def set_sony_aperture( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        #cmd='/home/pi/cams/SonyTEST32/set_aperture/RemoteCli ' + ValArg
        cmd='/bin/sh /home/mark/pipe/aper.sh ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Aperture_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []
        for xx in a:
            if xx.find('Aperture_Val') > -1:
                idx = itemNo
            else:
                if (idx != 99999):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = str(0)     
                        xx = xx.replace(",","")     
                        vv = xx.strip("}")                       # caters for a case in testing where i have closing bracket 34}                                
                        answers.append(vv)
                        idx = 99999
            itemNo += 1
        return answers	
        
# ============================ functions =================================
#
# performs MPI receive from rank 1
#
def doMPIRcv( cam ):
    # initialize the receiving buffer to 20 elements max char size for tag
    #
    data = np.zeros(20)
        
    comm.Recv(data, source=1, tag=0)
        
    # convert it back to a list and parse its values to the variables
    #
    list1 = data.tolist()
    if len(list1) > 1:
        print('\033[34m Process {} received current value as :'.format(rank), list1[1])
        print('Process {} received previous value as : \033[0m'.format(rank), list1[0])

    # increment the recieve counter
    #    
    cam.loop.value = cam.loop.value + 1    
    print('\033[33m Process {} errcnt : \033[0m'.format(rank), mySonyAlpha.error_counts)  

# doMPIRcv daemon process
#
def rundoMPIRcv( cam ):
    while True:
        doMPIRcv( cam )

# ============================ main =================================
#        
if __name__ == '__main__':
        
    tagValues = [ 2, 1, 5, 2, 3, 3, 5, 4 ]
    tag_list = [ "S_STILL_CAP", "S_APERTURE", "S_ISO", "S_EX_PRO", "S_FOCUS", "S_FOCUS_MODE", "S_FOCUS_AREA", "S_SHUT_SP" ]
        
    NUMBER_OF_ITEMS = len(tag_list)
    LOOP_ITERATOR = NUMBER_OF_ITEMS - 1

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    # if we need to see how many workers there are (we define as 2 from our run command)
    # size = comm.Get_size()

    mySonyAlpha = sonyAlphaNewCamera()

    listA = mySonyAlpha.set_sony_iso( 1 )
    print(f" begin with {listA}")

    mySonyAlpha.error_counts.value = 11     
    # master process is rank 0
    if rank == 0:

        # if you need to go through the ranks of all worker processes
        #    for i in range(1, size):
        #
        # we only have one.

        # master process sends data to worker No.1 processes by MPI send
        #
        loop = 0
        while loop <= LOOP_ITERATOR:
        #while True:
            #mySonyAlpha.error_counts = mySonyAlpha.error_counts + 4   only counts in this rank they are duplicates
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

        with mySonyAlpha.loop.get_lock():
            mySonyAlpha.loop.value = 0
            
        # runs the MPI reciever as a multi-process daemon
        #
        p1 = multiprocessing.Process(name='rundoMPIRcv', target=rundoMPIRcv, args=(mySonyAlpha,))
        p1.daemon = True
        if not p1.is_alive() == True:
            p1.start()
            
        # now the main loop is waiting for the shared variable to indicate we recieved back both packets
        # in other words the camera did both chosen actions with the values sent over MPI from this rank
        #
        while mySonyAlpha.loop.value <= 1:
            #doMPIRcv( mySonyAlpha )
            print("in main loop")
            time.sleep(10) 
        time.sleep(1)            
        p1.terminate()
        
    # worker processes is rank1 by our start-up definition, there are no more ranks
    elif rank == 1:

        loop = 0
        while loop <= LOOP_ITERATOR: 

            mySonyAlpha.error_counts.value = 4              
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
            print(f"\033[35m Process {rank} received the tagname \033[31;46m {tagName} \033[0m")

            # receive data from master process (second its the values associated as floating point numbers) 
            #        
            comm.Recv(data, source=0, tag=0)
        
            # convert it back to a list and parse its values to the variables
            #
            list1 = data.tolist()
            if len(list1) > 1:
                print('Process {} received data index number :'.format(rank), int(list1[1]))
                print('Process {} received data value :'.format(rank), list1[0])
        
                if (list1[1] == 3):
                    ansList = mySonyAlpha.set_sony_iso(list1[0]) 
                    print(f"ISO ran the shell with a reply of {ansList}")
                    data = np.array(ansList, dtype="float64")
                    comm.Send(data, dest=0, tag=0)                   
                elif (list1[1] == 2):
                    ansList = mySonyAlpha.set_sony_aperture(list1[0])  
                    print(f"APERTURE ran the shell with a reply of {ansList}")                    
                    #time.sleep(0.6)
                    data = np.array(ansList, dtype="float64")
                    comm.Send(data, dest=0, tag=0)        
            time.sleep(10)
            loop += 1
            print('\033[34m Process {} errcnt : \033[0m'.format(rank), mySonyAlpha.error_counts)  
    else:
        print("this process slot is not being used")