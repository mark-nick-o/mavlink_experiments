#
# a test stub to test multi-processing python
#
# it shows the functionality of multiprocess library
# for daemon, sequential, and paralel pool
#
import multiprocessing

# wait
import time,timeit
import sys

class fastGlobals:
    __slots__ = ('take_picture','start_video',) # __slots__ defines a fast variable
    take_picture: int    
    start_video: int 
    
# Starting timer for Parent measurement
start_time = timeit.default_timer()
timer = 0

class mySony():
   
    def __init__ (self):
        self.error_counts = multiprocessing.Value('i', 2)

    def __del__(self):  
        class_name = self.__class__.__name__  
        print('{} Deleted'.format(class_name))
       
class mavlinkSonyCamWriteVals():

    STATE_INIT = 99
    STATE_READY = 1
    STATE_CAM_WRITING = 2
    STATE_MAV_READING = 3
    STATE_MAV_WRITING = 4
    STATE_CAM_READING = 5
    STATE_WAIT = 6
    
    # indiviual states when a sequential priority queue is required
    FUNC_EX_PRO = 7
    FUNC_APER = 8
    FUNC_FOCUS = 9
    FUNC_ISO = 10
    FUNC_SS = 11
    FUNC_WB = 12
    FUNC_SC = 13
        
    class_global = 99
    numberOfVals = 0
   
    def __init__ (self):
        self.set_sony_iso = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.set_sony_aperture = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        mavlinkSonyCamWriteVals.numberOfVals += 1 

    def __del__(self):  
        class_name = self.__class__.__name__  
        print('{} Deleted'.format(class_name))
        
    def add_aper(self):
       self.set_sony_aperture.value += 1

# -------------------------------- SEQUENTIAL ------------------------------------------------------------------------------
#
# this task runs sequentially and doesnt set the variables (attributes) of the class passed to it.
#       
def manageAlphaCameraExpro( a, classObj, pvar, mpc, state_of_task ):

    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING
    print(f"\033[96m Task1:: initial value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc} \033[0m")
    time.sleep(1)
    #state_of_task.value = mavlinkSonyCamWriteVals.STATE_WAIT
    with classObj.set_sony_iso.get_lock():
        classObj.set_sony_iso.value += 1
    classObj.add_aper()
    mavlinkSonyCamWriteVals.class_global += 1
    pvar += 1
    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_APER
    print(f"Task1:: second value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY    
    # true paralel tasking mode --> state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY

#
# this task runs sequentially and doesnt set the variables (attributes) of the class passed to it.
#       
def manageAlphaCameraAperture( a, classObj, pvar, mpc, state_of_task ):

    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING
    print(f"\033[95m Task2:: initial value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc} \033[0m")
    time.sleep(1)
    #state_of_task.value = mavlinkSonyCamWriteVals.STATE_WAIT
    with classObj.set_sony_iso.get_lock():
        classObj.set_sony_iso.value += 1
    classObj.add_aper()
    mavlinkSonyCamWriteVals.class_global += 1
    pvar += 1
    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_FOCUS
    print(f"Task2:: second value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         
    # true paralel tasking mode --> state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY

def manageAlphaCameraFocusData( a, classObj, pvar, c, mpc, state_of_task ):

    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING
    print(f"\033[94m Task3:: initial value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc} \033[0m")
    time.sleep(1)
    #state_of_task.value = mavlinkSonyCamWriteVals.STATE_WAIT
    with classObj.set_sony_iso.get_lock():
        classObj.set_sony_iso.value += 1
    classObj.add_aper()
    mavlinkSonyCamWriteVals.class_global += 1
    pvar += 1
    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_ISO
    print(f"Task3:: second value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         
    # true paralel tasking mode --> state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY

def manageAlphaCameraIso( a, classObj, pvar, mpc, state_of_task ):

    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING
    print(f"\033[93m Task4:: initial value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc} \033[0m")
    time.sleep(1)
    #state_of_task.value = mavlinkSonyCamWriteVals.STATE_WAIT
    with classObj.set_sony_iso.get_lock():
        classObj.set_sony_iso.value += 1
    classObj.add_aper()
    mavlinkSonyCamWriteVals.class_global += 1
    pvar += 1
    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_SS
    print(f"Task4:: second value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         
    # true paralel tasking mode --> state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY

def manageAlphaCameraShutSpd( a, classObj, pvar, mpc, state_of_task ):

    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING
    print(f"\033[92m Task5:: initial value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc} \033[0m")
    time.sleep(1)
    #state_of_task.value = mavlinkSonyCamWriteVals.STATE_WAIT
    with classObj.set_sony_iso.get_lock():
        classObj.set_sony_iso.value += 1
    classObj.add_aper()
    mavlinkSonyCamWriteVals.class_global += 1
    pvar += 1
    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_WB
    print(f"Task5:: second value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         
    # true paralel tasking mode --> state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY

def manageAlphaWhiteBala( a, classObj, pvar, mpc, state_of_task ):

    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING
    print(f"\033[91;44m Task6:: initial value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc} \033[0m")
    time.sleep(1)
    #state_of_task.value = mavlinkSonyCamWriteVals.STATE_WAIT
    with classObj.set_sony_iso.get_lock():
        classObj.set_sony_iso.value += 1
    classObj.add_aper()
    mavlinkSonyCamWriteVals.class_global += 1
    pvar += 1
    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_SC
    print(f"Task6:: second value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         
    # true paralel tasking mode --> state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY

def manageAlphaCameraStillCap( a, classObj, pvar, mpc, state_of_task ):

    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING
    print(f"\033[97m Task7:: initial value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc} \033[0m")
    time.sleep(1)
    #state_of_task.value = mavlinkSonyCamWriteVals.STATE_WAIT
    with classObj.set_sony_iso.get_lock():
        classObj.set_sony_iso.value += 1
    classObj.add_aper()
    mavlinkSonyCamWriteVals.class_global += 1
    pvar += 1
    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_EX_PRO
    print(f"Task7:: second value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {pvar} {mpc}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         
    # true paralel tasking mode --> state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY

def perform_usb_reset( mySonyCam ):
    print("\033[34;42m usb reset ")
    #if (mySonyCam.error_counts.value >= 5):  
    #    #reset_usb_camlink()
    #    with mySonyCamN.error_counts.get_lock():
    #        mySonyCam.error_counts.value = 0 
    print("\033[31;44m PERFORM USB RESET !!!!!!!!!!!!!!!!!!!! \033[0m")
    
# --------------------------- DAEMON --------------------------------------------------------------        
#
# This task seems to write the value to the class until it exits
#
def manageTask2( classObj, mpc, count=5 ):
    while (count >= 0):
        print(f"\033[93;45m Task2 Daemon:: initial value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {mpc} \033[0m")
        time.sleep(2)
        with classObj.set_sony_iso.get_lock():
            classObj.set_sony_iso.value += 1
        classObj.add_aper()
        mavlinkSonyCamWriteVals.class_global += 1
        print(f"Task2 Daemon:: second value set is {classObj.set_sony_iso.value} {classObj.set_sony_aperture.value} {mavlinkSonyCamWriteVals.class_global} {mpc}")
        count -= 1

def manageTask3( classObj, mpc ):
    while True:
        manageTask2( classObj, mpc )
        time.sleep(10)

# ----------------------- PARALEL -----------------------------------------------------------------
#
def sendMavExpro( wedge, a, b ):
    print(f"\033[32;41m process sendMavExpro {wedge} \033[0m")
    time.sleep(1)
    timer = str(int(timeit.default_timer() - start_time)) 
    print (f"Elapsed Time: {timer} Loop Time:  {str(time.time()/1000)} ")  
    
def sendMavAper( wedge, a, b ):  
    time.sleep(1)
    print(f"\033[33;42m process sendMavAper {wedge} \033[0m")
    time.sleep(1)
    timer = str(int(timeit.default_timer() - start_time)) 
    print (f"Elapsed Time: {timer} Loop Time:  {str(time.time()/1000)} ")   
    
def sendMavFocusData( wedge, a, b, c ):  
    time.sleep(1)
    print(f"\033[30;43m process sendMavFocusData {wedge} \033[0m")
    time.sleep(1)
    timer = str(int(timeit.default_timer() - start_time)) 
    print (f"Elapsed Time: {timer} Loop Time:  {str(time.time()/1000)} ")   
    
def sendMavIso( wedge, a, b ):
    time.sleep(1)
    print(f"\033[32;44m process sendMavIso {wedge} \033[0m")
    time.sleep(1)
    timer = str(int(timeit.default_timer() - start_time)) 
    print (f"Elapsed Time: {timer} Loop Time:  {str(time.time()/1000)} ")    
    
def sendMavShutSpd( wedge, a, b ):
    time.sleep(1)
    print(f"\033[36;45m process sendMavShutSpd {wedge} \033[0m")
    time.sleep(4)
    timer = str(int(timeit.default_timer() - start_time)) 
    print (f"Elapsed Time: {timer} Loop Time:  {str(time.time()/1000)} ")  
    
def sendMavWhiteBala( wedge, a, b ):
    time.sleep(1)
    print(f"\033[37;46m process sendMavWhiteBala {wedge} \033[0m")
    time.sleep(2)
    timer = str(int(timeit.default_timer() - start_time)) 
    print (f"Elapsed Time: {timer} Loop Time:  {str(time.time()/1000)} ")   
    
def sendMavStillCap( wedge, a, b ):
    time.sleep(1)
    print(f"\033[31;47m process sendMavStillCap {wedge} \033[0m")
    time.sleep(1.5)
    timer = str(int(timeit.default_timer() - start_time)) 
    print (f"Elapsed Time: {timer} Loop Time:  {str(time.time()/1000)} ")

def sendMavlinkHeartBeat(fm, cID, sleepTm=1):
    while True:
        # fm.mavlink_send_GCS_heartbeat(cID)
        time.sleep(sleepTm)
        print(f"\033[36;44m HeartBEAT !!!!! ============= {sleepTm} seconds ================= \033[0m")
        # sleepTm -= 1

def serviceParamRequests( mySonyCam, mav2SonyVals, stcap, wb, ss, iso, pf, pfa, pa, expro ):
    while True:
        print("\033[46m service parameters >>>>>>>>>>>>>>>>>>>>>! \033[0m")
        time.sleep(15)

def run_process_messages_from_connection(fra, the_connect, sharedObj):
    while True:
        p = multiprocessing.current_process()
        print ('Starting: MavReader ', p.name, p.pid) 
        #fra.process_messages_from_connection( the_connect, sharedObj )
        time.sleep(0.2)
        print ('Exiting MavReader :', multiprocessing.current_process().name)

def fast_globs( mySonyCam ):

    #while True:
    print(f"?????????????????????????? fast globs on {fastGlobals.take_picture} ???????????????????????????????")
    if (fastGlobals.take_picture == 1):
        print("\033[33;42m ###############################################################################################################FAST GLOBALS SAW CHANGE \033[0m")
        return 2   
    print("fast globs on")
    return fastGlobals.take_picture
        
from random import seed
from random import randint
    
def gen_random_int( ):

    # generate some integers
    for _ in range(5):
	    value = randint(0, 5)
    print(f"generated random integer {value}")
    return int(value)
    
def mavlinkTakePhoto( mySonyCam, flg ):
    mySonyCam.take_a_picture_now(flg)
    
if __name__ == '__main__':

    # now use one of the processing values from the multiprocessing library
    #
    mp_choice = multiprocessing.Value('i', mavlinkSonyCamWriteVals.FUNC_EX_PRO)

    mp_state = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
    
    # use an internal program variable looks like it cant we written to when in multiprocessing mode
    #
    programVar = mavlinkSonyCamWriteVals.STATE_INIT
        
    gcsWrites2Sony = mavlinkSonyCamWriteVals() 
    #mySonyCamNo1 = mySony()

    # seed random number generator
    seed(1)
    fastGlobals.take_picture = gen_random_int()
        
    #p1 = multiprocessing.Process(name='manageAlphaCameraExpro', target=manageAlphaCameraExpro, args=(gcsWrites2Sony,)).start()
    p1 = multiprocessing.Process(name='manageAlphaCameraExpro', target=manageAlphaCameraExpro, args=(gcsWrites2Sony,programVar, mp_choice, mp_state, ))
    print("p1 is created...")

    time.sleep(0.5) 

    # initialise pool data
    #
    max_number_processes = 8 
    mySonyCamNo1 = 14356
    expro = 1
    aper = 2
    focusdata = 3
    focusarea = 4
    iso = 5
    shut_sp = 6
    whitebal = 7
    stillcap = 8
    cID = 87
    frame = 123450
    
    #
    # ================================= DAEMON CONTINUOS TASK No.1 ======================================
    #
    # this runs the daemon independantly once
    #
    # p2 = multiprocessing.Process(name='manageTask2', target=manageTask2, args=(gcsWrites2Sony, mp_choice,))
    #
    # this one repeats the above method every 30 seconds as a continuous daemon
    #
    p2 = multiprocessing.Process(name='manageTask3', target=manageTask3, args=(gcsWrites2Sony, mp_choice,))
    p2.daemon = True
    if not p2.is_alive() == True:
        p2.start() 
    print("daemon 1 is running")
    invSendHz = 5 / 6;
    p3 = multiprocessing.Process(name='sendMavlinkHeartBeat', target=sendMavlinkHeartBeat, args=(frame, cID, invSendHz))
    p3.daemon = True
    if not p3.is_alive() == True:
        p3.start() 
    print("daemon 2 is running")
    p00 = multiprocessing.Process(name='serviceParamRequests', target=serviceParamRequests, args=(mySonyCamNo1, gcsWrites2Sony, stillcap, whitebal, shut_sp, iso, focusdata, focusarea, aper, expro,))      
    p00.daemon = True
    if not p00.is_alive() == True:
        p00.start()  
    print("Service Request Daemon Active") 
    p0 = multiprocessing.Process(name='run_process_mavlink', target=run_process_messages_from_connection, args=(frame, cID, gcsWrites2Sony,))
    p0.daemon = True
    if not p0.is_alive() == True:
        p0.start() 
    print("\033[32m Started Mavlink Receiver \033[0m")  
    #p4 = multiprocessing.Process(name='fast_globs', target=fast_globs, args=(frame,))
    #p4.daemon = True
    #if not p4.is_alive() == True:
    #    p4.start() 
    #print("\033[32m Started Fast Globs \033[0m")
    
    #
    # continuos task scheduler
    #    
    while True:
        print(f"start at top of loop using multiprocessing..... {fastGlobals.take_picture}")
        fastGlobals.take_picture = gen_random_int()
        fastGlobals.take_picture = fast_globs( frame )
        print(f"fast_globs completed..... {fastGlobals.take_picture}")
        
        #
        # ===================== Sequential Task Scheduler ==========================
        #
        # runs each task in a linear sequence wating for completion in the background
        #
        
        if p1 is not None:
            print("p1 is made")
            if (p1.is_alive() == False): 
                print(f"\033[36m p1 is re-starting {mp_state.value} \033[0m")
                try:
                    if (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_EX_PRO):
                        print("\033[31m EXPRO \033[0m")
                        p1 = multiprocessing.Process(name='manageAlphaCameraExpro', target=manageAlphaCameraExpro, args=(mySonyCamNo1, gcsWrites2Sony, expro, mp_choice, mp_state,))
                    elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_APER):
                        print("\033[31m APER \033[0m")
                        p1 = multiprocessing.Process(name='manageAlphaCameraAperture', target=manageAlphaCameraAperture, args=(mySonyCamNo1, gcsWrites2Sony, aper, mp_choice, mp_state,))
                    elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_FOCUS):
                        print("\033[31m FOCUS \033[0m")
                        p1 = multiprocessing.Process(name='manageAlphaCameraFocusData', target=manageAlphaCameraFocusData, args=(mySonyCamNo1, gcsWrites2Sony, focusdata, focusarea, mp_choice, mp_state,))
                    elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_ISO):
                        print("\033[31m ISO \033[0m")
                        p1 = multiprocessing.Process(name='manageAlphaCameraIso', target=manageAlphaCameraIso, args=(mySonyCamNo1, gcsWrites2Sony, iso, mp_choice, mp_state,))
                    elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_SS):
                        print("\033[31m SS \033[0m")
                        p1 = multiprocessing.Process(name='manageAlphaCameraShutSpd', target=manageAlphaCameraShutSpd, args=(mySonyCamNo1, gcsWrites2Sony, shut_sp, mp_choice, mp_state,))
                    elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_WB):
                        print("\033[31m WB \033[0m")
                        p1 = multiprocessing.Process(name='manageAlphaWhiteBala', target=manageAlphaWhiteBala, args=(mySonyCamNo1, gcsWrites2Sony, whitebal, mp_choice, mp_state,))
                    elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_SC):
                        print("\033[31m SC \033[0m")
                        p1 = multiprocessing.Process(name='manageAlphaCameraStillCap', target=manageAlphaCameraStillCap, args=(mySonyCamNo1, gcsWrites2Sony, stillcap, mp_choice, mp_state,))
                        
                    if ((mp_state.value == mavlinkSonyCamWriteVals.STATE_READY) or (mp_state.value == mavlinkSonyCamWriteVals.STATE_INIT)): 
                        print("\033[33m p1 is re-started \033[0m")
                        with mp_state.get_lock():
                            mp_state.value == mavlinkSonyCamWriteVals.STATE_CAM_WRITING
                        p1.start()
                except Exception as err_msg:
                    print("error message {}".format(err_msg))  
            else:
                print("\033[35m p1 is still running \033[0m")           
        else:
            if (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_EX_PRO):     
                p1 = multiprocessing.Process(name='manageAlphaCameraExpro', target=manageAlphaCameraExpro, args=(mySonyCamNo1, gcsWrites2Sony, expro, mp_choice, mp_state,))
            elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_APER):
                p1 = multiprocessing.Process(name='manageAlphaCameraAperture', target=manageAlphaCameraAperture, args=(mySonyCamNo1, gcsWrites2Sony, aper, mp_choice, mp_state,))
            elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_FOCUS):
                p1 = multiprocessing.Process(name='manageAlphaCameraFocusData', target=manageAlphaCameraFocusData, args=(mySonyCamNo1, gcsWrites2Sony, focusdata, focusarea, mp_choice, mp_state,))
            elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_ISO):
                p1 = multiprocessing.Process(name='manageAlphaCameraIso', target=manageAlphaCameraIso, args=(mySonyCamNo1, gcsWrites2Sony, iso, mp_choice, mp_state,))
            elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_SS):
                p1 = multiprocessing.Process(name='manageAlphaCameraShutSpd', target=manageAlphaCameraShutSpd, args=(mySonyCamNo1, gcsWrites2Sony, shut_sp, mp_choice, mp_state,))
            elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_WB):
                p1 = multiprocessing.Process(name='manageAlphaWhiteBala', target=manageAlphaWhiteBala, args=(mySonyCamNo1, gcsWrites2Sony, whitebal, mp_choice, mp_state,))
            elif (mp_choice.value == mavlinkSonyCamWriteVals.FUNC_SC):
                p1 = multiprocessing.Process(name='manageAlphaCameraStillCap', target=manageAlphaCameraStillCap, args=(mySonyCamNo1, gcsWrites2Sony, stillcap, mp_choice, mp_state,))
                       
        time.sleep(0.1)    
        if (mp_state.value == mavlinkSonyCamWriteVals.STATE_READY):   
            print("now we are waiting for the multiprocess we started")        
            try:
                p1.join()
                p1.terminate()
                print("p1 is ended")
            except Exception as err_msg:
                print("error message {}".format(err_msg))

        #
        # ===================== Paralell Pool Scheduler 8 Tasks ==========================
        #
        # runs each task in a paralel waiting for all to finish 
        #
        
        print("\033[31m;42m Always waits for all proceses before restart loop ????\033[0m")    
        pool = multiprocessing.Pool(max_number_processes)  #Defines the Batch Size

        pool.apply_async(perform_usb_reset,args=(mySonyCamNo1,)) 
        #pool.apply_async(sendMavXXXX,args=(mySonyCamNo1, expro, cID,)) 
        pool.apply_async(sendMavExpro,args=(mySonyCamNo1, expro, cID,)) 
        pool.apply_async(sendMavAper,args=(mySonyCamNo1, aper, cID,)) 
        pool.apply_async(sendMavFocusData,args=(mySonyCamNo1, focusdata, focusarea, cID,)) 
        pool.apply_async(sendMavIso,args=(mySonyCamNo1, iso, cID,)) 
        pool.apply_async(sendMavShutSpd,args=(mySonyCamNo1, shut_sp, cID,)) 
        pool.apply_async(sendMavWhiteBala,args=(mySonyCamNo1, whitebal, cID,)) 
        pool.apply_async(sendMavStillCap,args=(mySonyCamNo1, stillcap, cID,)) 
  
        pool.close()                                        # After all threads started we close the pool
        pool.join()                                         # And wait until all threads are done
        print("\033[34;42m done function in-paralel \033[0m")
            

