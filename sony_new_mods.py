# ===============================================================================================================================
#
# Name : mavlinkSonyCamWriteVals.py
# Desc : Global memory value class for use to write mavlink to sony cam
# Auth : AIR-obots Ai-Robots
#
# ===============================================================================================================================

#
# for paralel tasking of the camera action routines
#
# from multiprocessing import Process
import multiprocessing

# for debug
import logging

# for signal interypt handling
import signal

import time

class fastGlobals:
    __slots__ = ('take_picture','start_video',) # __slots__ defines a fast variable
    take_picture: int    
    start_video: int 
    
class mavlinkSonyCamWriteVals():

    # state for multi-process object
    STATE_INIT = 99
    STATE_READY = 1
    STATE_CAM_WRITING = 2
    STATE_MAV_READING = 3
    STATE_MAV_WRITING = 4
    STATE_CAM_READING = 5
    # global counter for values
    numberOfVals = 8
    # flags to incdicate write action
    WRITE_PREV_DATA = 1
    DONT_WRITE_PREV_DATA = 0

    # mavlink write actions
    MAV_REQ_ALL_PARAM = 255
    ParamStillCap = 1
    ParamWhiteBala = 2
    ParamShutSpd = 4
    ParamIso = 8
    ParamFocus = 16
    ParamFocusArea = 32
    ParamAperture = 64
    ParamExPro = 128
    
    def __init__ (self):
        self.set_sony_iso = mavlinkSonyCamWriteVals.STATE_INIT
        self.set_sony_aperture = mavlinkSonyCamWriteVals.STATE_INIT
        self.set_sony_ex_pro = mavlinkSonyCamWriteVals.STATE_INIT
        self.set_sony_focus_area = mavlinkSonyCamWriteVals.STATE_INIT
        self.set_sony_focus = mavlinkSonyCamWriteVals.STATE_INIT
        self.set_sony_shutter = mavlinkSonyCamWriteVals.STATE_INIT
        self.set_sony_white_bal = mavlinkSonyCamWriteVals.STATE_INIT
        self.set_sony_still_cap_mode = mavlinkSonyCamWriteVals.STATE_INIT
        self.prev_sony_iso = mavlinkSonyCamWriteVals.STATE_INIT
        self.prev_sony_aperture = mavlinkSonyCamWriteVals.STATE_INIT
        self.prev_sony_ex_pro = mavlinkSonyCamWriteVals.STATE_INIT
        self.prev_sony_focus_area = mavlinkSonyCamWriteVals.STATE_INIT
        self.prev_sony_focus = mavlinkSonyCamWriteVals.STATE_INIT
        self.prev_sony_shutter = mavlinkSonyCamWriteVals.STATE_INIT
        self.prev_sony_white_bal = mavlinkSonyCamWriteVals.STATE_INIT
        self.prev_sony_still_cap_mode = mavlinkSonyCamWriteVals.STATE_INIT
        self.mav_req_all_param = 0
        self.mav_ext_req_all_param = 0
        self.state = mavlinkSonyCamWriteVals.STATE_INIT
        mavlinkSonyCamWriteVals.numberOfVals += 8                                                      # global counter of the number of values
    
    def __del__(self):  
        class_name = self.__class__.__name__  
        mavlinkSonyCamWriteVals.numberOfVals -= 1                                                      # global counter of the number of values
        print('{} Deleted'.format(class_name))

    def get_value_counter(self):  
        print('mavlink to sony writes has %d set-points' % (mavlinkSonyCamWriteVals.numberOfVals))
        return mavlinkSonyCamWriteVals.numberOfVals	

    def init_class_state( self ):
        if (self.state == mavlinkSonyCamWriteVals.STATE_INIT):
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            
    def setVal_sony_iso(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = myId
            if mode == 1:
                self.prev_sony_iso = self.set_sony_iso
            self.set_sony_iso = int(value)
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            print(f"\033[37m wrote the value {value} to {self.prev_sony_iso} {self.set_sony_iso} \033[0m")
            #exit(99)
            return True
        else:
            if (reset_state == True):
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            #exit(90)
            return False 

    def getVal_sony_iso(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = YourID
            print(' value: {} previous: {}'.format(self.set_sony_iso,self.prev_sony_iso))
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_iso,self.prev_sony_iso,True
        else:
            if (reset_state == True):
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_iso,self.prev_sony_iso,False
            
    def setVal_sony_aperture(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = myId
            if mode == 1:
                self.prev_sony_aperture = self.set_sony_aperture
            self.set_sony_aperture = int(value)
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return False 

    def getVal_sony_aperture(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = YourID
            print(' value: {} previous: {}'.format(self.set_sony_aperture,self.prev_sony_aperture))
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_aperture,self.prev_sony_aperture,True
        else:
            if (reset_state == True):
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_aperture,self.prev_sony_aperture,False
            
    def setVal_sony_ex_pro(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = myId
            if mode == 1:
                self.prev_sony_ex_pro = self.set_sony_ex_pro
            self.set_sony_ex_pro = int(value)
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return False 

    def getVal_sony_ex_pro(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = YourID
            print(' value: {} previous: {}'.format(self.set_sony_ex_pro,self.prev_sony_ex_pro))
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_ex_pro,self.prev_sony_ex_pro,True
        else:
            if (reset_state == True):
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_ex_pro,self.prev_sony_ex_pro,False
            
    def setVal_sony_focus_area(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = myId
            if mode == 1:
                self.prev_sony_focus_area = self.set_sony_focus_area
            self.set_sony_focus_area = int(value)
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return False 

    def getVal_sony_focus_area(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = YourID
            print(' value: {} previous: {}'.format(self.set_sony_focus_area,self.prev_sony_focus_area))
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_focus_area,self.prev_sony_focus_area,True
        else:
            if (reset_state == True):
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_focus_area,self.prev_sony_focus_area,False
            
    def setVal_sony_focus(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = myId
            if mode == 1:
                self.prev_sony_focus = self.set_sony_focus
            self.set_sony_focus = int(value)
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):        
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return False 

    def getVal_sony_focus(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = YourID
            print(' value: {} previous: {}'.format(self.set_sony_focus,self.prev_sony_focus))
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_focus,self.prev_sony_focus,True
        else:
            if (reset_state == True):      
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_focus,self.prev_sony_focus,False
            
    def setVal_sony_shutter(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = myId
            if mode == 1:
                self.prev_sony_shutter = self.set_sony_shutter
            self.set_sony_shutter = int(value)
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):  
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return False

    def getVal_sony_shutter(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = YourID
            print('value: {} previous: {}'.format(self.set_sony_shutter,self.prev_sony_shutter))
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_shutter,self.prev_sony_shutter,True
        else:
            if (reset_state == True): 
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_shutter,self.prev_sony_shutter,False
            
    def setVal_sony_white_bal(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = myId
            if mode == 1:
                self.prev_sony_white_bal = self.set_sony_white_bal
            self.set_sony_white_bal = int(value)
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True): 
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return False

    def getVal_sony_white_bal(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = YourID
            print('value: {} previous: {}'.format(self.set_sony_white_bal,self.prev_sony_white_bal))
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_white_bal,self.prev_sony_white_bal,True
        else:
            if (reset_state == True): 
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_white_bal,self.prev_sony_white_bal,False
            
    def setVal_sony_still_cap_mode(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = myId
            if mode == 1:
                self.prev_sony_still_cap_mode = self.set_sony_still_cap_mode
            self.set_sony_still_cap_mode = int(value)
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True): 
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return False

    def getVal_sony_still_cap_mode(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = YourID
            print('value: {} previous: {}'.format(self.set_sony_still_cap_mode,self.prev_sony_still_cap_mode))
            self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_still_cap_mode,self.prev_sony_still_cap_mode,True
        else:
            if (reset_state == True): 
                self.state = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_still_cap_mode,self.prev_sony_still_cap_mode,False

    def setMavIsoModeData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_iso(dataRcv,self.STATE_MAV_WRITING,self.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavIsoModeData( self ):
    
        ret = False  
        set_sony_iso = 0
        prev_sony_iso = 0        
        set_sony_iso,prev_sony_iso,ret = self.getVal_sony_iso(self.STATE_MAV_READING) 
        return set_sony_iso,prev_sony_iso,ret
        
    def setMavApertureData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_aperture(dataRcv,self.STATE_MAV_WRITING,self.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavApertureData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_aperture(self.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavExProData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_ex_pro(dataRcv,self.STATE_MAV_WRITING,self.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavExProData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_ex_pro(self.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavFocusAreaData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_focus_area(dataRcv,self.STATE_MAV_WRITING,self.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavFocusAreaData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_focus_area(self.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavFocusData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_focus(dataRcv,self.STATE_MAV_WRITING,self.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavFocusData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_focus(self.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavShutterData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_shutter(dataRcv,self.STATE_MAV_WRITING,self.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavShutterData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_shutter(self.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavWhiteBalData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_white_bal(dataRcv,self.STATE_MAV_WRITING,self.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavWhiteBalData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_white_bal(self.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavStillCapModeData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_still_cap_mode(dataRcv,self.STATE_MAV_WRITING,self.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavStillCapModeData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_still_cap_mode(self.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
# ===============================================================================================================================
#
# Name : MemoryValueClass.py
# Desc : Global memory value class for use with cameras and mavlink
# Auth : AIR-obots Ai-Robots
#
# ===============================================================================================================================
import time
        
class memoryValue():

    # multi process thread status of object
    STATE_READY = 1
    STATE_CAM_WRITING = 2
    STATE_MAV_READING = 3
    STATE_MAV_WRITING = 4
    STATE_CAM_READING = 5
    # number of objects created
    numberOfVals = 0

    def __init__ (self, name = 'value_name_not_set', signal = None,  prev = None,  state = STATE_READY):
        self.signal = signal                                                               # signal value
        self.prev = prev                                                                   # previous signal value
        self.state = state                                                                 # state of the value
        self.nextpointer = None                                                            # pointer for chain if needed
        self.name = name                                                                   # name as a string
        self.timestamp = 0                                                                 # timestamp
        self.updateNeeded = False                                                          # update required
        self.ack_send = False                                                              # param_ext_ack needed
        self.index = 0                                                                     # index number used for ack send
        memoryValue.numberOfVals += 1                                                      # global counter of the number of values
    
    def __del__(self):  
        class_name = self.__class__.__name__  
        memoryValue.numberOfVals -= 1                                                      # global counter of the number of values
        print('{} Deleted'.format(class_name))

    def get_value_counter(self):  
        print('%s: %d' % (self.name,memoryValue.numberOfVals))
        return memoryValue.numberOfVals		
  
    def get_value_data(self,YourID,timeout=100):  
        timeCnt = 0
        while (not (self.state == memoryValue.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = YourID
            print('Description: {}. value: {} previous: {}'.format(self.name, self.signal,self.prev))
            self.state = memoryValue.STATE_READY
            return self.name,self.signal,self.prev,True
        else:
            return self.name,self.signal,self.prev,False

    def set_value(self,value,myId,timeout=100):
        timeCnt = 0
        while (not (self.state == memoryValue.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = myId
            self.prev = self.signal
            self.signal = value
            self.updateNeeded = True
            self.state = memoryValue.STATE_READY
            return True
        else:
            return False

    def get_value_data_if_avail(self,YourID):  
        if  (self.state == memoryValue.STATE_READY):
            self.state = YourID
            print('Description: {}. value: {}'.format(self.name, self.signal))
            self.state = memoryValue.STATE_READY
            return self.name,self.signal,self.prev,True
        else:
            return self.name,self.signal,self.prev,False

    def set_update_flag( self, stateSent, myId ):
        if (self.state == memoryValue.STATE_READY):
            self.state = myId
            self.updateNeeded = stateSent
            self.state = memoryValue.STATE_READY
            return True
        else:
            return False

    def get_update_flag( self, myId ):
        v = 0
        if (self.state == memoryValue.STATE_READY):
            self.state = myId
            v = self.updateNeeded 
            self.state = memoryValue.STATE_READY
            return v,True
        else:
            return v,False
            
    def set_ack_send( self, stateSent, myId ):
        if (self.state == memoryValue.STATE_READY):
            self.state = myId
            self.ack_send = stateSent
            self.state = memoryValue.STATE_READY
            return True
        else:
            return False			

    def get_ack_send( self, myId ):
        v = 0
        if (self.state == memoryValue.STATE_READY):
            self.state = myId
            v = self.ack_send 
            self.state = memoryValue.STATE_READY
            return v,True
        else:
            return v,False
            
if __name__ == '__main__':

    #
    # Test the library is okay
    #
    initVal = 23
    getName = "noName"
    getValueforMAVSending = 0
    getPrev = 0
    
    SonyWhiteBalance = memoryValue('sonyWhiteBal',initVal)
    FocusSetpoint = memoryValue('FocusSetpoint',initVal+6)

    #
    # example using in mavlink sender
	#
    mavSetPointVal = 99 #we_got_from_mavlink
    Timeout = 20
    if (FocusSetpoint.set_value(mavSetPointVal, memoryValue.STATE_MAV_WRITING, Timeout) == True):
        # { value has been successfully set }
        print("set the setpoint value focus")

    #
    # example to get the white balance setting from the cam to send over mavlink
    #
    getName, getValueforMAVSending, getPrev, myState = SonyWhiteBalance.get_value_data(memoryValue.STATE_MAV_READING, Timeout) 
    if (myState == True):
        # now pack tha data
        print("got data ok")
    else:
        # you got an error or timeout
        print("data error")

    #
    # example using in mavlink sender
    #
    mavSetPointVal = 199 #we_got_from_mavlink
    Timeout = 20
    if (SonyWhiteBalance.set_value(mavSetPointVal, memoryValue.STATE_MAV_WRITING, Timeout) == True):
        # { value has been successfully set }
        print("set the setpoint value white balance")

    #
    # example to get the white balance setting from the cam to send over mavlink
    #
    getName, getValueforMAVSending, getPrev, myState = SonyWhiteBalance.get_value_data(memoryValue.STATE_MAV_READING, Timeout) 
    if (myState == True):
        # now pack tha data
        print("got data ok")
    else:
        # you got an error or timeout
        print("data error")
        
    #
    # example to iterate without waiting for completion on the write to the value from elsewhere
    #
    myState = False
    while not myState == True:
        getName, getVal, getPrev, myState = FocusSetpoint.get_value_data_if_avail( memoryValue.STATE_CAM_READING )
        if myState == True:
            # now use this value and send to the camera
            print("setpoint available")
        else:
            # do something else while watiting
            print("setpoint being written by other task")
        # what you do until it has arrived
        time.sleep(0.1)
        
    # what you do after
    print("using the setpoint to change the camera")

    #
    # print the number of memory values
    #
    print(FocusSetpoint.get_value_counter())
    print(SonyWhiteBalance.get_value_counter())
    
    #
    # Release the shared memory
    #	
    del FocusSetpoint
    del SonyWhiteBalance
	
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
        self.error_counts = 0
        
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
           fastGlobals.take_picture = 2
           print(f"\033[36m Took the picture {flag}")
           #exit(222)
        
    def set_sony_iso_orig( self, isoVal ):

        # run the API command in the shell and look for the descriptor for the field
        #
        isoValArg=str(isoVal)
        cmd='/home/pi/cams/SonyTEST32/set_iso/RemoteCli ' + isoValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "ISO_Mode"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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

    def set_sony_iso( self, isoVal ):

        # run the API command in the shell and look for the descriptor for the field
        #
        isoValArg=str(isoVal)
        cmd='/home/pi/cams/SonyTEST32/set_iso/RemoteCli ' + isoValArg
        args = shlex.split(cmd)
        #    s=subprocess.Popen(args, stdout=subprocess.PIPE)
        #    p2 = subprocess.Popen(["grep", "ISO_Mode"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        #    output = p2.communicate()[0]
        #    print(f"{output} \n returned to shell {p2.returncode}")
        #    s.stdout.close()

        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output = p3.communicate()[0]


        # CONSIDER :: because we have to trap various errors and act on them we had to parse the output for other things i might modify CameraDevice.cpp to
        # cover it all and exit as quick as possible using return codes but i couldnt succeed to read them all successfully using .returncode property
        # with the pipe attached as above and we dont want too many delays
        #
        s=subprocess.run( args, stdout=subprocess.PIPE )
        output=s.stdout
        #s.stdout.close()
              
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas

        #    alternative using file........
        #
        #    with open('out.txt','w+') as fout:
        #        s=subprocess.call(args, stdout=fout)
        #        fout.seek(0)
        #        output=fout.read()
        #        a = shlex.split(output)
        #        fout.close()
        
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []

        # new error handler sends a unique reply which means count these errors and then force a reset of the usb
        #
        if  ( not(z.find("No cameras detected") == -1) or not(z.find("Failed to get") == -1)) :            
            self.error_counts += 1
            print(f"\033[31m Error Reading from Camera USB Link {self.error_counts} \033[0m")
            return answers
            
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
        cmd='/home/pi/cams/SonyTEST32/set_aperture/RemoteCli ' + ValArg
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

    def set_sony_ex_pro( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_ex_pro/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Exposure_Program_Value"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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
            if xx.find('Exposure_Program_Value') > -1:
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

    def set_sony_focus( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_focus/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Focus_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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
            if xx.find('Focus_Val') > -1:
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

    def set_sony_focus_area( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_fa/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Focus_Area_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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
            if xx.find('Focus_Area_Val') > -1:
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

    def set_sony_shutter( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_shutter/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Shutter_Value"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        zz = z.replace("\"","")            # get rid of the inch symbol it will crash us
        a = shlex.split(zz)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []
        for xx in a:
            if xx.find('Shutter_Value') > -1:
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

    def set_sony_white_bal( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_wb/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "White_Bal_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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
            if xx.find('White_Bal_Val') > -1:
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

    def get_sony_still_cap_mode( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/still_cap_mode/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Still_Capture_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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
            if xx.find('Still_Capture_Val') > -1:
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

    def get_sony_white_balance( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/white_bal/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "White_Bal_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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
            if xx.find('White_Bal_Val') > -1:
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

    def get_sony_ex_pro( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/exp_pro_mode/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Exposure_Program_Value"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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
            if xx.find('Exposure_Program_Value') > -1:
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

    def get_sony_aperture( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/get_aperture/RemoteCli ' 
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

    def get_sony_focus( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/get_focus/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Focus_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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
            if xx.find('Focus_Val') > -1:
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

    def set_sony_still_cap( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_still_cap/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Still_Capture_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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
            if xx.find('Still_Capture_Val') > -1:
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

    def get_sony_focus_area( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/get_focus_dist/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Focus_Area_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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
            if xx.find('Focus_Area_Val') > -1:
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

    def get_sony_iso( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/get_iso/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "ISO_Format"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
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

    def get_sony_shut_spd( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/get_shutter/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Shutter_Value"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        zz = z.replace("\"","")            # remove quoate mark meaning seconds
        a = shlex.split(zz)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []
        for xx in a:
            if xx.find('Shutter_Value') > -1:
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
        
    # ======================= new additions to the class ================================================

    def setSonyObjData( self, mem, camDataPointVal, Timeout = 100 ):

        if not (mem.set_value(camDataPointVal, mem.STATE_CAM_WRITING, Timeout) == True):
            print("\033[31m value has not been successfully set \033[0m")   
            return False
        else:
            return True
            
    def initSonyCamExProData( self ):
    
        ans = self.get_sony_ex_pro( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" Exposure Prog Mode = {ans}")
                try:
                    SonyObject = memoryValue('S_EX_PRO_MODE',int(ans[0]))
                    SonyObject.updateNeeded = True 
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('S_EX_PRO_MODE',0) 
            else:
                print("\033[31m Failed get the camera ExPro \033[0m")
                SonyObject = memoryValue('S_EX_PRO_MODE',0)             
        else:
            print("\033[31m Cant get Exposure Prog Mode \033[0m")
            SonyObject = memoryValue('S_EX_PRO_MODE',0)

        SonyObject.index = memoryValue.numberOfVals 
        print(f"Expro : created object number : {SonyObject.index}")
        return SonyObject

    def getSonyCamExProData( self, mem ):
    
        ret = False
        ans = self.get_sony_ex_pro( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" exposure program mode =  {ans}")
                try:
                    ret = self.setSonyObjData( mem, int(ans[0]) ) 
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
            else:
                print("\033[31m Failed get the exposure program mode\033[0m ")
        else:
            print("\033[31m Cant get Exposure Prog Mode \033[0m")          
        return ret
        
    def initSonyApertureData( self ):
               
        ans = self.get_sony_aperture( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" Aperture = {ans}")
                try:
                    SonyObject = memoryValue('S_APERTURE',int(ans[0]))
                    SonyObject.updateNeeded = True 
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('S_APERTURE',0) 
            else:
                print("\033[31m Failed get the camera aperture \033[0m")
                SonyObject = memoryValue('S_APERTURE',0)  
        else:
            print("\033[31m Cant get Aperture \033[0m")
            SonyObject = memoryValue('S_APERTURE',0)  

        SonyObject.index = memoryValue.numberOfVals 
        print(f"Aperture : created object number : {SonyObject.index}")             
        return SonyObject

    def getSonyApertureData( self, mem ):
    
        ret = False
        ans = self.get_sony_aperture( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" aperture =  {ans}")
                try:
                    ret = self.setSonyObjData( mem, int(ans[0]) ) 
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
            else:
                print("\033[31m Failed get the aperture \033[0m")
        else:
            print("\033[31m Cant get aperture \033[0m")          
        return ret
        
    def initSonyCamFocusData( self ):                         ###### @@11
    
        ans = self.get_sony_focus( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" Focus Mode = {ans}")
                try:
                    SonyObject = memoryValue('S_FOCUS_MODE',int(ans[0]))
                    SonyObject.updateNeeded = True  
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('S_FOCUS_MODE',0) 
            else:
                print("\033[31m Failed get the camera focus mode \033[0m")
                SonyObject = memoryValue('S_FOCUS_MODE',0) 
        else:
            print("\033[31m Cant get Focus Mode \033[0m")
            SonyObject = memoryValue('S_FOCUS_MODE',0) 

        SonyObject.index = memoryValue.numberOfVals 
        print(f"FocusData : created object number : {SonyObject.index}")            
        return SonyObject

    def getSonyCamFocusData( self, mem ):
    
        ret = False
        ans = self.get_sony_focus( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" focus =  {ans}")
                try:
                    ret = self.setSonyObjData( mem, int(ans[0]) ) 
                except Exception as err_msg:
                    print("\033[31m Failed set the focus mode object to initial value : %s \033[0m" % (err_msg))
            else:
                print("\033[31m Failed get the focus mode \033[0m")
        else:
            print("\033[31m Cant get focus mode \033[0m")          
        return ret
        
    def initSonyCamFocusAreaData( self ):
    
        ans = self.get_sony_focus_area( )

        if not (ans is None):
            if (len(ans) > 0):
                print(f" Focus Area = {ans}")
                try:
                    SonyObject = memoryValue('S_FOCUS_AREA',int(ans[0]))
                    SonyObject.updateNeeded = True  
                except Exception as err_msg:
                    print("\033[31m Failed set the focus area object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('S_FOCUS_AREA',0) 
            else:
                print("\033[31m Failed get the camera focus area \033[0m")
                SonyObject = memoryValue('S_FOCUS_AREA',0) 
        else:
            print("\033[31m Cant get Focus Mode \033[0m")
            SonyObject = memoryValue('S_FOCUS_AREA',0) 

        SonyObject.index = memoryValue.numberOfVals 
        print(f"Focus Area : created object number : {SonyObject.index}")            
        return SonyObject        

    def getSonyCamFocusAreaData( self, mem ):
    
        ret = False
        ans = self.get_sony_focus_area( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f"\033[33m FOCUS AREA =  {ans} \033[0m")
                try:
                    ret = self.setSonyObjData( mem, int(ans[0]) ) 
                except Exception as err_msg:
                    print("\033[31m Failed set the focus area object to initial value : %s \033[0m" % (err_msg))
            else:
                print("\033[31m Failed get the focus area \033[0m")
        else:
            print("\033[31m Cant get focus area ")          
        return ret
        
    def initSonyCamISOData( self ):
    
        ans = self.get_sony_iso( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" ISO = {ans}")
                try:
                    SonyObject = memoryValue('S_ISO',int(ans[0]))
                    SonyObject.updateNeeded = True  
                except Exception as err_msg:
                    print("\033[31m Failed set the iso object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('S_ISO',0) 
            else:
                print("\033[31m Failed get the camera iso \033[0m")
                SonyObject = memoryValue('S_ISO',0) 
        else:
            print("\033[31m Cant get ISO \033[0m")
            SonyObject = memoryValue('S_ISO',0) 

        SonyObject.index = memoryValue.numberOfVals 
        print(f"ISO : created object number : {SonyObject.index}")            
        return SonyObject      

    def getSonyCamISOData( self, mem ):
    
        ret = False
        ans = self.get_sony_iso( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" ISO =  {ans}")
                try:
                    ret = self.setSonyObjData( mem, int(ans[0]) ) 
                except Exception as err_msg:
                    print("\033[31m Failed set the iso object to initial value : %s \033[0m" % (err_msg))
            else:
                print("\033[31m Failed get the iso \033[0m")
        else:
            print("\033[31m Cant get iso \033[0m")          
        return ret
        
    def initSonyCamShutSpdData( self ):
    
        ans = self.get_sony_shut_spd( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" Shutter Speed =  {ans}")
                try:
                    SonyObject = memoryValue('S_SHUT_SPD',int(ans[0]))
                    SonyObject.updateNeeded = True  
                except Exception as err_msg:
                    print("\033[31m Failed set the shut spd object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('S_SHUT_SPD',0) 
            else:
                print("\033[31m Failed get the camera shutter speed \033[0m")
                SonyObject = memoryValue('S_SHUT_SPD',0) 
        else:
            print("\033[31m Cant get Shutter Speed \033[0m")
            SonyObject = memoryValue('S_SHUT_SPD',0)
            
        SonyObject.index = memoryValue.numberOfVals 
        print(f"Shut Speed : created object number : {SonyObject.index}")              
        return SonyObject 

    def getSonyCamShutSpdData( self, mem ):
    
        ret = False
        ans = self.get_sony_shut_spd( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" Shutter Speed =  {ans}")
                try:
                    ret = self.setSonyObjData( mem, int(ans[0]) ) 
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
            else:
                print("\033[31m Failed get the shutter speed \033[0m")
        else:
            print("\033[31m Cant get shutter speed \033[0m")          
        return ret
        
    def initSonyCamWhiteBalaData( self ):
    
        ans = self.get_sony_white_balance( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" White Balance =  {ans}")
                try:
                    SonyObject = memoryValue('S_WHITE_BAL',int(ans[0]))
                    SonyObject.updateNeeded = True  
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('S_WHITE_BAL',0) 
            else:
                print("\033[31m Failed get the camera white balance \033[0m")
                SonyObject = memoryValue('S_WHITE_BAL',0)         
        else:
            print("\033[31m Cant get Shutter Speed \033[0m")
            SonyObject = memoryValue('S_WHITE_BAL',0)    

        SonyObject.index = memoryValue.numberOfVals 
        print(f"White Balance : created object number : {SonyObject.index}")            
        return SonyObject 

    def getSonyCamWhiteBalaData( self, mem ):
    
        ret = False
        ans = self.get_sony_white_balance( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" White Balance =  {ans}")
                try:
                    ret = self.setSonyObjData( mem, int(ans[0]) ) 
                except Exception as err_msg:
                    print("\033[31m Failed set the white balance object to initial value : %s \033[0m" % (err_msg))
            else:
                print("\033[31m Failed get the camera white balance \033[0m")
        else:
            print("\033[31m Cant get white balance \033[0m")          
        return ret
        
    def initSonyCamStillCapModeData( self ):
    
        ans = self.get_sony_still_cap_mode( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" Still Cap Mode =  {ans}")
                try:
                    SonyObject = memoryValue('S_STILL_CAP',int(ans[0]))
                    SonyObject.updateNeeded = True  
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('S_STILL_CAP',0) 
            else:
                print("\033[31m Failed get the camera still capture mode \033[0m")
                SonyObject = memoryValue('S_STILL_CAP',0)  
        else:
            print("\033[31m Cant get Still Capture Mode \033[0m")
            SonyObject = memoryValue('S_STILL_CAP',0)   

        SonyObject.index = memoryValue.numberOfVals 
        print(f"Still Cap Mode : created object number : {SonyObject.index}")            
        return SonyObject 

    def getSonyCamStillCapModeData( self, mem ):
    
        ret = False
        ans = self.get_sony_still_cap_mode( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" Still Cap Mode =  {ans}")
                try:
                    ret = self.setSonyObjData( mem, int(ans[0]) ) 
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
            else:
                print("\033[31m Failed get the camera still capture mode \033[0m")
        else:
            print("\033[31m Cant get still cap mode \033[0m")          
        return ret    

    def enumerate_still_cap_sony_a7( self, num ):

        enum_num = 0
        enum_num_state = True
        if num == 65543:
            enum_num = 2
        elif num == 1:
            enum_num = 0
        elif num == 65540:
            enum_num = 1
        elif num == 65537:
            enum_num = 3
        elif num == 65538:
            enum_num = 4
        elif num == 196611:
            enum_num = 5
        elif num == 196610:
            enum_num = 6
        elif num == 196609:
            enum_num = 7
        elif num == 524289:
            enum_num = 8
        elif num == 524290:
            enum_num = 9
        elif num == 524293:
            enum_num = 10
        elif num == 524294:
            enum_num = 11
        elif num == 524251:
            enum_num = 12
        elif num == 524292:
            enum_num = 13
        elif ((num >= 262913) and (num <= 262928)):
            enum_num = 14 + (num-262913)
        elif ((num >= 327681) and (num <= 327696)):
            enum_num = 30 + (num-327681)
        elif num == 393218:
            enum_num = 46
        elif num == 393217:
            enum_num = 47
        elif num == 458754:
            enum_num = 48
        elif num == 458753:
            enum_num = 49
        else:
            enum_num_state = False
        return enum_num_state, enum_num

    def enumerate_aperture_sony_a7( self, num ):

        enum_num = 0
        enum_num_state = True
        if num == 280:
            enum_num = 0
        elif num == 320:
            enum_num = 1
        elif num == 350:
            enum_num = 2
        elif num == 400:
            enum_num = 3
        elif num == 450:
            enum_num = 4 
        elif num == 500:
            enum_num = 5    
        elif num == 560:
            enum_num = 6     
        elif num == 630:
            enum_num = 7     
        elif num == 710:
            enum_num = 8   
        elif num == 800:
            enum_num = 9   
        elif num == 900:
            enum_num = 10  
        elif num == 1000:
            enum_num = 11         
        elif num == 1100:
            enum_num = 12   
        elif num == 1300:
            enum_num = 13    
        elif num == 1400:
            enum_num = 14     
        elif num == 1600:
            enum_num = 15         
        elif num == 1800:
            enum_num = 16       
        elif num == 2000:
            enum_num = 17         
        elif num == 2200:
            enum_num = 18               
        else:
            enum_num_state = False
        return enum_num_state, enum_num


    def enumerate_iso_sony_a7( self, num ):

        enum_num = 0
        enum_num_state = True
        if num == 0:
            enum_num = 0
        elif num == 50:
            enum_num = 1
        elif num == 64:
            enum_num = 2
        elif num == 80:
            enum_num = 3
        elif num == 100:
            enum_num = 4
        elif num == 125:
            enum_num = 5
        elif num == 160:
            enum_num = 6
        elif num == 200:
            enum_num = 7
        elif num == 250:
            enum_num = 8
        elif num == 320:
            enum_num = 9
        elif num == 400:
            enum_num = 10
        elif num == 500:
            enum_num = 11
        elif num == 640:
            enum_num = 12
        elif num == 800:
            enum_num = 13
        elif num == 1000:
            enum_num = 14
        elif num == 1250:
            enum_num = 15
        elif num == 1600:
            enum_num = 16
        elif num == 2000:
            enum_num = 17
        elif num == 2500:
            enum_num = 18
        elif num == 3200:
            enum_num = 19
        elif num == 4000:
            enum_num = 20
        elif num == 5000:
            enum_num = 21
        elif num == 6400:
            enum_num = 22
        elif num == 8000:
            enum_num = 23 
        elif num == 10000:
            enum_num = 24  
        elif num == 12800:
            enum_num = 25 
        elif num == 16000:
            enum_num = 26   
        elif num == 20000:
            enum_num = 27 
        elif num == 25600:
            enum_num = 28  
        elif num == 32000:
            enum_num = 29 
        elif num == 40000:
            enum_num = 30
        elif num == 51200:
            enum_num = 31 
        elif num == 64000:
            enum_num = 32   
        elif num == 80000:
            enum_num = 33       
        elif num == 102400:
            enum_num = 34                         
        else:
            enum_num_state = False
        return enum_num_state, enum_num

    def enumerate_ex_pro_sony_a7( self, num ):

        enum_num = 0
        enum_num_state = True
        if num == 32859:
            enum_num = 2
        else:
            enum_num_state = False
        return enum_num_state, enum_num

    def enumerate_focus_area_sony_a7( self, num ):

        enum_num = 0
        enum_num_state = True
        if ((num >= 1) and (num <= 7)):
            enum_num = num - 1
        else:
            enum_num_state = False
        return enum_num_state, enum_num

    def enumerate_focus_sony_a7( self, num ):

        enum_num = 0
        enum_num_state = True
        enum_num_state = True
        if num == 2:
            enum_num = 0
        else:
            enum_num_state = False
        return enum_num_state, enum_num

    def enumerate_shutter_sony_a7( self, num ):

        enum_num = 0
        enum_num_state = True
        if num == 0:
            enum_num = 0        
        if num == 19660810:
            enum_num = 1
        elif num == 16384010:
            enum_num = 2
        elif num == 13107210:
            enum_num = 3
        elif num == 9830410:
            enum_num = 4
        elif num == 8519690:
            enum_num = 5
        elif num == 6553610:
            enum_num = 6
        elif num == 5242890:
            enum_num = 7
        elif num == 3932170:
            enum_num = 8
        elif num == 3276810:
            enum_num = 9
        elif num == 2621450:
            enum_num = 10
        elif num == 2097162:
            enum_num = 11
        elif num == 1638410:
            enum_num = 12
        elif num == 1310730:
            enum_num = 13
        elif num == 1048586:
            enum_num = 14
        elif num == 851978:
            enum_num = 15
        elif num == 655370:
            enum_num = 16
        elif num == 524298:
            enum_num = 17
        elif num == 393226:
            enum_num = 18
        elif num == 327690:
            enum_num = 19
        elif num == 262154:
            enum_num = 20
        elif num == 65539:
            enum_num = 21
        elif num == 65540:
            enum_num = 22
        elif num == 65541:
            enum_num = 23
        elif num == 65542:
            enum_num = 24
        elif num == 65544:
            enum_num = 25
        elif num == 65546:
            enum_num = 26
        elif num == 65549:
            enum_num = 27
        elif num == 65551:
            enum_num = 28
        elif num == 65556:
            enum_num = 29
        elif num == 65561:
            enum_num = 30
        elif num == 65566:
            enum_num = 31
        elif num == 65576:
            enum_num = 32
        elif num == 65586:
            enum_num = 33
        elif num == 65596:
            enum_num = 34
        elif num == 65616:
            enum_num = 35
        elif num == 65636:
            enum_num = 36
        elif num == 65661:
            enum_num = 37
        elif num == 65696:
            enum_num = 38 
        elif num == 65736:
            enum_num = 39 
        elif num == 65786:
            enum_num = 40
        elif num == 65856:
            enum_num = 41 
        elif num == 65936:
            enum_num = 42 
        elif num == 66036:
            enum_num = 43 
        elif num == 66176:
            enum_num = 44  
        elif num == 66336:
            enum_num = 45  
        elif num == 66536:
            enum_num = 46  
        elif num == 66786:
            enum_num = 47
        elif num == 67136:
            enum_num = 48 
        elif num == 67536:
            enum_num = 49  
        elif num == 68036:
            enum_num = 50   
        elif num == 68736:
            enum_num = 51  
        elif num == 69536:
            enum_num = 52  
        elif num == 70536:
            enum_num = 53  
        elif num == 71936:
            enum_num = 54 
        elif num == 73536:
            enum_num = 55             
        else:
            enum_num_state = False
        return enum_num_state, enum_num

    def enumerate_white_bal_sony_a7( self, num ):

        enum_num = 0
        enum_num_state = True
        if num == 0:
            enum_num = 0
        elif num == 17:
            enum_num = 1
        elif num == 18:
            enum_num = 2
        elif num == 19:
            enum_num = 3
        elif num == 20:
            enum_num = 4
        elif num == 33:
            enum_num = 5
        elif num == 34:
            enum_num = 6
        elif num == 35:
            enum_num = 7
        elif num == 36:
            enum_num = 8
        elif num == 48:
            enum_num = 9
        elif num == 1:
            enum_num = 10
        elif num == 256:
            enum_num = 11
        elif num == 257:
            enum_num = 12
        elif num == 258:
            enum_num = 13
        elif num == 259:
            enum_num = 14
        else:
            enum_num_state = False
        return enum_num_state, enum_num

    #def setSonyCamISOData( self, mem, mavObj, timeout1=100, timeout2=50, no_timeout1_retry=1, no_timeout2_retry=1 ):
    
    #    ret = False
    #    readSuccess = False
    #    print(" =========== sony cam iso ================ ")
        
        # 
    #    timeout1 = timeout1 * no_timeout1_retry
    #    timeout2 = timeout2 * no_timeout2_retry
        #
    #    while (readSuccess == False) and (timeout1 > 0):
    #        reqDat, prevDat, readSuccess  = mavObj.getVal_sony_iso(mavObj.STATE_CAM_READING,timeout1)
    #        timeout1 -= timeout1                                          # no retries
    #        print("Why !!!!!!!! {readSuccess} {reqDat} {prevDat}")
            
    #    print(f"set to ISO {reqDat} {prevDat} {timeout1} {mavObj.state}")
        
    #    if ((not (reqDat == mavlinkSonyCamWriteVals.STATE_INIT) and not (reqDat == prevDat)) and not(timeout1 <= 0)):
    #        ee = self.enumerate_iso_sony_a7(reqDat)
    #        print(f"enumeration value for iso {ee} req {reqDat}")
    #        ans = self.set_sony_iso( ee ) 
    #        print(ans)
    #        exit(90)
    #        if not (ans is None):  
    #            if (len(ans)==0):
    #                print("length of command return was zero")
    #                return ret                
    #            writeSuccess = False
    #            while (writeSuccess == False) and (timeout2 > 0): 
    #                try:
    #                    writeSuccess = mavObj.setVal_sony_iso(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
    #                    ret = ( ans[1] == reqDat ) 
    #                except Exception as err_msg:                
    #                    print("write sony iso failed to set iso")
    #                timeout2 -= timeout2                                  # no retries                
    #            if ( ret == True ):
    #                ret = self.setSonyObjData( mem, int(ans[1]) ) 
        #exit(200)                    
    #    return ret
    def setSonyCamISOData( self, mem, mavObj, timeout1=100, timeout2=50, no_timeout1_retry=1, no_timeout2_retry=1 ):
    
        ret = False
        readSuccess = False
        print(" =========== set sony cam iso ================ ")
        
        # 
        timeoutS1 = timeout1 * no_timeout1_retry

        #
        while (readSuccess == False) and (timeoutS1 > 0):
            reqDat, prevDat, readSuccess  = mavObj.getVal_sony_iso(mavObj.STATE_CAM_READING,timeout1)
            timeoutS1 -= timeout1                                          # no retries
            print(f"In iterator {readSuccess} {reqDat} {prevDat}")
            
        print(f"set to ISO r={reqDat} p={prevDat} time={timeout1} state={mavObj.state}")
        
        if ((not (int(reqDat) == mavlinkSonyCamWriteVals.STATE_INIT) and not (int(reqDat) == int(prevDat))) and (readSuccess == True)):
            timeoutS2 = timeout2 * no_timeout2_retry
            ret,ee = self.enumerate_iso_sony_a7(int(reqDat))
            if (ret == False):
                print(f"\033[31m Error Invalid parameter Iso {reqDat}\033[0m")
                writeSuccess = False
                while (writeSuccess == False) and (timeoutS2 > 0): 
                    writeSuccess = mavObj.setVal_sony_iso(int(prevDat),mavObj.STATE_CAM_WRITING,mavObj.DONT_WRITE_PREV_DATA,timeout2) 
                    timeoutS2 -= timeout2                                  # no retries  
                return writeSuccess
            print(f"enumeration value for iso {ee} req {reqDat}")
            ans = self.set_sony_iso( ee ) 
            # exit(90)
            if not (ans is None):         
                if (len(ans)==0):
                    print("setting iso the length of command return was zero")
                    return ret  
                print(f" \033[32m set the ISO from/to :: {ans} \033[0m")                       
                writeSuccess = False
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_iso(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                            print(f" write {writeSuccess}")
                    else:
                        print(f" what wat {ans[1]}=={reqDat}")
                except Exception as err_msg:                
                   print("\033[31m write sony iso failed to set iso \033[0m")                    
                if ( writeSuccess == True ):
                    ret = self.setSonyObjData( mem, int(ans[1]) ) 
        else:
            ret = ( int(prevDat) == int(reqDat) )
            if ret == False:
                print(f"\033[32m timeout error trying to set iso to \033[4;42;31m {reqDat} \033[0m")
        #exit(200)                    
        return ret
        
    def setSonyCamApertureData( self, mem, mavObj, timeout1=100, timeout2=50, no_timeout1_retry=1, no_timeout2_retry=1 ):
    
        ret = False
        readSuccess = False
        print(" =========== set sony cam aperture ================ ")
        
        # 
        timeoutS1 = timeout1 * no_timeout1_retry

        #
        while (readSuccess == False) and (timeoutS1 > 0):
            reqDat, prevDat, readSuccess  = mavObj.getVal_sony_aperture(mavObj.STATE_CAM_READING,timeout1)
            timeoutS1 -= timeout1                                          # no retries
            
        if ((not (int(reqDat) == mavObj.STATE_INIT) and not (int(reqDat) == int(prevDat))) and (readSuccess == True)):
            timeoutS2 = timeout2 * no_timeout2_retry
            ret,e = self.enumerate_aperture_sony_a7(int(reqDat))
            if (ret == False):
                print(f"\033[31m Error Invalid parameter aperture {reqDat}\033[0m")
                writeSuccess = False
                while (writeSuccess == False) and (timeoutS2 > 0): 
                    writeSuccess = mavObj.setVal_sony_aperture(int(prevDat),mavObj.STATE_CAM_WRITING,mavObj.DONT_WRITE_PREV_DATA,timeout2) 
                    timeoutS2 -= timeout2                                  # no retries  
                return writeSuccess
            ans = self.set_sony_aperture( e ) 
            if not (ans is None):
                if (len(ans)==0):
                    print("length of command return was zero")
                    return ret       
                print(f" \033[32m set the Aperture from/to :: {ans} \033[0m")                           # 
                writeSuccess = False
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_aperture(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony aperture failed to set aperture \033[0m")                     
                if ( writeSuccess == True ):
                    ret = self.setSonyObjData( mem, int(ans[1]) ) 
        else:
            ret = ( int(prevDat) == int(reqDat) )
            if ret == False:
                print(f"\033[32m timeout error trying to set aperture to \033[4;42;31m {reqDat}\033[0m")               
        return ret 

    def setSonyCamExProData( self, mem, mavObj, timeout1=100, timeout2=50, no_timeout1_retry=1, no_timeout2_retry=1 ):
    
        ret = False
        readSuccess = False
        print(" =========== set sony ex pro ================ ")
        
        # 
        timeoutS1 = timeout1 * no_timeout1_retry

        #
        while (readSuccess == False) and (timeoutS1 > 0):
            reqDat, prevDat, readSuccess  = mavObj.getVal_sony_ex_pro(mavObj.STATE_CAM_READING,timeout1)
            timeoutS1 -= timeout1
            
        if ((not (int(reqDat) == mavObj.STATE_INIT) and not (int(reqDat) == int(prevDat))) and (readSuccess == True)):
            timeoutS2 = timeout2 * no_timeout2_retry
            ret,ee = self.enumerate_ex_pro_sony_a7(int(reqDat))
            if (ret == False):
                print(f"\033[31m Error Invalid parameter exposure program mode {reqDat}\033[0m")
                writeSuccess = False
                while (writeSuccess == False) and (timeoutS2 > 0): 
                    writeSuccess = mavObj.setVal_sony_ex_pro(int(prevDat),mavObj.STATE_CAM_WRITING,mavObj.DONT_WRITE_PREV_DATA,timeout2) 
                    timeoutS2 -= timeout2                                  # no retries  
                return writeSuccess            
            ans = self.set_sony_ex_pro( ee ) 
            print(f" \033[32m set the ex=Pro from/to :: {ans}\033[0m")   
            if not (ans is None):    
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret             # 
                print(f" \033[32m set the ex=Pro from/to :: {ans} \033[0m")  
                writeSuccess = False
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_ex_pro(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony expro failed to set expro \033[0m")                    
                if ( writeSuccess == True ):
                    ret = self.setSonyObjData( mem, int(ans[1]) ) 
        else:
            ret = ( int(prevDat) == int(reqDat) )
            if ret == False:
                print(f"\033[32m timeout error trying to set expro to \033[4;42;31m {reqDat} \033[0m")                     
        return ret

    def setSonyCamFocusData( self, mem, mavObj, timeout1=100, timeout2=50, no_timeout1_retry=1, no_timeout2_retry=1 ):
    
        ret = False
        readSuccess = False
        print(" =========== set sony focus mode ================ ")
        # 
        timeoutS1 = timeout1 * no_timeout1_retry

        #
        while (readSuccess == False) and (timeoutS1 > 0):
            reqDat, prevDat, readSuccess  = mavObj.getVal_sony_focus(mavObj.STATE_CAM_READING,timeout1)
            timeoutS1 -= timeout1
            
        if ((not (int(reqDat) == mavObj.STATE_INIT) and not (int(reqDat) == int(prevDat))) and (readSuccess == True)):
            timeoutS2 = timeout2 * no_timeout2_retry
            ret,ee = self.enumerate_focus_sony_a7(int(reqDat))
            if (ret == False):
                print(f"\033[31m Error Invalid parameter focus mode {reqDat}\033[0m")
                writeSuccess = False
                while (writeSuccess == False) and (timeoutS2 > 0): 
                    writeSuccess = mavObj.setVal_sony_focus(int(prevDat),mavObj.STATE_CAM_WRITING,mavObj.DONT_WRITE_PREV_DATA,timeout2) 
                    timeoutS2 -= timeout2                                  # no retries  
                return writeSuccess    
            ans = self.set_sony_focus( ee ) 
            if not (ans is None):  
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret             # 
                print(f" \033[32m set the focus mode from/to :: {ans} \033[0m")   
                writeSuccess = False
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_focus(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony focus mode failed to set focus mode \033[0m")                    
                if ( writeSuccess == True ):
                    ret = self.setSonyObjData( mem, int(ans[1]) ) 
        else:
            ret = ( int(prevDat) == int(reqDat) )
            if ret == False:
                print(f"\033[32m timeout error trying to set focus mode to \033[4;42;31m {reqDat} \033[0m")                            
        return ret

    def setSonyCamFocusAreaData( self, mem, mavObj, timeout1=100, timeout2=50, no_timeout1_retry=1, no_timeout2_retry=1 ):
    
        ret = False
        readSuccess = False
        print(" =========== set sony focus area ================ ")
        # 
        timeoutS1 = timeout1 * no_timeout1_retry
        
        #
        while (readSuccess == False) and (timeoutS1 > 0):
            reqDat, prevDat, readSuccess  = mavObj.getVal_sony_focus_area(mavObj.STATE_CAM_READING,timeout1)
            timeoutS1 -= timeout1
            
        if ((not (int(reqDat) == mavObj.STATE_INIT) and not (int(reqDat) == prevDat)) and (readSuccess == True)):
            timeoutS2 = timeout2 * no_timeout2_retry
            ret,ee = self.enumerate_focus_area_sony_a7(int(reqDat))
            if (ret == False):
                print(f"\033[31m Error Invalid parameter focus area {reqDat}\033[0m")
                writeSuccess = False
                while (writeSuccess == False) and (timeoutS2 > 0): 
                    writeSuccess = mavObj.setVal_sony_focus_area(int(prevDat),mavObj.STATE_CAM_WRITING,mavObj.DONT_WRITE_PREV_DATA,timeout2) 
                    timeoutS2 -= timeout2                                  # no retries  
                return writeSuccess 
            ans = self.set_sony_focus_area( ee ) 
            if not (ans is None):   
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret             # 
                writeSuccess = False
                print(f" \033[32m set the focus area from/to :: {ans} \033[0m")   
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_focus_area(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony focus area failed to set focus area \033[0m")                    
                if ( writeSuccess == True ):
                    ret = self.setSonyObjData( mem, int(ans[1]) ) 
        else:
            ret = ( int(prevDat) == int(reqDat) )
            if ret == False:
                print(f"\033[32m timeout error trying to set focus area to \033[4;42;31m {reqDat} \033[0m")                
        return ret

    def setSonyCamShutSpdData( self, mem, mavObj, timeout1=100, timeout2=50, no_timeout1_retry=1, no_timeout2_retry=1 ):
    
        ret = False
        readSuccess = False
        print(" =========== set sony shutter speed ================ ")
        # 
        timeoutS1 = timeout1 * no_timeout1_retry
            
        #
        while (readSuccess == False) and (timeoutS1 > 0):
            reqDat, prevDat, readSuccess  = mavObj.getVal_sony_shutter(mavObj.STATE_CAM_READING,timeout1)
            timeoutS1 -= timeout1
            
        print(f"set to ISO r={reqDat} p={prevDat} time={timeout1} state={mavObj.state}")
        
        if ((not (int(reqDat) == mavObj.STATE_INIT) and not (int(reqDat) == int(prevDat))) and (readSuccess == True)):
            timeoutS2 = timeout2 * no_timeout2_retry
            ret,ee = self.enumerate_shutter_sony_a7(int(reqDat))
            if (ret == False):
                print(f"\033[31m Error Invalid parameter shutter speed {reqDat}\033[0m")
                writeSuccess = False
                while (writeSuccess == False) and (timeoutS2 > 0): 
                    writeSuccess = mavObj.setVal_sony_shutter(int(prevDat),mavObj.STATE_CAM_WRITING,mavObj.DONT_WRITE_PREV_DATA,timeout2) 
                    timeoutS2 -= timeout2                                  # no retries  
                return writeSuccess 
            ans = self.set_sony_shutter( ee ) 
            if not (ans is None): 
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret             # 
                writeSuccess = False
                print(f" \033[32m set the shutter speed from/to :: {ans} \033[0m")   
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_shutter(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            print(f"written {ans[1]} {writeSuccess}")
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony shutter speed failed to set shutter speed \033[0m")                    
                if ( writeSuccess == True ):
                    print(f"saving..... {ans[1]} {writeSuccess}")               
                    ret = self.setSonyObjData( mem, int(ans[1]) ) 
        else:
            ret = ( int(prevDat) == int(reqDat) )
            if ret == False:
                print(f"\033[32m timeout error trying to set shutter speed to \033[4;42;31m {reqDat} \033[0m")                
        return ret

    def setSonyCamWhiteBalaData( self, mem, mavObj, timeout1=100, timeout2=50, no_timeout1_retry=1, no_timeout2_retry=1 ):
    
        ret = False
        readSuccess = False
        print(" =========== set sony white balance ================ ")
        # 
        timeoutS1 = timeout1 * no_timeout1_retry
        
        #
        while (readSuccess == False) and (timeoutS1 > 0):
            reqDat, prevDat, readSuccess  = mavObj.getVal_sony_white_bal(mavObj.STATE_CAM_READING,timeout1)
            timeoutS1 -= timeout1
            
        if ((not (int(reqDat) == mavObj.STATE_INIT) and not (int(reqDat) == int(prevDat))) and (readSuccess == True)):
            timeoutS2 = timeout2 * no_timeout2_retry
            ret,ee = self.enumerate_white_bal_sony_a7(int(reqDat))
            if (ret == False):
                print(f"\033[31m Error Invalid parameter white balance {reqDat}\033[0m")
                writeSuccess = False
                while (writeSuccess == False) and (timeoutS2 > 0): 
                    writeSuccess = mavObj.setVal_sony_white_bal(int(prevDat),mavObj.STATE_CAM_WRITING,mavObj.DONT_WRITE_PREV_DATA,timeout2) 
                    timeoutS2 -= timeout2                                  # no retries  
                return writeSuccess 
            ans = self.set_sony_white_bal( ee ) 
            if not (ans is None):   
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret             # 
                writeSuccess = False
                print(f" \033[32m set the white balance from/to :: {ans} \033[0m")   
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_white_bal(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony white balance failed to set white balance \033[0m")                    
                if ( writeSuccess == True ):
                    ret = self.setSonyObjData( mem, int(ans[1]) ) 
        else:
            ret = ( int(prevDat) == int(reqDat) )
            if ret == False:
                 print(f"\033[32m timeout error trying to set white balance to \033[4;42;31m {reqDat} \033[0m")                    
        return ret
        
    def setSonyCamStillCapModeData( self, mem, mavObj, timeout1=100, timeout2=50, no_timeout1_retry=1, no_timeout2_retry=1 ):
    
        ret = False
        readSuccess = False
        print(" =========== set sony still capture mode ================ ")
        # 
        timeoutS1 = timeout1 * no_timeout1_retry
            
        #
        while (readSuccess == False) and (timeoutS1 > 0):
            reqDat, prevDat, readSuccess  = mavObj.getVal_sony_still_cap_mode(mavObj.STATE_CAM_READING,timeout1)
            timeoutS1 -= timeout1
            
        if ((not (int(reqDat) == mavObj.STATE_INIT) and not (int(reqDat) == int(prevDat))) and (readSuccess == True)):
            timeoutS2 = timeout2 * no_timeout2_retry
            ret,ee = self.enumerate_still_cap_sony_a7(int(reqDat))
            if (ret == False):
                print(f"\033[31m Error Invalid parameter still capture {reqDat}\033[0m")
                writeSuccess = False
                while (writeSuccess == False) and (timeoutS2 > 0): 
                    writeSuccess = mavObj.setVal_sony_still_cap_mode(int(prevDat),mavObj.STATE_CAM_WRITING,mavObj.DONT_WRITE_PREV_DATA,timeout2) 
                    timeoutS2 -= timeout2                                  # no retries  
                return writeSuccess 
            ans = self.set_sony_still_cap( ee ) 
            if not (ans is None): 
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret             # 
                writeSuccess = False
                print(f" \033[32m set the still capture mode from/to :: {ans} \033[0m")   
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_still_cap_mode(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony still capture mode failed to set still capture mode \033[0m")                    
                if ( writeSuccess == True ):
                    ret = self.setSonyObjData( mem, int(ans[1]) ) 
        else:
            ret = ( int(prevDat) == int(reqDat) )
            if ret == False:
                print(f"\033[32m timeout error trying to set still capture mode to \033[4;42;31m {reqDat} \033[0m")               
        return ret  

    #
    # would go into mavlink class if it was in multi-tasking mode
    #
    def sendMavlinkMessageForParamObject( self, obj, the_connection, Timeout=5 ):

        if (obj.updateNeeded == True):
        
            # send mavlink message  obj.name obj.signal obj.numberOfVals      
            #
            getName, getValueforMAVSending, getPrev, myState = obj.get_value_data(obj.STATE_MAV_READING, Timeout) 
            print(f"-------------- obj update found for param_value {getName} {getValueforMAVSending} {getPrev} {myState}")
            sendVal = struct.unpack('f', struct.pack('I', getValueforMAVSending))[0]  
            if (myState == True):
                try:
                    the_connection.mav.param_value_send(
                        getName.encode('ascii'),
                        sendVal,
                        mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
                        obj.numberOfVals,
                        obj.index)
                    ret = True
                except Exception as err_msg:
                    print("Failed to send param value message : %s" % (err_msg))
                    ret = False
                if (ret == True):
                    writeSuccess = False
                    TimeCount = 0
                    while (writeSuccess == False) and (Timeout > TimeCount):
                        # obj.updateNeeded = False
                        writeSuccess = obj.set_update_flag( False, obj.STATE_MAV_WRITING )
                        TimeCount += 1
                return ret

    #
    # would go into mavlink class if it was in multi-tasking mode
    #
    def sendMavlinkMessageForParamExtObject( self, obj, the_connection, Timeout=5 ):

        v, r = obj.get_ack_send( obj.STATE_MAV_READING )
        if ((v == True) and (r == True)):
        # if (obj.ack_send == True):
        
            # send mavlink message  obj.name obj.signal obj.numberOfVals      
            #
            getName, getValueforMAVSending, getPrev, myState = obj.get_value_data(obj.STATE_MAV_READING, Timeout) 
            print(f"-------------- obj update found for param_value {getName} {getValueforMAVSending} {getPrev} {myState}")
            if (myState == True):
                try:
                    the_connection.mav.param_ext_value_send(
                        getName.encode('ascii'),
                        str(getValueforMAVSending).encode('ascii'),
                        mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
                        obj.numberOfVals,
                        obj.index)
                    ret = True
                except Exception as err_msg:
                    print("Failed to send param value message : %s" % (err_msg))
                    ret = False
                if (ret == True):
                    writeSuccess = False
                    TimeCount = 0
                    while (writeSuccess == False) and (Timeout > TimeCount):
                        # obj.updateNeeded = False
                        writeSuccess = obj.set_ack_send( False, obj.STATE_MAV_WRITING )
                        TimeCount += 1
                return ret
                
#
# Pymavlink Library

# Acknowledgements:
# Thank you to Andrew Tridgell, the mastermind behind pymavlink and MAVProxy
# Thread code from http://stackoverflow.com/questions/730645/python-wxpython-doing-work-continuously-in-the-background
# Serial port code taken from http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
# UDP http://snakeproject.ru/rubric/article.php?art=python_udp_network_server_client

# AirCamPro :- 21/10/21 support android kivy serial driver
#
# when you install pymavlink you also need to use mavgen to generate the libraries
# instructions are shown here
# https://mavlink.io/en/mavgen_python/
# https://github.com/ArduPilot/pymavlink/blob/master/mavutil.py

# multi-tasking info
# https://ja.pymotw.com/2/multiprocessing/basics.html
# https://techacademy.jp/magazine/20607 

# sudo apt-get install python3-dev python3-opencv python3-wxgtk4.0 python3-pip python3-matplotlib python3-lxml
# sudo apt-get install libxml++2.6-dev
# sudo pip install dronekit

# ================== Compatible Joysticks =========================================
# X-Box 360 Controller (name: "Xbox 360 Controller")
# Playstation 4 Controller (name: "PS4 Controller")
# X-Box 360 Controller (name: "Controller (XBOX 360 For Windows)")
#  
from pymavlink import mavutil   # ref:- https://www.ardusub.com/developers/pymavlink.html
#import wx
import sys, serial, glob, threading
# for serial message out packing
import struct

# this is included for android serial and to detect the android platform using kivy
# ref:- https://github.com/frmdstryr/kivy-android-serial
# install kivy with the following in your conda environment
# conda install kivy -c conda-forge
#`from kivy.utils import platform
# from kvserial.driver import CdcAcmSerialPort

# to list ports using the serial library
from serial.tools import list_ports

BUTTON_CONNECT = 10
BUTTON_ARM = 20

# ethernet UDP communication and joystick
#
# python3 -m pip install -U pygame --user
import socket
import pygame
JOYSTICK_UDP_PORT = 14556
JOY_SCALE = 1000
MAX_SCALE = 32767
X_MAX = MAX_SCALE
Y_MAX = MAX_SCALE


MAV_TARGET = 110
MAV_SOURCE = 30

# import pymavlink.dialects.v10.lapwing as mavlink
# this is a custom dialect which i cant find
# this chooses version 1 you would need to change the ACK function TODO
#
# from mavlink_python_libs import com1 as commonV1
# import com1 as mavdefs
#
from mavlink_python_libs import com2 as commonV1
#from my_python_libs import com2 as commonV1
import com2 as mavdefs

import math
import time
import array as arr

#from mypymavlink import mavutilcust as custommav

#
# multithreading control via asyncio
#
import asyncio
import time

import numpy as np
import os

# ============== control Raspberry Pi IO ===============
# sudo apt-get install rpi.gpio
#
#import RPi.GPIO as GPIO
 
# to use Raspberry Pi board pin numbers
#GPIO.setmode(GPIO.BOARD)
 
# set up the GPIO channels - one input and one output here
#GPIO.setup(11, GPIO.IN)
#GPIO.setup(12, GPIO.OUT)

#---------------------------------------------------------------------------

class fifo(object):
    def __init__(self):
        self.buf = []
    def write(self, data):
        self.buf += data
        return len(data)
    def read(self):
        return self.buf.pop(0)

import re
        
# mavlink communicator class (without GUI)
#

class MAVFrame():

    RCV_COMMAND = mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE
    RPM2 = 0
    ACK_RESULT = mavutil.mavlink.MAV_RESULT_UNSUPPORTED
    DEFAULT_SYS_ID = 1
    ACK_ALL_DATA_COMPLETE = 99
 
    CAMERA_INFORMATION = 259                 #camera_information
    CAMERA_SETTINGS = 260
    STORAGE_INFORMATION = 261
    CAMERA_CAPTURE_STATUS = 262
    CAMERA_IMAGE_CAPTURED = 263
    VIDEO_STREAM = 269

    # camera informations (default camera routines will retrieve this)
    time_boot_ms = 1
    firmware_version = 12
    focal_length = 1.1
    sensor_size_h = 3.0
    sensor_size_v = 4.0
    flags = 4
    resolution_h = 300
    resolution_v = 400
    cam_definition_version = 2
    #vendor_name_nd = np.dtype([('A',np.uint8)])
    #model_name_nd = np.dtype([('B',np.uint8)])
    #vendor_name_list = [65] 
    #model_name_list = [67]
    #vendor_name = "A" 
    #model_name = "B"
    lens_id = 1
    cam_definition_uri = "http://10.0.2.51/cam_defs"
                                           
    # camera settings
    mode_id = 3                                                      #  Camera mode
    zoomLevel = 7                                                    #  Current zoom level (0.0 to 100.0, NaN if not known)*/
    focusLevel = 9 

    # storage informations
    total_capacity = 1.2                                                       #  [MiB] Total capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.
    used_capacity = 1.1                                                        #  [MiB] Used capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.
    available_capacity = 0.1                                                   #  [MiB] Available storage capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.
    read_speed = 0.67                                                          #  [MiB/s] Read speed.
    write_speed = 0.76                                                         #  [MiB/s] Write speed.
    storage_id = 1                                                             #  Storage ID (1 for first, 2 for second, etc.)
    storage_count = 2                                                          #  Number of storage devices
    status = 0 
    #status = mavutil.mavlink.STORAGE_STATUS_READY 

    # camera capture status
    image_interval = 3.3                                                      #  [s] Image capture interval
    recording_time_ms = 10000                                                 #  [ms] Time since recording started
    available_capacity = 0.34                                                 #  [MiB] Available storage capacity.
    image_status = 1                                                          #  Current status of image capturing (0: idle, 1: capture in progress, 2: interval set but idle, 3: interval set and capture in progress)
    video_status = 1                                                          #  Current status of video capturing (0: idle, 1: capture in progress)
    image_count = 11

    # video stream
    framerate = 30.0                                                          # [Hz] Frame rate.
    bitrate = 3000                                                            # [bits/s] Bit rate.
    Vflags = 3                                                                 # Bitmap of stream status flags.
    Vresolution_h = 300                                                        # [pix] Horizontal resolution.
    Vresolution_v = 400                                                        # [pix] Vertical resolution.
    rotation = 90                                                             # [deg] Video image rotation clockwise.
    hfov = 45                                                                 # [deg] Horizontal Field of view.
    stream_id = 2                                                             # Video Stream ID (1 for first, 2 for second, etc.)
    count = 4                                                                 # Number of streams available.
    stream_type = mavutil.mavlink.VIDEO_STREAM_TYPE_MPEG_TS_H264              # Type of stream.
    videoname = "vid_001"
    video_uri = "http://10.0.0.56/vids/001.mov"

    # camera image captured
    time_utc = 667700                                                        #  [us] Timestamp (time since UNIX epoch) in UTC. 0 for unknown.
    lat = 30                                                                 #  [degE7] Latitude where image was taken
    lon = 40                                                                 #  [degE7] Longitude where capture was taken
    alt = 11                                                                 #  [mm] Altitude (MSL) where image was taken
    relative_alt = 12                                                        #  [mm] Altitude above ground
    q = [1,0,0,0]                                                            #  Quaternion of camera orientation (w, x, y, z order, zero-rotation is 0, 0, 0, 0)
    image_index = 4                                                          #  Zero based index of this image (image count since armed -1)
    camera_id = 1                                                            #  Camera ID (1 for first, 2 for second, etc.)
    capture_result = 1                                                       #  Boolean indicating success (1) or failure (0) while capturing this image.
    file_url = "http://10.1.2.3/img/1.jpg"

    # camera feedback
    time_usec = 10000 
    cam_idx = 1 
    img_idx = 1 
    # already lat, 
    lng = lon 
    alt_msl = 2 
    alt_rel = 4 
    roll = 6
    pitch = 1 
    yaw = 2 
    foc_len = 7 
    CFflags = 3
                
    ACK_ERROR = 0
    errRCV_COMMAND = 0
    errRPM2 = 0

    # task control flag
    #
    task_control_1 = 0

    # global constants
    #
    GOT_ERROR = 1
    GOT_SUCCESS = 2
    GOT_BAD = 3
    GOT_UNFORMAT = 4 
    
    # used to decide what is being requested from the calling (GCS) station
    #
    type_of_msg = 0
   
    g_count = 0
    pin_no = 0

    # defines for camera ID file
    #
    CAM_XML_FILE =  "alpha_cam_new.xml"
    NETWORK_ID = 1

    def __init__(self, pinNum=26):
        #self.setUPPiRelayNumBCM()
        #self.setPinINput(pinNum)
        MAVFrame.pin_no=pinNum

    def __del__(self):  
        class_name = self.__class__.__name__  
        print('{} Deleted'.format(class_name))  

    #
    # check our operating system
    #
    def check_os( self ):
        if ((sys.platform=='linux2') or (sys.platform=='linux')): return 1
        elif  sys.platform=='win32': return 2
        else: return 3
 
    def update_utc_label( self ):
        if (self.check_os() == 1):
            cmd = "date +%s"
            self.time_utc = os.popen(cmd).read()

    def update_uptime_label( self ):
        if (self.check_os() == 1):
            cmd = "uptime"
            upTimStr = os.popen(cmd).read().split(",")
            dd = upTimStr[0].split()
            days = int(dd[2])
            xx = dd[0].split(":")
            hours = int(xx[0])
            mins = int(xx[1])
            secs = int(xx[2])
            self.time_boot_ms = (days*60*60*24) + (hours*60*60) + (mins*60) + secs
            #print(f"boot tim {self.time_boot_ms} { (days*60*60*24) + (hours*60*60) + (mins*60) + secs }")
        
    def on_click_connect(self,e):
        #"""
        #Process a click on the CONNECT button
        #Attempt to connect to the MAV using the specified port and baud rate,
        #then subscribe a function called check_heartbeat that will listen for
        #a heartbeat message, as well as a function that will print all incoming
        #MAVLink messages to the console.
        #"""

        port = self.cb_port.GetValue()
        baud = int(self.cb_baud.GetValue())
        self.textOutput.AppendText("Connecting to " + port + " at " + str(baud) + " baud\n")

        self.master = mavutil.mavlink_connection(port, baud=baud)
        self.thread = threading.Thread(target=self.process_messages)
        self.thread.setDaemon(True)
        self.thread.start()

        self.master.message_hooks.append(self.check_heartbeat)
        self.master.message_hooks.append(self.check_rcv_data_msg)
        self.master.message_hooks.append(self.log_message)


        print("Connecting to " + port + " at " + str(baud) + "baud")
        self.textOutput.AppendText("Waiting for APM heartbeat\n")
        return

    def on_click_arm(self,e):
        #"""
        #Process a click on the ARM button
        #Send an arm message to the MAV, then subscribe a function called
        #check_arm_ack that will listen for a positive confirmation of arming.
        # """
        self.textOutput.AppendText("Arming motor\n")
        print("******arming motor*********")
        self.master.arducopter_arm()

        self.master.message_hooks.append(self.check_arm_ack)

    def log_message(self,caller,msg):
        if msg.get_type() != 'BAD_DATA':
            print(str(msg))
        return

    def process_messages(self):
        #"""
        #This runs continuously. The mavutil.recv_match() function will call mavutil.post_message()
        #any time a new message is received, and will notify all functions in the master.message_hooks list.
        #"""
        while True:
            msg = self.master.recv_match(blocking=True)
            if not msg:
                return
            if msg.get_type() == "BAD_DATA":
                if mavutil.all_printable(msg.data):
                    sys.stdout.write(msg.data)
                    sys.stdout.flush()

    def check_heartbeat(self,caller,msg):
        #"""
        #Listens for a heartbeat message
        #Once this function is subscribed to the dispatcher, it listens to every
        #incoming MAVLINK message and watches for a 'HEARTBEAT' message. Once
        #that message is received, the function updates the GUI and then
        # unsubscribes itself.
        #" ""

        if msg.get_type() ==  'HEARTBEAT':
            self.textOutput.AppendText("Heartbeat received from APM (system %u component %u)\n" % (self.master.target_system, self.master.target_component))
            self.master.message_hooks.remove(self.check_heartbeat)

    def check_arm_ack(self, caller, msg):
        #"""
        #Listens for confirmation of motor arming
        #Once this function is subscribed to the dispatcher, it listens to every
        #incomign MAVLINK message and watches for the "Motor armed!" confirmation.
        #Once the message is received, teh function updates the GUI and then
        #unsubscribes itself.
        #"""

        if msg.get_type() == 'STATUSTEXT':
            if "Throttle armed" in msg.text:
                self.textOutput.AppendText("Motor armed!")
                self.master.message_hooks.remove(self.check_arm_ack)

    def check_rcv_data_msg(self, msg):
    
        if msg.get_type() == 'RC_CHANNELS':
            self.textOutput.AppendText("RC Channel message (system %u component %u)\n" % (self.master.target_system, self.master.target_component))
            self.textOutput.AppendText("chan1 %u chan2 %u)\n" % (self.master.chan1_raw, self.master.chan2_raw))
            self.master.message_hooks.remove(self.check_rcv_data_msg)
        elif msg.get_type() == 'COMMAND_LONG':
            self.textOutput.AppendText("Long message received (system %u component %u)\n" % (self.master.target_system, self.master.target_component))
            self.textOutput.AppendText("Command %u p1 %u p2 %u p3 %u p4 %u \n" % (self.master.command, self.master.param1, self.master.param2, self.master.param3, self.master.param4))
            self.textOutput.AppendText("p5 %u p6 %u p7 %u \n" % (self.master.param5, self.master.param6, self.master.param7))
            self.master.message_hooks.remove(self.check_rcv_data_msg)        
        elif msg.get_type() == 'CAMERA_IMAGE_CAPTURED':
            self.textOutput.AppendText("Cam Cap message received (system %u component %u)\n" % (self.master.target_system, self.master.target_component)) 
            self.textOutput.AppendText("lat %u lon %u alt %u\n" % (self.master.lat, self.master.lon, self.master.alt)) 
            self.textOutput.AppendText("URL %u)\n" % (self.master.file_url))
            self.master.message_hooks.remove(self.check_rcv_data_msg) 
            
    def OnClose(self, e):
        self._mgr.UnInit()
        self.Close()

    # if you want this then uncomment these lines for the android kivy libraries as well (instructions to install are above)

    #`from kivy.utils import platform
    # from kvserial.driver import CdcAcmSerialPort

    def serial_ports(self):
    # Lists all available serial ports
    #:raises EnvironmentError:
    #    On unsupported or unknown platforms
    #:returns:
    #    A list of available serial ports
    #
        if 'ANDROID_BOOTLOGO' in os.environ:                                # detect android first as if using sys alone, it returns linux
        #if platform == 'android':                                          using kivy instead  
            ports = '/dev/ttyACM0'
        else:
            if sys.platform.startswith('win'):
                ports = ['COM' + str(i + 1) for i in range(256)]

            elif sys.platform.startswith('linux') or sys.platform.startswith('linux2') or sys.platform.startswith('cygwin'):    # check this shows /dev/ttyAMA0 on raspberry pi.
            # this is to exclude your current terminal "/dev/tty"
                ports = glob.glob('/dev/tty[A-Za-z]*')

            elif sys.platform.startswith('darwin'):                         # apple mac support if using darwin
                ports = glob.glob('/dev/tty.*')

            else:
                ports = list_ports.comports()                               # Outputs list of available serial ports should do the rest e.g. riscos atheos os2 freebsd aix etc
 
        if len(ports) == 0:                                                     
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            if 'ANDROID_BOOTLOGO' in os.environ:                            # device android
                s = CdcAcmSerialPort(port)
                s.close()
                result.append(port)
            else:
                try:
                    s = serial.Serial(port)
                    s.close()
                    result.append(port)
                except (OSError, serial.SerialException):
                    pass
        return result


    def print_red(self,text,value):
        print("\033[31m %s : %6.3f"%(text,value))
        
    def print_yellow(self,text,value):
        print("\033[33m %s : %6.3f"%(text,value))

    def print_2_yellow(self,text,value1,value2):
        print("\033[33m %s : %6.3f %6.3f"%(text,value1,value2))

    def print_3_yellow(self,text,value1,value2,value3):
        print("\033[33m %s : %6.3f %6.3f %6.3f"%(text,value1,value2,value3))

    def print_3_blue(self,text,value1,value2,value3):
        print("\033[34m %s %6.3f %6.3f %6.3f"%(text,value1,value2,value3))
        
    def print_blue(self,text,value):
        print("\033[34m %s : %6.3f"%(text,value))
        
    def joystickInit(self):
        # Set the width and height of the screen [width,height]
        size = [500, 700]
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("----- My test of mavlink and joystick -----")
        
        pygame.init()
        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()
        # Initialize the joysticks 
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        # Get ready to print
        textPrint = TextPrint()
    
    def initUDPSocket(self,bind):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # bind the socket if this is a server (pass bind==1)
        if bind == 1:
           host = 'localhost'
           port = JOYSTICK_UDP_PORT
           sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
           addr = (host,port)
           sock.bind(addr)
        sock.setblocking(0)
        return sock

    def closeUDPSocket(self,udp_socket):
        udp_socket.close()
        
    def serverReadUDPSocket(self,udp_socket,port):
        conn, addr = udp_socket.recvfrom(port)
        return conn,addr
        
    def clientReadUDPSocket(self,udp_socket,port):
        dataV = udp_socket.recvfrom(port)
        return dataV
        
    def joyMavlinkInit(self):
        mav = mavutil.mavlink.MAVLink(fifo())
        mav.srcSystem = MAV_SOURCE                          # set to master

    def blockMouseDown(self,block_flag):
        if block_flag:
            pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
        else:
            pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)

    def blockMouseUp(self,block_flag):
        if block_flag:
            pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
        else:
            pygame.event.set_allowed(pygame.MOUSEBUTTONUP)

    def checkMouseDwnBlock(self):
        print ('MOUSEBUTTONDOWN is block: ', pygame.event.get_blocked(pygame.MOUSEBUTTONDOWN))

    def checkMouseUpBlock(self):
        print ('MOUSEBUTTONUP is block: ', pygame.event.get_blocked(pygame.MOUSEBUTTONUP))

    def write_mav_serial_data(self, serial, x ):
        serial.write(struct.pack(x))
        
    def write_pack_serial_data(self, serial, x, y, z, roll, pitch, yaw):
        serial.write(struct.pack('<chhhhhh', 'S',x, y, z, roll, pitch, yaw))

    def test_linear(self, serial, lenght=200, times=1000, delta=0.05):
        for angle in xrange(1, times, 5):
            a = angle * math.pi / 180
            self.write_serial_data(serial, int(lenght * math.cos(a)), int(lenght * math.sin(a)),0,0,0,0)
            time.sleep(delta)
        self.write_serial_data(serial, 0,0,0,0,0,0)
 
    def test_angles(self, serial, lenght=200, times=1000, delta=0.05):
        for angle in xrange(1, times, 5):
            a = angle * math.pi / 180
            self.write_serial_data(0, 0,0,0,int(30 * math.cos(a)),int(30 * math.sin(-a)))
            time.sleep(delta)
        self.write_serial_data(serial, 0,0,0,0,0,0)
 
    def test_yaw(self, serial, lenght=200, times=1000, delta=0.05):
        for angle in xrange(1, times, 5):
            a = angle * math.pi / 180
            self.write_serial_data(serial, int(lenght * math.cos(a)),0,0,int(30 * math.sin(a)),0,0)
            time.sleep(delta)
        self.write_serial_data(serial, 0,0,0,0,0,0)
        
    def processJoystickSendMavlink(self,sock):

        msgbuf = None
        # -------- Main Program Loop -----------
        while done == False:
            btns = 0
            thrust = 0.0
            rudder = 0.0

            # EVENT PROCESSING STEP
            for event in pygame.event.get(): # User did something

                screen.fill(WHITE)
                textPrint.reset()
                
                # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
                # QUIT - none
                # ACTIVEEVENT - gain, state
                # KEYDOWN - unicode, key, mod
                # KEYUP - key, mod
                # MOUSEMOTION - pos, rel, buttons
                # MOUSEBUTTONUP - pos, button
                # MOUSEBUTTONDOWN - pos, button
                # JOYAXISMOTION - joy, axis, value
                # JOYBALLMOTION - joy, ball, rel
                # JOYHATMOTION - joy, hat, value
                # JOYBUTTONUP - joy, button
                # JOYBUTTONDOWN - joy, button
                # VIDEORESIZE - size, w, h
                # VIDEOEXPOSE - none
                # USEREVENT – code
                if event.type == pygame.QUIT:
                    done=True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.print_2_yellow("Mouse button down pressed.",event.button,event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.print_2_yellow("Mouse button up pressed.",event.button,event.pos)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.print_2_yellow("Joystick button down pressed.",event.button,event.joy)
                elif event.type == pygame.JOYBUTTONUP:
                    self.print_2_yellow("Joystick button up released.",event.button,event.joy)
                elif event.type == pygame.JOYAXISMOTION:
                    self.print_3_yellow("Joystick axis motion.",event.joy,event.axis,event.value)
                elif event.type == pygame.JOYBALLMOTION:
                    self.print_3_yellow("Joystick ball motion.",event.joy,event.ball,event.rel)
                elif event.type == pygame.JOYHATMOTION:
                    self.print_3_yellow("Joystick hat motion",event.joy,event.hat,event.value)
                elif event.type == pygame.VIDEORESIZE:
                    self.print_3_blue("video re-size.",event.size,event.w,event.h)
                elif event.type == pygame.KEYDOWN:
                    self.print_3_yellow("key down ",event.unicode,event.key,event.mod)
                elif event.type == pygame.KEYUP:
                    self.print_2_yellow("key up ",event.key,event.mod)

                # Get the name from the OS for the controller/joystick
                name = joystick.get_name()
                print("Joystick name: {}".format(name) )

                # get the buttons
                buttons = joystick.get_numbuttons()
                for i in range( buttons ):
                    button = joystick.get_button( i )
                    print( "Button {:>2} value: {}".format(i,button) )

                # get the hats
                # Hat switch. All or nothing for direction, not like joysticks.
                # Value comes back in an array.
                hats = joystick.get_numhats()
                print( "Number of hats: {}".format(hats) )
                textPrint.indent()

                for i in range( hats ):
                    hat = joystick.get_hat( i )
                    print( "Hat {} value: {}".format(i, str(hat)) )
            
                # Getting available devices
                for id in range(pygame.joystick.get_count()):
                    print( "devices list : %u %d %s" % (id, pygame.joystick.Joystick(id).get_name()))
                    
                # Get thrust and break first
                # mix 2 shifts in single channels
                thr =  (joystick.get_axis(5) + 1) / 2
                brk = -(joystick.get_axis(2) + 1) / 2
                thrust = thr + brk
                self.print_yellow("Thrust value ",thrust)

                # this is the x axis
                rudder = joystick.get_axis(0)
                self.print_blue("Rudder value ",rudder)

                # now collect all buttons
                btns = 0
                for i in range(joystick.get_numbuttons()):
                     btns |= joystick.get_button(i) << i

                # Usually axis run in pairs, up/down for one, and left/right for
                # the other.
                axes = joystick.get_numaxes()
                print( "Number of axes: {}".format(axes) )
                textPrint.indent()

                for i in range( axes ):
                    axis = joystick.get_axis( i )
                    print( "Axis {} value: {:>6.3f}".format(i, axis) )
                textPrint.unindent()

                # Update events in pygame
                pygame.event.pump()
        
                # pack acquired data and throw it to socket
                msg = mavutil.mavlink.MAVLink_manual_control_message( target = MAV_TARGET, x = X_MAX, y = Y_MAX, z = round(thrust*JOY_SCALE), r = round(rudder*JOY_SCALE), buttons = btns)
                msgbuf = msg.pack(mav)

                try:
                    jid = joystick.get_instance_id()
                except AttributeError:
                # get_instance_id() is an SDL2 method
                   jid = joystick.get_id()
                
                print( "Joystick {}".format(jid))

                try:
                    guid = joystick.get_guid()
                except AttributeError:
                # get_guid() is an SDL2 method
                    pass
                else:
                    print("GUID: {}".format(guid))   
                
            # Limit to 20 frames per second
            clock.tick(25)
            if msgbuf:
                # send the message on the UDP Port
                sock.sendto(msgbuf, ('', JOYSTICK_UDP_PORT))   
                # send the message on serial
                # write_mav_serial_data(serial, msgbuf)
                
        # Close the window and quit.
        # If you forget this line, the program will 'hang'
        # on exit if running from IDLE.
        pygame.joystick.quit()
        pygame.quit()

    # make a mavlink connection using mavutil like ardusub does....
    #
    # Create the connection and return it for use with the other functions
    #
    # TODO::: change the port and see if this can run entirely paralel with camera
    #         take picture on another port
    #
    def makeMAVlinkConn(self):
        try:
            #the_conection = mavutil.mavlink_connection('udpin:0.0.0.0:14560',autoreconnect=True)
            the_conection = mavutil.mavlink_connection('udpin:0.0.0.0:14550',autoreconnect=True, source_system=1, source_component=100)
            return the_conection,True
        except Exception as err_msg:
            print("Failed to connect : %s" % (err_msg))
            return the_conection,False

    def makeNewMAVlinkConn(self,id):
        try:
            #the_conection = mavutil.mavlink_connection('udpin:0.0.0.0:14560',autoreconnect=True, source_system=id)
            the_conection = mavutil.mavlink_connection('udpin:0.0.0.0:14550',autoreconnect=True, source_system=id, source_component=100)
            return the_conection,True
        except Exception as err_msg:
            print("Failed to connect : %s" % (err_msg))
            return the_conection,False
            
    # Send heartbeat from a GCS (types are define as enum in the dialect file). 
    #
    def mavlink_send_GCS_heartbeat(self, the_conection): 
        print(" heartbeat..............................  %s\n"%(mavutil.mavlink.MAV_TYPE_CAMERA))
        try:
            the_conection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_CAMERA, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavutil.mavlink.MAV_STATE_ACTIVE)
            ret = True
        except Exception as err_msg:
            print("Failed to send GCS heartbeat : %s" % (err_msg))
            ret = False
        return ret
        
    # Send heartbeat from a MAVLink application.
    #
    def mavlink_send_OBC_heartbeat2(self, the_connection):   
        try:
            mavutil.mavlink.heartbeat_send(mavutil.mavlink.MAV_TYPE_CAMERA, mavutil.mavlink.MAV_AUTOPILOT_GENERIC, 0, 0, 0)
            ret = True
        except Exception as err_msg:
            print("Failed to send OBC heartbeat : %s" % (err_msg))
            ret = False
        return ret
        
    # Receive heartbeat from a MAVLink application.
    #
    def mavlink_rcv_heartbeat(self, the_connection):   
        try:
            the_connection.wait_heartbeat()
            ret = True
        except Exception as err_msg:
            print("Failed to wait for heartbeat : %s" % (err_msg))
            ret = False
        return ret
        
    # Sets a value to the rc channel
    #
    def mavlink_set_rc_channel_pwm(self, the_connection, channel_id, pwm=1500):
    #""" Set RC channel pwm value
    #Args:
    #    channel_id (TYPE): Channel ID
    #    pwm (int, optional): Channel pwm value 1100-1900
    #"""
        if channel_id < 1 or channel_id > 18:
            print("Channel does not exist.")
            return

        # Mavlink 2 supports up to 18 channels:
        # https://mavlink.io/en/messages/common.html#RC_CHANNELS_OVERRIDE
        rc_channel_values = [65535 for _ in range(18)]
        rc_channel_values[channel_id - 1] = pwm

        try:
            the_connection.mav.rc_channels_override_send( the_connection.target_system, the_connection.target_component, *rc_channel_values )  
            ret = True            
        except Exception as err_msg:
            print("Failed to set RC Chan PWM : %s" % (err_msg))
            ret = False
        return ret
        
    # drives a gimbal axis controller to the pitch roll yaw specified
    #
    def gimbal_move_to( self, the_connection, tilt=0, roll=0, pan=0):
    #"""
    #Moves gimbal to given position
        try:
            the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component, mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL, 1, tilt, roll, pan, 0, 0, 0, mavutil.mavlink.MAV_MOUNT_MODE_MAVLINK_TARGETING)
            ret = True
        except Exception as err_msg:
            print("Failed to move gimbal using command long : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink10(self,connID):
     #   '''return True if using MAVLink 1.0 or later'''
        return float(connID.WIRE_PROTOCOL_VERSION) >= 1

    def mavlink20(self,connID):
     #  '''return True if using MAVLink 2.0 or later'''
        return float(connID.WIRE_PROTOCOL_VERSION) >= 2		        

    #   Set relay_pin to value of state
    def mavlink_set_relay(self, the_connection, relay_pin=0, state=True):

        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_DO_SET_RELAY, # command
                0, # Confirmation
                relay_pin, # Relay Number
                int(state), # state (1 to indicate arm)
                0, # param3 (all other params meaningless)
                0, # param4
                0, # param5
                0, # param6
                0) # param7
            ret = True
        except Exception as err_msg:
            print("Failed to set relay using command long : %s" % (err_msg))
            ret = False
        return ret
        

    # ref:- https://mavlink.io/en/messages/common.html#MAV_CMD
    
    def mavlink_video_stop_capture(self, the_connection, streamNo):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_VIDEO_STOP_CAPTURE, # command
                0, # Confirmation
                streamNo, # stream number
                0, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7
            ret = True
        except Exception as err_msg:
            print("Failed to stop video capture using command long : %s" % (err_msg))
            ret = False
        return ret            
            

    def mavlink_video_start_capture(self, the_connection, streamNo, freq):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_VIDEO_START_CAPTURE, # command
                0, # Confirmation
                streamNo, # stream number
                freq, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7
            ret = True
        except Exception as err_msg:
            print("Failed to start video capture using command long : %s" % (err_msg))
            ret = False
        return ret            

    def mavlink_image_stop_capture(self, the_connection):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_IMAGE_STOP_CAPTURE, # command
                0, # Confirmation
                0, # param1
                0, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7
            ret = True
        except Exception as err_msg:
            print("Failed to stop image capture using command long : %s" % (err_msg))
            ret = False
        return ret 
        
    def mavlink_image_start_capture(self, the_connection, interval, totalImages, seqNo):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_IMAGE_START_CAPTURE, # command
                0, # Confirmation
                0, # param1
                interval, # Desired elapsed time between two consecutive pictures (in seconds)
                totalImages, # Total number of images to capture. 0 to capture forever/until MAV_CMD_IMAGE_STOP_CAPTURE.
                seqNo, # Capture sequence number starting from 1. This is only valid for single-capture (param3 == 1), otherwise set to 0. Increment the capture ID for each capture command to prevent double captures when a command is re-transmitted
                0, # param5
                0, # param6
                0) # param7
            ret = True
        except Exception as err_msg:
            print("Failed to start image capture using command long : %s" % (err_msg))
            ret = False
        return ret             

    def mavlink_video_stop_streaming(self, the_connection, streamNo):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,                 # target_system
                the_connection.target_component,              # target_component
                mavutil.mavlink.MAV_CMD_VIDEO_STOP_STREAMING, # command
                0,                                            # Confirmation
                streamNo,                                     # stream number
                0,                                            # param2
                0,                                            # param3 
                0,                                            # param4
                0,                                            # param5
                0,                                            # param6
                0)                                            # param7
            ret = True
        except Exception as err_msg:
            print("Failed to send stop streaming using command long : %s" % (err_msg))
            ret = False
        return ret              

    def mavlink_do_ftp_send(self, the_connection, network, payload):
        MAX_CHUNK_BYTES = 251
        numOfchunk = round(len(payload) / MAX_CHUNK_BYTES)
        for i in range(numOfchunk):
            #print(f"ftp send chunk {i} offset {i*251}")
            msgpay = []
            b = 1
            for b in range(MAX_CHUNK_BYTES):
                try:
                    msgpay.append(payload[b+(i*251)])
                except Exception as e:
                    msgpay.append(0)
            try:
                the_connection.mav.file_transfer_protocol_send (
                    network,
                    the_connection.target_system,        # target_system
                    the_connection.target_component,     # target_component
                    msgpay )
            except Exception as e:
                 print(f" ftp send exception {e} \nchunk {i} @ offset {i*MAX_CHUNK_BYTES}") 

    def mavlink_video_start_streaming(self, the_connection, streamNo):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,                   # target_system
                the_connection.target_component,                # target_component
                mavutil.mavlink.MAV_CMD_VIDEO_START_STREAMING,  # command
                0,                                              # Confirmation
                streamNo,                                       # stream number
                0,                                              # param2
                0,                                              # param3 
                0,                                              # param4
                0,                                              # param5
                0,                                              # param6
                0)                                              # param7
            ret = True
        except Exception as err_msg:
            print("Failed to send start streaming using command long : %s" % (err_msg))
            ret = False
        return ret               

    # suitable variables to drive CamMode
    #
    MAV_CAMERA_MODE_IMAGE = 0
    MAV_CAMERA_MODE_VIDEO = 1
    MAV_CAMERA_MODE_IMAGE_SURVEY = 2
    
    def mavlink_video_set_camera_mode(self, the_connection, camMode):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_SET_CAMERA_MODE, # command
                0, # Confirmation
                0, # param1
                camMode, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7
            ret = True
        except Exception as err_msg:
            print("Failed to send video set camera mode using command long : %s" % (err_msg))
            ret = False
        return ret 
        
    # suitable variables to drive CamZoomType
    #
    MAV_ZOOM_TYPE_STEP = 0	        # Zoom one step increment (-1 for wide, 1 for tele)
    MAV_ZOOM_TYPE_CONTINUOUS = 1	# Continuous zoom up/down until stopped (-1 for wide, 1 for tele, 0 to stop zooming)
    MAV_ZOOM_TYPE_RANGE = 2         # Zoom value as proportion of full camera range (a value between 0.0 and 100.0)
    MAV_ZOOM_TYPE_FOCAL_LENGTH = 3  # Zoom value/variable focal length in milimetres
    
    def mavlink_video_set_camera_zoom(self, the_connection, camZoomType, camZoomValue):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_SET_CAMERA_MODE, # command
                0, # Confirmation
                camZoomType, # param1
                camZoomValue, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7
            ret = True
        except Exception as err_msg:
            print("Failed to send camera zoom using command long : %s" % (err_msg))
            ret = False
        return ret 
        
    MAV_FOCUS_TYPE_STEP = 0	       # Focus one step increment (-1 for focusing in, 1 for focusing out towards infinity).
    MAV_FOCUS_TYPE_CONTINUOUS = 1  # Continuous focus up/down until stopped (-1 for focusing in, 1 for focusing out towards infinity, 0 to stop focusing)
    MAV_FOCUS_TYPE_RANGE = 2	   # Focus value as proportion of full camera focus range (a value between 0.0 and 100.0)
    MAV_FOCUS_TYPE_METERS = 3	   # Focus value in metres

    def mavlink_video_set_camera_focus(self, the_connection, camFocusType, camFocusValue):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavdefs.MAV_CMD_SET_CAMERA_FOCUS, # command
                0, # Confirmation
                camFocusType, # param1
                camFocusValue, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7
            ret = True
        except Exception as err_msg:
            print("Failed to send camera focus using command long : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_do_digicam_configure(self, the_connection, camMode, camShutterSpeed, camAperture, camISO, camExposure, camCommandIdentity, camEngineCutOff):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONFIGURE, # command
                0, # Confirmation
                camMode, # param1
                camShutterSpeed, # param2
                camAperture, # param3 
                camISO, # param4
                camExposure, # param5
                camCommandIdentity, # param6
                camEngineCutOff) # param7
            ret = True
        except Exception as err_msg:
            print("Failed to send digicam configure using command long : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_do_digicam_control(self, the_connection, camSessionControl, camZoomAbsolute, camZoomRelative, camFocus, camShootCommand, camCommandIdentity, camShotID):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL, # command
                0, # Confirmation
                camSessionControl, # param1
                camZoomAbsolute, # param2
                camZoomRelative, # param3 
                camFocus, # param4
                camShootCommand, # param5
                camCommandIdentity, # param6
                camShotID) # param7
            ret = True
        except Exception as err_msg:
            print("Failed to send digicam control using command long : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_do_video_control(self, the_connection, camID, camTransmission, camInterval, camRecording):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_DO_CONTROL_VIDEO, # command
                0, # Confirmation
                camID, # param1
                camTransmission, # param2
                camInterval, # param3 
                camRecording, # param4
                0, # param5
                0, # param6
                0) # param7 
            ret = True
        except Exception as err_msg:
            print("Failed to send do video control using command long : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_get_camera_settings(self, the_connection):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_SETTINGS, # command
                0, # Confirmation
                1, # param1
                0, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7 
            ret = True
        except Exception as err_msg:
            print("Failed to get cam settings using command long : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_get_storage_info(self, the_connection, StoId):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_REQUEST_STORAGE_INFORMATION, # command
                0, # Confirmation
                StoId, # param1
                1, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7 
            ret = True
        except Exception as err_msg:
            print("Failed to get storage info using command long : %s" % (err_msg))
            ret = False
        return ret
        

    def mavlink_get_capture_status(self, the_connection):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS, # command
                0, # Confirmation
                1, # param1
                0, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7 
            ret = True
        except Exception as err_msg:
            print("Failed to get capture status using command long : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_get_stream_info(self, the_connection):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_REQUEST_VIDEO_STREAM_INFORMATION, # command
                0, # Confirmation
                1, # param1
                0, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7 
            ret = True
        except Exception as err_msg:
            print("Failed to get stream info using command long : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_reset_camera(self, the_connection):
        #if self.mavlink10():
        try:
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_RESET_CAMERA_SETTINGS, # command
                0, # Confirmation
                1, # param1
                0, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7 
            ret = True
        except Exception as err_msg:
            print("Failed to reset camera using command long : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_set_camera_trig_interval(self, the_connection, camTriggerCycle, camShutterIntegration):
        #if self.mavlink10():
        try:        
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_DO_SET_CAM_TRIGG_INTERVAL, # command
                0, # Confirmation
                camTriggerCycle, # param1
                camShutterIntegration, # param2
                0, # param3 
                0, # param4
                0, # param5
                0, # param6
                0) # param7 
            ret = True
        except Exception as err_msg:
            print("Failed to set camera trip interval using command long : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_set_camera_to_quaternion(self, the_connection, q1, q2, q3, q4):
        #if self.mavlink10():
        try:        
            the_connection.mav.command_long_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL_QUAT, # command
                0, # Confirmation
                q1, # param1
                q2, # param2
                q3, # param3 
                q4, # param4
                0, # param5
                0, # param6
                0) # param7 
            ret = True
        except Exception as err_msg:
            print("Failed to set camera to quartenion using command long : %s" % (err_msg))
            ret = False
        return ret

    # convert to integer param_value from mavlink
    #
    def mav_param_type_conv( self, typ, value ):

        if ( int(mavutil.mavlink.MAV_PARAM_TYPE_INT64) >= int(typ) ):
            return int(struct.unpack('I', struct.pack('f', value))[0])   
        else:
            return value

    # convert an integer param_value to be sent on mavlink
    #
    def param_to_mav_msg_conv( self, typ, value ):

        if ( int(mavutil.mavlink.MAV_PARAM_TYPE_INT64) >= int(typ) ):
            return float(struct.unpack('f', struct.pack('I', value))[0])   
        else:
            return value

    # param_value handlers : seperate ones to allow changes in data type etc
    #
    def mavlink_send_param_value_iso(self, the_connection, val ):
        
        print("\033[36m sending a parameter : iso ") 
        d = struct.unpack('f', struct.pack('I', val))[0]
        try:
            the_connection.mav.param_value_send(
            "S_ISO".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            1)
            return True
        except Exception as err_msg: 
            print("Failed to send param value message 1: %s" % (err_msg))
            return False

    def mavlink_send_param_value_aper(self, the_connection, val ):

        print("\033[31m sending a parameter : aperture ")     
        d = struct.unpack('f', struct.pack('I', val))[0]
        try:
            the_connection.mav.param_value_send(
            "S_APERTURE".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            2)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 2: %s" % (err_msg))
            return False

    def mavlink_send_param_value_expro(self, the_connection, val ):

        print("\033[32m sending a parameter : expro ")      
        d = struct.unpack('f', struct.pack('I', val))[0]
        try:
            the_connection.mav.param_value_send(
            "S_EX_PRO_MODE".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            3)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 3: %s" % (err_msg))
            return False

    def mavlink_send_param_value_focus(self, the_connection, val ):

        print("\033[33m sending a parameter : focus mode ")      
        d = struct.unpack('f', struct.pack('I', val))[0]           
        try:
            the_connection.mav.param_value_send(
            "S_FOCUS_MODE".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            4)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 4: %s" % (err_msg))
            return False

    def mavlink_send_param_value_focus_area(self, the_connection, val ):

        print("\033[34m sending a parameter : focus area ")      
        p = struct.unpack('f', struct.pack('I', val))[0] 
        try:
            the_connection.mav.param_value_send(
            "S_FOCUS_AREA".encode('ascii'),
            p,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            5)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 5: %s" % (err_msg))
            return False

    def mavlink_send_param_value_shut_spd(self, the_connection, val ):

        print("\033[35m sending a parameter : shutter speed ")       
        d = struct.unpack('f', struct.pack('I', val))[0]
        try:
            the_connection.mav.param_value_send(
            "S_SHUT_SPD".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            6)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 6: %s" % (err_msg))
            return False

    def mavlink_send_param_value_white_bal(self, the_connection, val ):

        print("\033[37m sending a parameter : white balance ")       
        d = struct.unpack('f', struct.pack('I', val))[0]
        try:
            the_connection.mav.param_value_send(
            "S_WHITE_BAL".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            7)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 7: %s" % (err_msg))
            return False

    def mavlink_send_param_value_still_cap(self, the_connection, val ):

        print("\033[38m sending a parameter : still capture mode ")    
        d = struct.unpack('f', struct.pack('I', val))[0]
        try:
            the_connection.mav.param_value_send(
            "S_STILL_CAP".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            8)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 8: %s" % (err_msg))
            return False

    def mavlink_send_param_ext_value_iso(self, the_connection, val ):
        
        print("\033[31m sending an ext parameter iso") 
        d = str(val)
        try:
            the_connection.mav.param_ext_value_send(
            "S_ISO".encode('ascii'),
            d.encode('ascii'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            8,
            1)
            return True
        except Exception as err_msg: 
            print("Failed to send param value message 1: %s" % (err_msg))
            return False

    def mavlink_send_param_ext_value_aper(self, the_connection, val ):

        print("\033[32m sending an ext parameter aper")     
        d = str(val)
        try:
            the_connection.mav.param_ext_value_send(
            "S_APERTURE".encode('ascii'),
            d.encode('ascii'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            8,
            2)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 2: %s" % (err_msg))
            return False

    def mavlink_send_param_ext_value_expro(self, the_connection, val ):

        print("\033[33m sending an ext parameter expro")     
        d = str(val)
        try:
            the_connection.mav.param_ext_value_send(
            "S_EX_PRO_MODE".encode('ascii'),
            d.encode('ascii'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            8,
            3)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 3: %s" % (err_msg))
            return False

    def mavlink_send_param_ext_value_focus(self, the_connection, val ):

        print("\033[34m sending an ext parameter focus")    
        d = str(val)           
        try:
            the_connection.mav.param_ext_value_send(
            "S_FOCUS_MODE".encode('ascii'),
            d.encode('ascii'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            8,
            4)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 4: %s" % (err_msg))
            return False

    def mavlink_send_param_ext_value_focus_area(self, the_connection, val ):

        print("\033[35m sending an ext parameter focus area")       
        p = str(val) 
        try:
            the_connection.mav.param_ext_value_send(
            "S_FOCUS_AREA".encode('ascii'),
            p.encode('ascii'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            8,
            5)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 5: %s" % (err_msg))
            return False

    def mavlink_send_param_ext_value_shut_spd(self, the_connection, val ):

        print("\033[36m sending an ext parameter shutter speed")     
        d = str(val)
        try:
            the_connection.mav.param_ext_value_send(
            "S_SHUT_SPD".encode('ascii'),
            d.encode('ascii'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            8,
            6)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 6: %s" % (err_msg))
            return False

    def mavlink_send_param_ext_value_white_bal(self, the_connection, val ):

        print("\033[37m sending an ext parameter white balance")        
        d = str(val)
        try:
            the_connection.mav.param_ext_value_send(
            "S_WHITE_BAL".encode('ascii'),
            d.encode('ascii'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            8,
            7)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 7: %s" % (err_msg))
            return False

    def mavlink_send_param_ext_value_still_cap(self, the_connection, val ):

        print("\033[37m sending an ext parameter still capture")     
        d = str(val)
        try:
            the_connection.mav.param_ext_value_send(
            "S_STILL_CAP".encode('ascii'),
            d.encode('ascii'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            8,
            8)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 8: %s" % (err_msg))
            return False
            
    def mavlink_send_param_value(self, the_connection):
        
        print("\033[36m sending a parameter") 
        d = struct.unpack('f', struct.pack('I', 1))[0]
        try:
            the_connection.mav.param_value_send(
            "S_ISO".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            1)
            ret = True
        except Exception as err_msg: 
            print("Failed to send param value message 1: %s" % (err_msg))
            ret = False
        d = struct.unpack('f', struct.pack('I', 10))[0]
        try:
            the_connection.mav.param_value_send(
            "S_APERTURE".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            2)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message 2: %s" % (err_msg))
            ret = False
        d = struct.unpack('f', struct.pack('I', 30))[0]
        try:
            the_connection.mav.param_value_send(
            "S_EX_PRO_MODE".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            3)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message 3: %s" % (err_msg))
            ret = False
        d = struct.unpack('f', struct.pack('I', 5))[0]           
        try:
            the_connection.mav.param_value_send(
            "S_FOCUS_MODE".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            4)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message 4: %s" % (err_msg))
            ret = False
        p = struct.unpack('f', struct.pack('I', 11))[0] 
        try:
            the_connection.mav.param_value_send(
            "S_FOCUS_AREA".encode('ascii'),
            p,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            5)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message 5: %s" % (err_msg))
            ret = False
        d = struct.unpack('f', struct.pack('I', 675))[0]
        try:
            the_connection.mav.param_value_send(
            "S_SHUT_SPD".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            6)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message 6: %s" % (err_msg))
            ret = False
        d = struct.unpack('f', struct.pack('I', 76))[0]
        try:
            the_connection.mav.param_value_send(
            "S_WHITE_BAL".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            7)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message 7: %s" % (err_msg))
            ret = False
        d = struct.unpack('f', struct.pack('I', 7))[0]
        try:
            the_connection.mav.param_value_send(
            "S_STILL_CAP".encode('ascii'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            8)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message 8: %s" % (err_msg))
            ret = False
        return ret

    def mavlink_send_camera_information(self, the_connection):
        #if self.mavlink10():

        vendor_name_nd = np.dtype([('ABB',np.uint8)])
        model_name_nd = np.dtype([('BAC',np.uint8)])
        vendor_name_list = [65,66,66] 
        model_name_list = [66,65,67]
        vendor_name = "ABB" 
        model_name = "BAC"
        #
        # convert string to ascii list and make numpy array
        #
        vn = []
        mn = []
        j = 0
        for j in range(len(model_name)):
            mn.append(ord(model_name[j]))
        k = 0
        for k in range(len(vendor_name)):
            vn.append(ord(vendor_name[k]))
        u8_model_name = np.array(mn, np.uint8)
        u8_vendor_name = np.array(vn, np.uint8)
        mn_u8 = u8_model_name.astype(np.uint8)
        vn_u8 = u8_vendor_name.astype(np.uint8)

        arr_vendor = [0] * 32
        arr_vendor[0] = ord("A")

        arr_model = [0] * 32
        arr_model[0] = ord("C")

        #    "http://10.0.2.51/cam_defs/alpha_cam_new.xml".encode('ascii'))
        print("\033[33m Sending camera information")
        try:
            the_connection.mav.camera_information_send(
            100,
            arr_vendor,
            arr_model,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            391,
            1,
            "http://10.0.2.51/cam_defs".encode('ascii'))
            ret = True
        except Exception as err_msg:
            print("Failed to send camera information message : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_send_camera_settings(self, the_connection):
        #if self.mavlink10():
        try:    
            the_connection.mav.camera_settings_send(
                self.time_boot_ms,
                self.mode_id,                                                       #  Camera mode
                self.zoomLevel,                                                     #  Current zoom level (0.0 to 100.0, NaN if not known)*/
                self.focusLevel)  
            ret = True
        except Exception as err_msg:
            print("Failed to send camera settings message : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_send_storage_information(self, the_connection):
        #if self.mavlink10():
        #
        # This is a byte array of the string 
        #
        b = bytearray(b'ABB')
        #
        # forced uint8 with numpy
        #
        b8_numpy = np.array(b, np.uint8)
        #
        # ascii string encoded
        #
        nm = "storenm"
        try:
            u8_model_name = (nm).encode("ascii")
        except Exception as err_msg:
            print("\033[32m Failed to SET storage information message : %s " % (err_msg))
        print(f" sending storage info {u8_model_name} type {type(u8_model_name)}")
        try:    
            the_connection.mav.storage_information_send(
                self.time_boot_ms, 
                self.storage_id, 
                self.storage_count, 
                self.status, 
                self.total_capacity, 
                self.used_capacity, 
                self.available_capacity, 
                self.read_speed, 
                self.write_speed,
                1,
                np.array(u8_model_name,np.uint8),
                2)
            ret = True
        except Exception as err_msg:
            print("\033[32m Failed to send storage information message : %s type is %s" % (err_msg,type(u8_model_name)))
            ret = False
        return ret
        
    def mavlink_send_camera_capture_status(self, the_connection):
       
        try:           
            the_connection.mav.camera_capture_status_send(
                self.time_boot_ms, 
                self.image_status, 
                self.video_status, 
                self.image_interval, 
                self.recording_time_ms, 
                self.available_capacity,
                self.image_count) 
            ret = True
        except Exception as err_msg:
            print("Failed to send camera capture status message : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_send_video_stream_information(self, the_connection):
        #if self.mavlink10():
        print("    !!! sending the video stream information   !!! \n")
        try:             
            the_connection.mav.video_stream_information_send(
                self.stream_id, 
                self.count, 
                self.stream_type, 
                self.Vflags, 
                self.framerate, 
                self.Vresolution_h, 
                self.Vresolution_v, 
                self.bitrate, 
                self.rotation, 
                self.hfov, 
                #self.videoname, 
                (self.videoname).encode('ascii'),
                (self.video_uri).encode('ascii'))
            ret = True
        except Exception as err_msg:
            print("Failed to send video stream information message : %s" % (err_msg))
            ret = False
        return ret
        
    def mavlink_send_camera_image_captured(self, the_connection):
        #if self.mavlink10():
        b = bytearray(b'[2,3,4,5]')
        print(f"sending cam image cap {self.time_boot_ms}")
        try:  
            the_connection.mav.camera_image_captured_send(
                self.time_boot_ms, 
                self.time_utc, 
                self.camera_id, 
                self.lat, 
                self.lon, 
                self.alt, 
                self.relative_alt, 
                b, 
                self.image_index, 
                self.capture_result, 
                self.file_url)
            ret = True
        except Exception as err_msg:
            print("Failed to send camera image captured message : %s" % (err_msg))
            ret = False
        return ret
 
    def mavlink_send_camera_feedback(self, the_connection):
        #if self.mavlink10():
        print("\033[32m sending camera feedback")
        try:  
            the_connection.mav.camera_feedback_send( 
                self.time_usec, 
                the_connection.target_system, 
                self.cam_idx, 
                self.img_idx, 
                self.lat, 
                self.lng, 
                self.alt_msl, 
                self.alt_rel, 
                self.roll,
                self.pitch, 
                self.yaw, 
                self.foc_len, 
                self.CFflags)
            ret = True
            print("\033[36m success sending camera feedback")
        except Exception as err_msg:
            print("Failed to send camera feedback message : %s" % (err_msg))
            ret = False
        return ret

    # check with this function the order in python !!!!!!!!
    #
    def mavlink_send_param_ext_ack(self, the_connection, val, status_code, tag ):
        
        print("\033[38m acking the ext parameter iso") 
        d = str(val)
        try:
            the_connection.mav.param_ext_ack_send(
            tag.encode('ascii'),
            d,
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            status_code)
            ret = True
        except Exception as err_msg: 
            print("Failed to send param value message 1: %s" % (err_msg))
            ret = False

            
    def writeParamSetFromMavLink( self, msgString, mavObj, dataRcv, the_connection ):

        # must be EXACT tag match
        #patternISO = re.compile(r"\bS_ISO\b")
        #patternAper = re.compile(r"\bS_APERTURE\b")
        #patternExPro = re.compile(r"\bS_EX_PRO_MODE\b")
        #patternFocus = re.compile(r"\bS_FOCUS_MODE\b")
        #patternFocA = re.compile(r"\bS_FOCUS_AREA\b")
        #patternShSp = re.compile(r"\bS_SHUT_SPD\b")  
        #patternWhiBal = re.compile(r"S_WHITE_BAL") 
        #patternStCa = re.compile(r"\bS_STILL_CAP\b") 

        if (len(msgString) == 0):
            print("zero length tag passed")
            return False
            
        if not (msgString.find("S_ISO") == -1):
        #if (re.search(patternISO, msgString.upper())==True): 
            print(f"saw sonISO with {dataRcv}")
            if (mavObj.setMavIsoModeData( dataRcv )==True):
                print(f"setMavIsoModeData sonISO with {dataRcv}")
                return (self.mavlink_send_param_value_iso( the_connection, dataRcv )) 
        elif not (msgString.find("S_APERTURE") == -1):
        #elif (re.search(patternAper, msgString.upper())==True):
            if (mavObj.setMavApertureData( dataRcv )==True):        
                return (self.mavlink_send_param_value_aper( the_connection, dataRcv ))          
        elif not (msgString.find("S_EX_PRO_MODE") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            if (mavObj.setMavExProData( dataRcv )==True):        
                return (self.mavlink_send_param_value_expro( the_connection, dataRcv ))                   
        elif not (msgString.find("S_FOCUS_AREA") == -1):
        #elif (re.search(patternFocA, msgString.upper())==True): 
            if (mavObj.setMavFocusAreaData( dataRcv )==True):        
                return (self.mavlink_send_param_value_focus_area( the_connection, dataRcv ))           
        elif not (msgString.find("S_FOCUS_MODE") == -1):
        #elif (re.search(patternFocus, msgString.upper())==True):
            if (mavObj.setMavFocusData( dataRcv )==True): 
                return (self.mavlink_send_param_value_focus( the_connection, dataRcv ))                  
        elif not (msgString.find("S_SHUT_SPD") == -1):
        #elif (re.search(patternShSp, msgString.upper())==True):
            if (mavObj.setMavShutterData( dataRcv )==True):         
                return (self.mavlink_send_param_value_shut_spd( the_connection, dataRcv ))                               
        elif not (msgString.find("S_WHITE_BAL") == -1):
        #elif (re.search(patternWhiBal, msgString.upper())==True): 
            if (mavObj.setMavWhiteBalData( dataRcv )==True):        
                return (self.mavlink_send_param_value_white_bal( the_connection, dataRcv ))
        elif not (msgString.find("S_STILL_CAP") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavStillCapModeData( dataRcv )==True):        
                return (self.mavlink_send_param_value_still_cap( the_connection, dataRcv ))        
        else:
            print("unsupported variable name %s to val=%d :: NOT SET "%(msgString,dataRcv))
            return False

    def readParamSetFromMavLink( self, msgString, mavObj, the_connection ):

        # must be EXACT tag match
        #patternISO = re.compile(r"\bS_ISO\b")
        #patternAper = re.compile(r"\bS_APERTURE\b")
        #patternExPro = re.compile(r"\bS_EX_PRO_MODE\b")
        #patternFocus = re.compile(r"\bS_FOCUS_MODE\b")
        #patternFocA = re.compile(r"\bS_FOCUS_AREA\b")
        #patternShSp = re.compile(r"\bS_SHUT_SPD\b")  
        #patternWhiBal = re.compile(r"S_WHITE_BAL") 
        #patternStCa = re.compile(r"\bS_STILL_CAP\b") 

        v = 0
        p = 0
        r = False

        if (len(msgString) == 0):
            print("zero length tag passed")
            return False
            
        if not (msgString.find("S_ISO") == -1):
        #if (re.search(patternISO, msgString.upper())==True): 
            mavObj.mav_req_all_param |= mavlinkSonyCamWriteVals.ParamIso                                     # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavIsoModeData( )
            if (r == True):
                return ( self.mavlink_send_param_value_iso( the_connection, v ) )
            else:
                return False            
        elif not (msgString.find("S_APERTURE") == -1):
        #elif (re.search(patternAper, msgString.upper())==True): 
            mavObj.mav_req_all_param |= mavlinkSonyCamWriteVals.ParamAperture                                # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavApertureData( )
            if (r == True):
                return ( self.mavlink_send_param_value_aper( the_connection, v ) )  
            else:
                return False                 
        elif not (msgString.find("S_EX_PRO_MODE") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            mavObj.mav_req_all_param |= mavlinkSonyCamWriteVals.ParamExPro                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavExProData( )
            if (r == True):
                return ( self.mavlink_send_param_value_expro( the_connection, v ) )
            else:
                return False                 
        elif not (msgString.find("S_FOCUS_AREA") == -1):
        #elif (re.search(patternFocA, msgString.upper())==True): 
            mavObj.mav_req_all_param |= mavlinkSonyCamWriteVals.ParamFocusArea                                   # >>> set the bit to enable full read of parameter    
            v, p, r = mavObj.getMavFocusAreaData( )
            if (r == True):        
                return ( self.mavlink_send_param_value_focus_area( the_connection, v ) ) 
            else:
                return False                 
        elif not (msgString.find("S_FOCUS_MODE") == -1):
        #elif (re.search(patternFocus, msgString.upper())==True):
            mavObj.mav_req_all_param |= mavlinkSonyCamWriteVals.ParamFocus                                   # >>> set the bit to enable full read of parameter  
            v, p, r = mavObj.getMavFocusData( )
            if (r == True):
                return ( self.mavlink_send_param_value_focus( the_connection, v ) )
            else:
                return False                 
        elif not (msgString.find("S_SHUT_SPD") == -1):
        #elif (re.search(patternShSp, msgString.upper())==True): 
            mavObj.mav_req_all_param |= mavlinkSonyCamWriteVals.ParamShutSpd                                   # >>> set the bit to enable full read of parameter  
            v, p, r = mavObj.getMavShutterData( )
            if (r == True):
                return ( self.mavlink_send_param_value_shut_spd( the_connection, v ) )      
            else:
                return False                 
        elif not (msgString.find("S_WHITE_BAL") == -1):
        #elif (re.search(patternWhiBal, msgString.upper())==True):  
            mavObj.mav_req_all_param |= mavlinkSonyCamWriteVals.ParamWhiteBala                                   # >>> set the bit to enable full read of parameter  
            v, p, r = mavObj.getMavWhiteBalData( )
            if (r == True):
                return ( self.mavlink_send_param_value_white_bal( the_connection, v ) )        
            else:
                return False 
        elif not (msgString.find("S_STILL_CAP") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):  
            mavObj.mav_req_all_param |= mavlinkSonyCamWriteVals.ParamStillCap                                   # >>> set the bit to enable full read of parameter          
            v, p, r = mavObj.getMavStillCapModeData( )
            if (r == True):
                return ( self.mavlink_send_param_value_still_cap( the_connection, v ) )    
            else:
                return False                 
        else:
            print("unsupported variable name %s :: NOT SET "%(msgString))
            return False
            
    def writeParamExtSetFromMavLink( self, msgString, mavObj, dataRcv, the_connection ):

        # must be EXACT tag match
        #patternISO = re.compile(r"\bS_ISO\b")
        #patternAper = re.compile(r"\bS_APERTURE\b")
        #patternExPro = re.compile(r"\bS_EX_PRO_MODE\b")
        #patternFocus = re.compile(r"\bS_FOCUS_MODE\b")
        #patternFocA = re.compile(r"\bS_FOCUS_AREA\b")
        #patternShSp = re.compile(r"\bS_SHUT_SPD\b")  
        #patternWhiBal = re.compile(r"S_WHITE_BAL") 
        #patternStCa = re.compile(r"\bS_STILL_CAP\b") 

        ret = False

        if (len(msgString) == 0):
            print("zero length tag passed")
            return False
            
        if not (msgString.find("S_ISO") == -1):
        #if (re.search(patternISO, msgString.upper())==True): 
            if ((mavObj.setMavIsoModeData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_ACCEPTED, "S_ISO" )
            else:
                self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_FAILED, "S_ISO" )            
        elif not (msgString.find("S_APERTURE") == -1):
        #elif (re.search(patternAper, msgString.upper())==True): 
            if ((mavObj.setMavApertureData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_ACCEPTED, "S_APERTURE" )
            else:
                self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_FAILED, "S_APERTURE" )   
        elif not (msgString.find("S_EX_PRO_MODE") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            if ((mavObj.setMavExProData( dataRcv )) == True):
                self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_ACCEPTED, "S_EX_PRO_MODE" )
            else:
                self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_FAILED, "S_EX_PRO_MODE" )                        
        elif not (msgString.find("S_FOCUS_AREA") == -1):
        #elif (re.search(patternFocA, msgString.upper())==True):    
            if ((mavObj.setMavFocusAreaData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_ACCEPTED, "S_FOCUS_AREA" )
            else:
                self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_FAILED, "S_FOCUS_AREA" )              
        elif not (msgString.find("S_FOCUS_MODE") == -1):
        #elif (re.search(patternFocus, msgString.upper())==True):
            if ((mavObj.setMavFocusData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_ACCEPTED, "S_FOCUS_MODE" )
            else:
                self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_FAILED, "S_FOCUS_MODE" )                 
        elif not (msgString.find("S_SHUT_SPD") == -1):
        #elif (re.search(patternShSp, msgString.upper())==True):   
            if ((mavObj.setMavShutterData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_ACCEPTED, "S_SHUT_SPD" )
            else:
                self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_FAILED, "S_SHUT_SPD" )                           
        elif not (msgString.find("S_WHITE_BAL") == -1):
        #elif (re.search(patternWhiBal, msgString.upper())==True):  
            if ((mavObj.setMavWhiteBalData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_ACCEPTED, "S_WHITE_BAL" )
            else:
                self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_FAILED, "S_WHITE_BAL" )          
        elif not (msgString.find("S_STILL_CAP") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):    
            if ((mavObj.setMavStillCapModeData( dataRcv )) == True):
                    ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_ACCEPTED, "S_STILL_CAP" )
            else:
                self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavutil.mavlink.PARAM_ACK_FAILED, "S_STILL_CAP" )                  
        else:
            print("unsupported variable name %s to val=%d :: NOT SET "%(msgString,dataRcv))
            return False

        return ret
                
    def readParamExtSetFromMavLink( self, msgString, mavObj, the_connection ):

        # must be EXACT tag match
        #patternISO = re.compile(r"\bS_ISO\b")
        #patternAper = re.compile(r"\bS_APERTURE\b")
        #patternExPro = re.compile(r"\bS_EX_PRO_MODE\b")
        #patternFocus = re.compile(r"\bS_FOCUS_MODE\b")
        #patternFocA = re.compile(r"\bS_FOCUS_AREA\b")
        #patternShSp = re.compile(r"\bS_SHUT_SPD\b")  
        #patternWhiBal = re.compile(r"S_WHITE_BAL") 
        #patternStCa = re.compile(r"\bS_STILL_CAP\b") 

        v = 0
        p = 0
        r = False

        if (len(msgString) == 0):
            print("zero length tag passed")
            return False
            
        if not (msgString.find("S_ISO") == -1):
        #if (re.search(patternISO, msgString.upper())==True): 
            v, p, r = mavObj.getMavIsoModeData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_iso( the_connection, v ) == True ):
                    mavObj.mav_ext_req_all_param |= mavObj.ParamIso                                     # >>> set the bit to enable full read of parameter
                    return r
            return False            
        elif not (msgString.find("S_APERTURE") == -1):
        #elif (re.search(patternAper, msgString.upper())==True): 
            v, p, r = mavObj.getMavApertureData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_aper( the_connection, v ) == True ):
                    mavObj.mav_ext_req_all_param |= mavObj.ParamAperture                                # >>> set the bit to enable full read of parameter                
                    return r
            return False                 
        elif not (msgString.find("S_EX_PRO_MODE") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            v, p, r = mavObj.getMavExProData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_expro( the_connection, v ) == True ):
                    mavObj.mav_ext_req_all_param |= mavObj.ParamExPro                                   # >>> set the bit to enable full read of parameter
                    return r
            return False                  
        elif not (msgString.find("S_FOCUS_AREA") == -1):
        #elif (re.search(patternFocA, msgString.upper())==True): 
            v, p, r = mavObj.getMavFocusAreaData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_focus_area( the_connection, v ) == True ):
                    mavObj.mav_ext_req_all_param |= mavObj.ParamFocusArea                               # >>> set the bit to enable full read of parameter                  
                    return r
            return False                 
        elif not (msgString.find("S_FOCUS_MODE") == -1):
        #elif (re.search(patternFocus, msgString.upper())==True):
            v, p, r = mavObj.getMavFocusData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_focus( the_connection, v ) == True ):
                    mavObj.mav_ext_req_all_param |= mavObj.ParamFocus                                   # >>> set the bit to enable full read of parameter 
                    return r
            return False                  
        elif not (msgString.find("S_SHUT_SPD") == -1):
        #elif (re.search(patternShSp, msgString.upper())==True): 
            v, p, r = mavObj.getMavShutterData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_shut_spd( the_connection, v ) == True ): 
                    mavObj.mav_ext_req_all_param |= mavObj.ParamShutSpd                                 # >>> set the bit to enable full read of parameter                 
                    return r
            return False                     
        elif not (msgString.find("S_WHITE_BAL") == -1):
        #elif (re.search(patternWhiBal, msgString.upper())==True):  
            v, p, r = mavObj.getMavWhiteBalData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_white_bal( the_connection, v ) == True ): 
                   mavObj.mav_ext_req_all_param |= mavObj.ParamWhiteBala                               # >>> set the bit to enable full read of parameter                  
                   return r
            return False 
        elif not (msgString.find("S_STILL_CAP") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavStillCapModeData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_still_cap( the_connection, v ) == True ):  
                   mavObj.mav_ext_req_all_param |= mavObj.ParamStillCap                                # >>> set the bit to enable full read of parameter                  
                   return r
            return False                 
        else:
            print("unsupported variable name %s to val=%d :: NOT SET "%(msgString,dataRcv))
            return False
            
    # process the incoming messages received
    #
    def process_messages_from_connection(self, the_connection, sharedObj):
        #"""
        #This runs continuously. The mavutil.recv_match() function will call mavutil.post_message()
        #any time a new message is received, and will notify all functions in the master.message_hooks list.
        #"""
        loop = 5
        while loop >= 1:
        #while True:
            print("im receiving.............")
            #time.sleep(0.05)
            #self.update_uptime_label( )
            #self.update_utc_label( )
            #
            # wait heartbeat (only the GCS does this )
            # m = the_connection.recv_match(type="HEARTBEAT", blocking=True, timeout=5)
            #
            # you can also use type lists like this 
            # type=['COMMAND_LONG,RC_CHANNELS']
            #
            #msg = the_connection.recv_match(blocking=True, timeout=5)
            msg = the_connection.recv_match(blocking=True, timeout=1)
            if (msg is None):                                                                       # timeout with nothing just return 
                return
            if ( the_connection.target_system == msg.get_srcSystem() ):                             # check this and eliminate spurious messages if needed
                print(f"data read {msg.get_type()}")
                print(f"connection {the_connection.target_system} == {msg.get_srcSystem()}")
            last_timestamp = msg._timestamp
            #
            # These are test messages to check the receive end !!!!
            #
            #self.mavlink_send_camera_feedback( the_connection )
            #self.mavlink_send_camera_information(the_connection)
            #self.mavlink_send_storage_information(the_connection)
            #self.mavlink_send_camera_capture_status(the_connection)
            #print(f" video stream returned {self.mavlink_send_video_stream_information(the_connection)}")
            #self.mavlink_send_camera_image_captured(the_connection)
            #the_connection.mav.camera_feedback_send( 1000, 1, 1, 22, 21, 10, 30, 21, 2, 3, 5, 2, 3)
            #the_connection.mav.gps_raw_int_send( 1000, self.g_count, 77, 66, 76, 3, 1, 2, 3, 5)
            the_connection.mav.vibration_send( 1000, 1, 1, 22, 21, 10, 30 )
            #self.mavlink_send_param_value(the_connection)
            #print("FTP request for XML file .... I'm sending it as my payload")
            #try:
            #    f = open(self.CAM_XML_FILE,'r')
            #    #payload = f.read() not raw read but as bytes below
            #    lab = np.fromfile(f, dtype=np.uint8)
            #    f.close()
            #except Exception as e:
            #     print(f" XML file read exception {e}") 
            #self.mavlink_do_ftp_send( the_connection, self.NETWORK_ID, lab)
            self.g_count = self.g_count + 1
            if not msg:
                print("\033[31m no msg ! \033[0m")
                return
            if msg.get_type() == "BAD_DATA":
                self.ACK_ERROR = self.GOT_BAD
                self.errRCV_COMMAND = 0
                self.errRPM2 = 0
                if mavutil.all_printable(msg.data):
                    sys.stdout.write(msg.data)
                    sys.stdout.flush()
            elif msg.get_type() == 'PARAM_REQUEST_LIST':
                # this is a dummy message to reply immediately for now
                #
                # out for now update sent right away self.mavlink_send_param_value(the_connection)
                #
                sharedObj.mav_req_all_param = mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM
                print("\033[35m PARAM_REQUEST_LIST was sent - shared object set to %d" % (sharedObj.mav_req_all_param))
                # ===== TRAP ======
                #exit(99)
            elif msg.get_type() == 'PARAM_EXT_REQUEST_LIST':
                #
                #
                sharedObj.mav_ext_req_all_param = mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM
                print("\033[35m PARAM_EXT_REQUEST_LIST was sent - shared object set to %d" % (sharedObj.mav_ext_req_all_param))  
                # ===== TRAP ======
                #exit(99)                
            elif msg.get_type() == 'PARAM_SET':
                #
                # for testing...... self.mavlink_send_ext_param_value(the_connection)
                #
                #
                # value is sent as a float but its an integer, so unpack the float read as an integer
                # ref:- https://gist.github.com/AlexEshoo/d3edc53129ed010b0a5b693b88c7e0b5
                #
                m = struct.unpack('I', struct.pack('f', msg.param_value))[0]
                ee = self.mav_param_type_conv( msg.param_type, msg.param_value )
                print(f"\033[36m Values mavlink :: {m} from func {ee}")
                if ( self.writeParamSetFromMavLink( msg.param_id, sharedObj, ee, the_connection ) == True ):
                    print(f"\033[33m PARAM_SET was sent for {msg.param_id} val {ee} type {msg.param_type} really sent {m} \033[0m" )
                else:
                    print("\033[31m PARAM_SET write fail for %s :: %d type %d \033[0m"%( msg.param_id, ee, msg.param_type ))
                # ===== TRAP =====
                #exit(97)
            elif msg.get_type() == 'PARAM_REQUEST_READ':
                #
                if ( self.readParamSetFromMavLink( msg.param_id, sharedObj, the_connection )==True):
                    print(f"\033[34m Success reading param {msg.param_id} \033[0m")
                else:
                    print(f"\033[31;46m Error reading param {msg.param_id} \033[0m")
                # ===== TRAP =====
                #exit(96)
            elif msg.get_type() == 'PARAM_EXT_REQUEST_READ':
                #
                if ( self.readParamExtSetFromMavLink( msg.param_id, sharedObj, the_connection )==True):
                    print(f"\033[32m Sucess reading EXT Param {msg.param_id} \033[0m")
                else:
                    print(f"\033[31;43m Error sending param {msg.param_id} \033[0m")                
                # ===== TRAP =====
                exit(96)
            elif msg.get_type() == 'PARAM_EXT_SET':
                #
                # self.mavlink_send_param_value(the_connection)
                #
                if ( self.writeParamExtSetFromMavLink( msg.param_id, sharedObj, int(msg.param_value) ) == True ):
                    print("\033[35m PARAM_EXT_SET was sent for %s :: %d \033[0m"%( msg.param_id, int(msg.param_value) ))
                    ## =======> send_ext_ack
                else:
                    print("\033[31m PARAM_EXT_SET write fail for %s :: %s"%( msg.param_id, msg.param_value))
                # ===== TRAP =====
                exit(95)
            elif msg.get_type() == 'RC_CHANNELS':
                print("RC Channel message (system %u component %u)\n" % (the_connection.target_system, the_connection.target_component))
            elif msg.get_type() == 'COMMAND_LONG':
                print("!!!!!! Long message received (system %u component %u)\n" % (the_connection.target_system, the_connection.target_component))
                print("in cmd long ... ACK RES %s %u \n" % (self.ACK_RESULT,mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_INFORMATION))
                print("Command %u p1 %u p2 %u p3 %u p4 %u \n" % (msg.command, msg.param1, msg.param2, msg.param3, msg.param4))
                print("p5 %u p6 %u p7 %u \n" % (msg.param5, msg.param6, msg.param7))  

                # print(msg.get_payload())
                # print(msg.get_msgbuf())
                # print(msg.get_fieldnames())
                # print(msg.get_type())
                #
                # print the message recieved in json
                #
                print(msg.to_dict())

                if not (self.ACK_RESULT == mavutil.mavlink.MAV_RESULT_ACCEPTED):
                    self.RCV_COMMAND = int(msg.command)
                    print(f"\033[35m IN LOOP :: self ACK RES {self.ACK_RESULT} RCV {self.RCV_COMMAND} == {mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE}")
 
                    if (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE):
                        self.RPM2 = int(msg.param1) 
                        print(f"Is it here {self.RPM2} == {self.CAMERA_INFORMATION}")
                        if (self.RPM2 == self.CAMERA_INFORMATION):                       #camera_information
                            self.type_of_msg = 6500
                            print("\033[34m >>>>>> camera information \033[36m >>>>>>>>>>>>>>>>>>>>>>")
                            self.mavlink_send_camera_information(the_connection)
                        elif (self.RPM2 == self.CAMERA_SETTINGS):                        #camera_settings
                            self.type_of_msg = 6501                        
                        elif (self.RPM2 == self.STORAGE_INFORMATION):                    #storage information
                            self.type_of_msg = 6502
                        elif (self.RPM2 == self.CAMERA_CAPTURE_STATUS):                  #camera capture status
                            self.type_of_msg = 6503  
                        elif (self.RPM2 == mavutil.mavlink.MAVLINK_MSG_ID_CAMERA_IMAGE_CAPTURED):   #retrieve lost images
                            self.type_of_msg = 6504   
                            self.Got_Param1 = int(msg.param2)
                        elif (self.RPM2 == 269):                                                    #video stream
                            self.type_of_msg = 6505                             
                        else:
                            self.type_of_msg = 0
                            print(f"camera info received {self.RPM2}")
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_INFORMATION):
                        print("request camera Info OLD MESSAGE.....")
                        #
                        # Send camera information
                        #
                        self.mavlink_send_camera_information(the_connection)
                        if (msg.param1 == 1):
                            self.type_of_msg = mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_INFORMATION
                            print("=========== !! send to QGround Camera Information !! ==========")
                            self.mavlink_send_camera_information(the_connection)
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_REQUEST_VIDEO_STREAM_INFORMATION):
                        print("request video stream Info OLD MESSAGE.....")
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_REQUEST_VIDEO_STREAM_INFORMATION
                        print("=========== !! send to QGround VideoStream !! ==========")
                        self.mavlink_send_video_stream_information(the_connection)
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_SETTINGS):
                        print("request camera settings Info OLD MESSAGE.....")
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_SETTINGS
                        print("\033[35m =========== !! send to QGround Camera settings !! ========== \033[0m")
                        self.mavlink_send_camera_settings(the_connection)
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS):
                        print("request camera capture status Info OLD MESSAGE.....")
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS
                        print("\033[36m =========== !! send to QGround Camera capture status !! ========== \033[0m")
                        self.mavlink_send_camera_capture_status(the_connection)
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_REQUEST_STORAGE_INFORMATION):
                        print("request storage info Info OLD MESSAGE.....")
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_REQUEST_STORAGE_INFORMATION
                        print("\033[34m =========== !! send to QGround Camera storage_info !! ========== \033[0m")
                        self.mavlink_send_storage_information(the_connection)
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_SET_RELAY):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_SET_RELAY
                        print(f"\033 [31m >>>>> Got a message to set the RelayNo {msg.param1} to state {msg.param2}")
                        self.raspberry_pi3_set_relay(self, msg.param1, msg.param2)
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_VIDEO_START_CAPTURE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_VIDEO_START_CAPTURE
                        self.Got_Param1 = msg.param1 
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_VIDEO_STOP_CAPTURE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_VIDEO_START_CAPTURE
                        self.Got_Param1 = msg.param1                           
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_IMAGE_START_CAPTURE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_IMAGE_START_CAPTURE
                        self.Got_Param1 = msg.param2
                        self.Got_Param2 = msg.param3
                        self.Got_Param3 = msg.param4
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_IMAGE_STOP_CAPTURE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_IMAGE_STOP_CAPTURE
                        self.Got_Param1 = msg.param3
                        self.Got_Param2 = msg.param4
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_VIDEO_START_STREAMING):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_VIDEO_START_STREAMING
                        self.Got_Param1 = msg.param1
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_VIDEO_STOP_STREAMING):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_VIDEO_STOP_STREAMING
                        self.Got_Param1 = msg.param1
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_SET_CAMERA_MODE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_SET_CAMERA_MODE
                        self.Got_Param1 = msg.param2
                    elif (self.RCV_COMMAND == mavdefs.MAV_CMD_SET_CAMERA_ZOOM):
                        self.type_of_msg = mavdefs.MAV_CMD_SET_CAMERA_ZOOM
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        self.Got_Param3 = msg.param3
                    elif (self.RCV_COMMAND == mavdefs.MAV_CMD_SET_CAMERA_FOCUS):
                        self.type_of_msg = mavdefs.MAV_CMD_SET_CAMERA_FOCUS
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONFIGURE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONFIGURE
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        self.Got_Param3 = msg.param3
                        self.Got_Param4 = msg.param4
                        self.Got_Param5 = msg.param5
                        self.Got_Param6 = msg.param6
                        self.Got_Param7 = msg.param7
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL):
                        #
                        # Taking a picture is hard coded to here as it needs no delay
                        #
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL
                        print(f"\033[33m DO DIGICAM CONTROL {msg.param5} {msg.param7}")
                        if ((int(msg.param5) == 1) and (int(msg.param7) == 0)):
                            fastGlobals.take_picture = 1 
                            print("set it to 1")
                            #time.sleep(10)
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        self.Got_Param3 = msg.param3
                        self.Got_Param4 = msg.param4
                        self.Got_Param5 = msg.param5
                        self.Got_Param6 = msg.param6
                        self.Got_Param7 = msg.param7
                        print(f"\033[36m DO DIGICAM CONTROL COMPLETED \033[0m {msg.param5} {msg.param7} ")
                        #time.sleep(10)
                        #exit(100)
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_CONTROL_VIDEO):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_CONTROL_VIDEO
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        self.Got_Param3 = msg.param3
                        self.Got_Param4 = msg.param4
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_SET_CAM_TRIGG_INTERVAL):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_SET_CAM_TRIGG_INTERVAL
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_RESET_CAMERA_SETTINGS):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_RESET_CAMERA_SETTINGS
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL_QUAT):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL_QUAT
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        self.Got_Param3 = msg.param3
                        self.Got_Param4 = msg.param4
                    #elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW):
                    #   self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW
                    #   self.Got_Param1 = msg.param1
                    #   self.Got_Param2 = msg.param2
                    #   self.Got_Param3 = msg.param3
                    #   self.Got_Param4 = msg.param4
                    #   self.Got_Param5 = msg.param5
                    #   self.Got_Param6 = msg.param6
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_TRIGGER_CONTROL):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_TRIGGER_CONTROL
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        self.Got_Param3 = msg.param3
                    elif (self.RCV_COMMAND == 2004):             # MAV_CMD_CAMERA_TRACK_POINT=2004
                        self.type_of_msg = 2004;
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        self.Got_Param3 = msg.param3
                    elif (self.RCV_COMMAND == 2005):             # MAV_CMD_CAMERA_TRACK_RECTANGLE=2005
                        self.type_of_msg = 2005;
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        self.Got_Param3 = msg.param3
                    elif (self.RCV_COMMAND == 2010):             # MAV_CMD_CAMERA_STOP_TRACKING=2010
                        self.type_of_msg = 2010;
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_STORAGE_FORMAT):           
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_STORAGE_FORMAT
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_SET_SERVO):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_SET_SERVO
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        print("\033[32m saw the relay command come in")
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_PREFLIGHT_STORAGE):
                        print(f"\033[33m Asks for storage params paramStorage={msg.param1}  missionStorage={msg.param2} \033[0m")
                    elif (self.RCV_COMMAND == 42428):
                        print(f"\033[37m Command 42428 was sent not sure what im meant to do..... \033[0m")	
                    else:
                        print(f"got this id {self.RCV_COMMAND} {msg.command}")
                        self.RPM2 = 0
                        self.type_of_msg = self.RCV_COMMAND
                    self.ACK_RESULT = mavutil.mavlink.MAV_RESULT_ACCEPTED
                    print("\033[36m >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ACK RES %d %d"%(self.ACK_RESULT,mavutil.mavlink.MAV_RESULT_ACCEPTED))
                    print("\033[31m")
                else:
                    self.ACK_ERROR = self.GOT_ERROR
                    self.errRCV_COMMAND = msg.command
                    self.errRPM2 = msg.param1
                    print(f"Error ACK message send for multiple request @ cmd :: {self.errRCV_COMMAND} rpm :: {self.errRPM2}")
                    
            elif msg.get_type() == 'CAMERA_IMAGE_CAPTURED':
                print("Cam Cap message received (system %u component %u)\n" % (the_connection.target_system, the_connection.target_component)) 
                print("lat %u lon %u alt %u\n" % (msg.lat, msg.lon, msg.alt)) 
                print("URL %u)\n" % (msg.file_url))                    
            elif msg.get_type() == 'GPS_RAW_INT':
                the_connection.mav.gps_raw_int_send( 1000, 1, 22, 21, 1, 3, 1, 2, 3, 5)
            elif msg.get_type() == 'CAMERA_FEEDBACK':
                print("Camera Feedback request was made")
                #the_connection.mav.camera_feedback_send( 1000, 1, 1, 22, 21, 10, 30, 21, 2, 3, 5, 2, 3)
            elif msg.get_type() == 'FILE_TRANSFER_PROTOCOL':
                print("FTP request for XML file .... I'm sending it as my payloads in chunks of 251 bytes")
                lab = []
                try:
                    f = open(self.CAM_XML_FILE,'r')
                    #payload = f.read() not raw read but as bytes below
                    lab = np.fromfile(f, dtype=np.uint8)
                    f.close()
                except Exception as e:
                    print(f" XML file read exception {e}") 
                self.mavlink_do_ftp_send( the_connection, self.NETWORK_ID, lab)
            elif msg.get_type() == 'REQUEST_DATA_STREAM':
                print("REQUEST DATA STREAM :: start %u id %u req_rte %u\n" % (msg.start_stop, msg.req_stream_id, msg.req_message_rate))
            elif msg.get_type() == 'STATUSTEXT':
                print("STATUSTEXT :: text %s " % (msg.text)) 
            elif msg.get_type() == 'HEARTBEAT':
                print("HEARTBEAT :: src %s type %s auto %s sys %s" % (msg.get_srcSystem(), msg.type,msg.autopilot,msg.system_status)) 
            else:
                print(f"unsupported command :: {msg.get_type()}")   
            #time.sleep(0.05)
            loop = loop - 1

    def mavlink_send_ack_command(self, the_connection, cmd, rpm2, pro, res):
        if (self.mavlink20(the_connection) == True):
            print(f"\033[31m sending an ACK {pro}")
            try:
                the_connection.mav.command_ack_send(
                    int(cmd),                                                # command
                    int(res),                                                # result
                    int(pro),                                                # progress
                    int(rpm2),                                               # result_param2
                    the_connection.target_system,                       # target_system
                    the_connection.target_component)                    # target_component
                print(f"ACK sent {rpm2} {res}")
                ret = True
            except Exception as err_msg:
                print("Failed 1st ACK message : %s" % (err_msg))
                try:
                    the_connection.mav.command_ack_send(
                         int(cmd),                                                # command
                         int(res))                                                # result
                    print(f"ACK sent {rpm2} {res}")
                    ret = True
                except Exception as err_msg:
                    print("Failed 2nd ACK message : %s" % (err_msg))
                    ret = False
            return ret
        elif (self.mavlink10(the_connection) == True):
            print(f"\033[31m sending an ACK {pro}")
            try:
                the_connection.mav.command_ack_send(
                    int(cmd),                                                # command
                    int(res))                                                # result
                print(f"ACK sent {rpm2} {res}")
                ret = True
            except Exception as err_msg:
                print("Failed 1st ACK message : %s" % (err_msg))
                try:
                    the_connection.mav.command_ack_send(
                        int(cmd),                                                # command
                        int(res),                                                # result
                        int(pro),                                                # progress
                        int(rpm2),                                               # result_param2
                        the_connection.target_system,                       # target_system
                        the_connection.target_component)                    # target_component
                    print(f"ACK sent {rpm2} {res}")
                    ret = True
                except Exception as err_msg:
                    print("Failed 2nd ACK message : %s" % (err_msg))
                    ret = False
            return ret

#
# ============================================================= multi-process threads =====================================================================
# 

        
def manageAlphaCameraExpro( mySonyCam, mav2SonyVals, expro, tm_upd_disable=False, time_delta = 1000 ):

    p = multiprocessing.current_process()
    print ('Starting Exposure Program :', p.name, p.pid)
    #
    # initialise general program control flags
    #
    success = False
    timenow = 0
    
    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    #        
    success = mySonyCam.setSonyCamExProData( expro, mav2SonyVals )

    #
    # Time enabled reading to poll on time_delta
    # when this data is written the mavlink task 
    # should send it to the GCS via mavlink messages
    #   
    if not (tm_upd_disable == True):    
        timenow = mySonyCam.my_timestamp()      
    #        
    if ((timenow - expro.timestamp) > time_delta):
        if (mySonyCam.getSonyCamExProData( expro )==True):
            expro.timestamp = timenow
        #print(f"\033[36m Time Delta occurred {timenow} {expro.timestamp}")
    #else:
        #print(f"\033[34m No time diff {timenow} {expro.timestamp}")
    print ('Exiting Exposure Program :', multiprocessing.current_process().name)
    
def sendMavExpro( mySonyCam, expro, ConnID ):
    p = multiprocessing.current_process()
    print ('Starting Exposure Program:', p.name, p.pid)
    success = mySonyCam.sendMavlinkMessageForParamObject( expro, ConnID )
    success = mySonyCam.sendMavlinkMessageForParamExtObject( expro, ConnID )
    print ('Exiting Exposure Program :', multiprocessing.current_process().name)             

def manageAlphaCameraAperture( mySonyCam, mav2SonyVals, aper, tm_upd_disable=False, time_delta = 1000 ):

    p = multiprocessing.current_process()
    print ('Starting Aperture :', p.name, p.pid)
    #
    # initialise general program control flags
    #
    success = False
    timenow = 0

    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    #            
    success = mySonyCam.setSonyCamApertureData( aper, mav2SonyVals )

    #
    # Time enabled reading to poll on time_delta
    # when this data is written the mavlink task 
    # should send it to the GCS via mavlink messages
    #   
    if not (tm_upd_disable == True):    
        timenow = mySonyCam.my_timestamp()  
    #        

    if ((timenow - aper.timestamp) > time_delta):
        if (mySonyCam.getSonyApertureData( aper )==True):
            aper.timestamp = timenow
    print ('Exiting  Aperture :', multiprocessing.current_process().name)
    
def sendMavAper( mySonyCam, aper, ConnID ):
    p = multiprocessing.current_process()
    print ('Starting Mavlink Aperture :', p.name, p.pid)
    success = mySonyCam.sendMavlinkMessageForParamObject( aper, ConnID )
    success = mySonyCam.sendMavlinkMessageForParamExtObject( aper, ConnID )
    print ('Exiting Mavlink Aperture :', multiprocessing.current_process().name)
    
def manageAlphaCameraFocusData( mySonyCam, mav2SonyVals, focusdata, focusarea, tm_upd_disable=False, time_delta = 1000 ):

    p = multiprocessing.current_process()
    print ('Starting Focus :', p.name, p.pid)
    #
    # initialise general program control flags
    #
    success = False
    timenow = 0

    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    #            
    success = mySonyCam.setSonyCamFocusData( focusdata, mav2SonyVals )
    success = mySonyCam.setSonyCamFocusAreaData( focusarea, mav2SonyVals ) 

    #
    # Time enabled reading to poll on time_delta
    # when this data is written the mavlink task 
    # should send it to the GCS via mavlink messages
    #   
    if not (tm_upd_disable == True):    
        timenow = mySonyCam.my_timestamp()   
    #        
    if ((timenow - focusdata.timestamp) > time_delta):
        if (mySonyCam.getSonyCamFocusData( focusdata )==True):
            focusdata.timestamp = timenow

    if ((timenow - focusarea.timestamp) > time_delta):
        if (mySonyCam.getSonyCamFocusAreaData( focusarea )==True):
            focusarea.timestamp = timenow
    print ('Exiting Focus :', multiprocessing.current_process().name)
    
def sendMavFocusData( mySonyCam, focusdata, focusarea, ConnID ):

    p = multiprocessing.current_process()
    print ('Starting Mavlink Focus Data :', p.name, p.pid)
    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    #     
    success = mySonyCam.sendMavlinkMessageForParamObject( focusdata, ConnID )
    success = mySonyCam.sendMavlinkMessageForParamObject( focusarea, ConnID )
    success = mySonyCam.sendMavlinkMessageForParamExtObject( focusdata, ConnID )
    success = mySonyCam.sendMavlinkMessageForParamExtObject( focusarea, ConnID )
    print ('Exiting Mavlink Focus Data  :', multiprocessing.current_process().name)

def manageAlphaCameraIso( mySonyCam, mav2SonyVals, iso, retries=3, tm_upd_disable=False, time_delta = 1000 ):

    p = multiprocessing.current_process()
    print ('Starting ISO set :', p.name, p.pid)
    #
    # initialise general program control flags
    #
    success = False
    timenow = 0

    print("\033[33m ================== ISO :: in manage function ======================== \033[0m")
    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    # 
    retry = 0
    while (retry < retries):    
        if (mySonyCam.setSonyCamISOData( iso, mav2SonyVals ) == True):
            print("\033[36m sony cam iso data success \033[0m")
            break
        else:
            print("\033[31m sony cam iso data write failure \033[0m")
            time.sleep(1)
            retry += 1
    else:
        print("\033[31;43m having probs !!! gonna reset it \033[0m")
        reset_usb_camlink()            

    #
    # Time enabled reading to poll on time_delta
    # when this data is written the mavlink task 
    # should send it to the GCS via mavlink messages
    #   
    if not (tm_upd_disable == True):    
        timenow = mySonyCam.my_timestamp()  
    #        
    if ((timenow - iso.timestamp) > time_delta):
        if (mySonyCam.getSonyCamISOData( iso )==True):
            print(f"\033[36;45m ISO timeupdate required @ {iso.timestamp} {timenow}")
            iso.timestamp = timenow
    print ('Exiting ISO Set :', multiprocessing.current_process().name)
    
def sendMavIso( mySonyCam, iso, ConnID ):

    #p = multiprocessing.current_process()
    #print ('Starting ISO :', p.name, p.pid)
    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    #     
    success = mySonyCam.sendMavlinkMessageForParamObject( iso, ConnID )
    success = mySonyCam.sendMavlinkMessageForParamExtObject( iso, ConnID )
    #print ('Exiting ISO :', multiprocessing.current_process().name)   
    
def manageAlphaCameraShutSpd( mySonyCam, mav2SonyVals, shut_sp, tm_upd_disable=False, time_delta = 1000 ):

    p = multiprocessing.current_process()
    print ('Starting Shutter Speed :', p.name, p.pid)
    
    #
    # initialise general program control flags
    #
    success = False
    timenow = 0

    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    #        
    success = mySonyCam.setSonyCamShutSpdData( shut_sp, mav2SonyVals )
    
    #
    # Time enabled reading to poll on time_delta
    # when this data is written the mavlink task 
    # should send it to the GCS via mavlink messages
    #   
    if not (tm_upd_disable == True):    
        timenow = mySonyCam.my_timestamp()  
    #        
    if ((timenow - shut_sp.timestamp) > time_delta):
        if (mySonyCam.getSonyCamShutSpdData( shut_sp )==True):
            shut_sp.timestamp = timenow            
    print ('Exiting Shutter Speed :', multiprocessing.current_process().name)
    
def sendMavShutSpd( mySonyCam, shut_sp, ConnID ):

    p = multiprocessing.current_process()
    print ('Starting Mavlink Shutter Speed :', p.name, p.pid)
    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    #     
    success = mySonyCam.sendMavlinkMessageForParamObject( shut_sp, ConnID )
    success = mySonyCam.sendMavlinkMessageForParamExtObject( shut_sp, ConnID )
    print ('Exiting Mavlink Shutter Speed :', multiprocessing.current_process().name)
    
def manageAlphaWhiteBala( mySonyCam, mav2SonyVals, whitebal, tm_upd_disable=False, time_delta = 1000 ):

    p = multiprocessing.current_process()
    print ('Starting White Balance :', p.name, p.pid)
    
    #
    # initialise general program control flags
    #
    success = False
    timenow = 0

    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    # 
    success = mySonyCam.setSonyCamWhiteBalaData( whitebal, mav2SonyVals )
    
    #
    # Time enabled reading to poll on time_delta
    # when this data is written the mavlink task 
    # should send it to the GCS via mavlink messages
    #   
    if not (tm_upd_disable == True):    
        timenow = mySonyCam.my_timestamp()  
    #                    
    if ((timenow - whitebal.timestamp) > time_delta):
        if (mySonyCam.getSonyCamWhiteBalaData( whitebal )==True):
            whitebal.timestamp = timenow 

    print ('Exiting White Balance :', multiprocessing.current_process().name)
    
def sendMavWhiteBala( mySonyCam, whitebal, ConnID ):
    p = multiprocessing.current_process()
    print ('Starting Mavlink White Balance :', p.name, p.pid)
    success = mySonyCam.sendMavlinkMessageForParamObject( whitebal, ConnID )  
    success = mySonyCam.sendMavlinkMessageForParamExtObject( whitebal, ConnID )     
    print ('Exiting Mavlink White Balance :', multiprocessing.current_process().name)    
    
def manageAlphaCameraStillCap( mySonyCam, mav2SonyVals, stillcap, tm_upd_disable=False, time_delta = 1000 ):

    #
    # initialise general program control flags
    #
    success = False
    timenow = 0

    # use this if you want ot make a daemon proc
    p = multiprocessing.current_process()
    print ('Starting Still Capture :', p.name, p.pid)
    #

    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    #                
    success = mySonyCam.setSonyCamStillCapModeData( stillcap, mav2SonyVals ) 
    
    #
    # Time enabled reading to poll on time_delta
    # when this data is written the mavlink task 
    # should send it to the GCS via mavlink messages
    #   
    if not (tm_upd_disable == True):    
        timenow = mySonyCam.my_timestamp()   
    #        
    if ((timenow - stillcap.timestamp) > time_delta):
        if (mySonyCam.getSonyCamStillCapModeData( stillcap )==True):
            stillcap.timestamp = timenow 

    print ('Exiting Still Capture :', multiprocessing.current_process().name)

   
def sendMavStillCap( mySonyCam, stillcap, ConnID ): 
    p = multiprocessing.current_process()
    print ('Starting Mavlink Still Capture :', p.name, p.pid)   
    success = mySonyCam.sendMavlinkMessageForParamObject( stillcap, ConnID )  
    success = mySonyCam.sendMavlinkMessageForParamExtObject( stillcap, ConnID )     
    print ('Exiting Mavlink Still Capture :', multiprocessing.current_process().name) #

def mavlinkReqGetParamStillCap(  mySonyCam, obj ):
    if (mySonyCam.getSonyCamStillCapModeData( obj )==True):
        obj.timestamp = mySonyCam.my_timestamp()
        return True
    else:
        return False
        
def mavlinkReqGetParamWhiteBala(  mySonyCam, obj ):
    if (mySonyCam.getSonyCamWhiteBalaData( obj )==True):
        obj.timestamp = mySonyCam.my_timestamp()
        return True
    else:
        return False
        
def mavlinkReqGetParamShutSpd(  mySonyCam, obj ):
    if (mySonyCam.getSonyCamShutSpdData( obj )==True):
        obj.timestamp = mySonyCam.my_timestamp()
        return True
    else:
        return False
        
def mavlinkReqGetParamIso(  mySonyCam, obj ):
    if (mySonyCam.getSonyCamISOData( obj )==True):
        obj.timestamp = mySonyCam.my_timestamp() 
        return True
    else:
        return False
        
def mavlinkReqGetParamFocus(  mySonyCam, obj ):
    if (mySonyCam.getSonyCamFocusData( obj )==True):
        obj.timestamp = mySonyCam.my_timestamp() 
        return True
    else:
        return False
        
def mavlinkReqGetParamFocusArea(  mySonyCam, obj ):
    if (mySonyCam.getSonyCamFocusAreaData( obj )==True):
        obj.timestamp = mySonyCam.my_timestamp() 
        return True
    else:
        return False
        
def mavlinkReqGetParamAperture(  mySonyCam, obj ):
    if (mySonyCam.getSonyApertureData( obj )==True):
        obj.timestamp = mySonyCam.my_timestamp() 
        return True
    else:
        return False
        
def mavlinkReqGetParamExPro(  mySonyCam, obj ):
    if (mySonyCam.getSonyCamExProData( obj )==True):
        obj.timestamp = mySonyCam.my_timestamp() 
        return True
    else:
        return False

def mavlinkTakePhoto( mySonyCam, flg ):
    mySonyCam.take_a_picture_now(flg)
    
    
def serviceParamRequestsOneAtATime( mySonyCam, mav2SonyVals, stcap, wb, ss, iso, pf, pfa, pa, expro ):

    p = multiprocessing.current_process()
    print ('Starting Service Mavlink incoming request packets :', p.name, p.pid)

    if not (mav2SonyVals.mav_req_all_param == 0):
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamStillCap)) == 0):   
            stcap.set_update_flag( True, memoryValue.STATE_MAV_WRITING )
            if (mavlinkReqGetParamStillCap(  mySonyCam, stcap ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamStillCap  
                # param_ack ?                
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamWhiteBala)) == 0):  
            wb.set_update_flag( True, memoryValue.STATE_MAV_WRITING )        
            if (mavlinkReqGetParamWhiteBala(  mySonyCam, wb ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamWhiteBala               
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamShutSpd)) == 0):   
            ss.set_update_flag( True, memoryValue.STATE_MAV_WRITING )  
            if (mavlinkReqGetParamShutSpd(  mySonyCam, ss ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamShutSpd             
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamIso)) == 0):  
            iso.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          
            if (mavlinkReqGetParamIso(  mySonyCam, iso ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamIso 
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamFocus)) == 0):   
            pf.set_update_flag( True, memoryValue.STATE_MAV_WRITING )   
            if (mavlinkReqGetParamFocus(  mySonyCam, pf ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamFocus 
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamFocusArea)) == 0): 
            pfa.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          
            if (mavlinkReqGetParamFocusArea(  mySonyCam, pfa ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamFocusArea 
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamAperture)) == 0): 
            pa.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          
            if (mavlinkReqGetParamAperture(  mySonyCam, pa ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamAperture 
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamExPro)) == 0):  
            expro.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamExPro(  mySonyCam, expro ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamExPro

    if not (mav2SonyVals.mav_ext_req_all_param == 0):
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamStillCap)) == 0): 
            stcap.set_ack_send( True, memoryValue.STATE_MAV_WRITING )        
            if ( mavlinkReqGetParamStillCap(  mySonyCam, stcap ) == True ):
                if ( stcap.set_ack_send( True, stcap.STATE_CAM_READING ) == True ):                                                      # additional PARAM_EXT_VALUE message requested
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamStillCap  
                    # param_ack ?                
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamWhiteBala)) == 0):   
            wb.set_ack_send( True, memoryValue.STATE_MAV_WRITING )  
            if ( mavlinkReqGetParamWhiteBala(  mySonyCam, wb ) == True ):
                if ( wb.set_ack_send( True, wb.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested            
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamWhiteBala               
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamShutSpd)) == 0):  
            ss.set_ack_send( True, memoryValue.STATE_MAV_WRITING )          
            if ( mavlinkReqGetParamShutSpd(  mySonyCam, ss ) == True ):
                if ( ss.set_ack_send( True, ss.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested                   
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamShutSpd             
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamIso)) == 0):   
            iso.set_ack_send( True, memoryValue.STATE_MAV_WRITING )         
            if ( mavlinkReqGetParamIso(  mySonyCam, iso ) == True ):
                if ( iso.set_ack_send( True, iso.STATE_CAM_READING ) == True ):                                                          # additional PARAM_EXT_VALUE message requested                  
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamIso 
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamFocus)) == 0):  
            pf.set_ack_send( True, memoryValue.STATE_MAV_WRITING )           
            if ( mavlinkReqGetParamFocus(  mySonyCam, pf ) == True ):
                if ( pf.set_ack_send( True, pf.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested                 
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamFocus 
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamFocusArea)) == 0):  
            pfa.set_ack_send( True, memoryValue.STATE_MAV_WRITING )          
            if ( mavlinkReqGetParamFocusArea(  mySonyCam, pfa ) == True ):
                if ( pfa.set_ack_send( True, pfa.STATE_CAM_READING ) == True ):                                                          # additional PARAM_EXT_VALUE message requested                 
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamFocusArea 
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamAperture)) == 0):   
            pa.set_ack_send( True, memoryValue.STATE_MAV_WRITING ) 
            if ( mavlinkReqGetParamAperture(  mySonyCam, pa ) == True ):
                if ( pa.set_ack_send( True, pa.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested              
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamAperture 
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamExPro)) == 0): 
            expro.set_ack_send( True, memoryValue.STATE_MAV_WRITING )         
            if ( mavlinkReqGetParamExPro(  mySonyCam, expro ) == True ):
                if ( expro.set_ack_send( True, expro.STATE_CAM_READING ) == True ):                                                      # additional PARAM_EXT_VALUE message requested               
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamExPro

    print ('Exiting Service Mavlink incoming packet requests :', multiprocessing.current_process().name) #

def serviceParamRequests( mySonyCam, mav2SonyVals, stcap, wb, ss, iso, pf, pfa, pa, expro ):

    p = multiprocessing.current_process()
    print ('Starting Service Mavlink incoming request packets :', p.name, p.pid)

    if not (mav2SonyVals.mav_req_all_param == 0):
    
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamStillCap)) == 0):   
            stcap.set_update_flag( True, memoryValue.STATE_MAV_WRITING )
                
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamWhiteBala)) == 0):  
            wb.set_update_flag( True, memoryValue.STATE_MAV_WRITING )        
             
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamShutSpd)) == 0):   
            ss.set_update_flag( True, memoryValue.STATE_MAV_WRITING )  
         
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamIso)) == 0):  
            iso.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          

        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamFocus)) == 0):   
            pf.set_update_flag( True, memoryValue.STATE_MAV_WRITING )   

        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamFocusArea)) == 0): 
            pfa.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          

        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamAperture)) == 0): 
            pa.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          

        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamExPro)) == 0):  
            expro.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           

    if not (mav2SonyVals.mav_ext_req_all_param == 0):
    
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamStillCap)) == 0): 
            stcap.set_ack_send( True, memoryValue.STATE_MAV_WRITING )        
               
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamWhiteBala)) == 0):   
            wb.set_ack_send( True, memoryValue.STATE_MAV_WRITING )  
              
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamShutSpd)) == 0):  
            ss.set_ack_send( True, memoryValue.STATE_MAV_WRITING )          
          
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamIso)) == 0):   
            iso.set_ack_send( True, memoryValue.STATE_MAV_WRITING )         

        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamFocus)) == 0):  
            pf.set_ack_send( True, memoryValue.STATE_MAV_WRITING )           

        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamFocusArea)) == 0):  
            pfa.set_ack_send( True, memoryValue.STATE_MAV_WRITING )          

        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamAperture)) == 0):   
            pa.set_ack_send( True, memoryValue.STATE_MAV_WRITING ) 

        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamExPro)) == 0): 
            expro.set_ack_send( True, memoryValue.STATE_MAV_WRITING )  
    
    if not (mav2SonyVals.mav_req_all_param == 0):
    
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamStillCap)) == 0): 
            if (mavlinkReqGetParamStillCap(  mySonyCam, stcap ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamStillCap 
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamWhiteBala)) == 0):  
            if (mavlinkReqGetParamWhiteBala(  mySonyCam, wb ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamWhiteBala  
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamShutSpd)) == 0):  
            if (mavlinkReqGetParamShutSpd(  mySonyCam, ss ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamShutSpd    
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamIso)) == 0):  
            if (mavlinkReqGetParamIso(  mySonyCam, iso ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamIso 
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamFocus)) == 0):   
            if (mavlinkReqGetParamFocus(  mySonyCam, pf ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamFocus 
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamFocusArea)) == 0): 
            if (mavlinkReqGetParamFocusArea(  mySonyCam, pfa ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamFocusArea 
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamAperture)) == 0): 
            if (mavlinkReqGetParamAperture(  mySonyCam, pa ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamAperture 
        if not ((int(mav2SonyVals.mav_req_all_param) & int(mav2SonyVals.ParamExPro)) == 0):  
            if (mavlinkReqGetParamExPro(  mySonyCam, expro ) == True):
                mav2SonyVals.mav_req_all_param = mav2SonyVals.mav_req_all_param & ~mav2SonyVals.ParamExPro       

    if not (mav2SonyVals.mav_ext_req_all_param == 0):
    
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamStillCap)) == 0): 
            if ( mavlinkReqGetParamStillCap(  mySonyCam, stcap ) == True ):
                if ( stcap.set_ack_send( True, stcap.STATE_CAM_READING ) == True ):                                                      # additional PARAM_EXT_VALUE message requested
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamStillCap          

        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamWhiteBala)) == 0): 
            if ( mavlinkReqGetParamWhiteBala(  mySonyCam, wb ) == True ):
                if ( wb.set_ack_send( True, wb.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested            
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamWhiteBala 
                    
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamShutSpd)) == 0):  
            if ( mavlinkReqGetParamShutSpd(  mySonyCam, ss ) == True ):
                if ( ss.set_ack_send( True, ss.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested                   
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamShutSpd   

        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamIso)) == 0):   
            if ( mavlinkReqGetParamIso(  mySonyCam, iso ) == True ):
                if ( iso.set_ack_send( True, iso.STATE_CAM_READING ) == True ):                                                          # additional PARAM_EXT_VALUE message requested                  
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamIso 

        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamFocus)) == 0):  
            if ( mavlinkReqGetParamFocus(  mySonyCam, pf ) == True ):
                if ( pf.set_ack_send( True, pf.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested                 
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamFocus 

        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamFocusArea)) == 0):  
            if ( mavlinkReqGetParamFocusArea(  mySonyCam, pfa ) == True ):
                if ( pfa.set_ack_send( True, pfa.STATE_CAM_READING ) == True ):                                                          # additional PARAM_EXT_VALUE message requested                 
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamFocusArea 

        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamAperture)) == 0):   
            if ( mavlinkReqGetParamAperture(  mySonyCam, pa ) == True ):
                if ( pa.set_ack_send( True, pa.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested              
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamAperture 
                    
        if not ((int(mav2SonyVals.mav_ext_req_all_param) & int(mav2SonyVals.ParamExPro)) == 0): 
            if ( mavlinkReqGetParamExPro(  mySonyCam, expro ) == True ):
                if ( expro.set_ack_send( True, expro.STATE_CAM_READING ) == True ):                                                      # additional PARAM_EXT_VALUE message requested               
                    mav2SonyVals.mav_ext_req_all_param = mav2SonyVals.mav_ext_req_all_param & ~mav2SonyVals.ParamExPro

    print ('Exiting Service Mavlink incoming packet requests :', multiprocessing.current_process().name) #
    
def run_process_messages_from_connection(fra, the_connect, sharedObj):
    #p = multiprocessing.current_process()
    #print ('Starting: MavReader ', p.name, p.pid) 
    fra.process_messages_from_connection( the_connect, sharedObj )
    #print ('Exiting MavReader :', multiprocessing.current_process().name)

# ================ error handler if the camera fails (powers link on off) ============

# uses https://github.com/mvp/uhubctl
#
def reset_usb_camlink():
    print("\033[31;43m executing reset usb camera link \033[0m")
    p = os.popen('sudo /home/pi/cams/SonyTEST32/uhubctl/uhubctl -l 1-1 -a 0')
    print(p.read())
    time.sleep(2)
    p = os.popen('sudo /home/pi/cams/SonyTEST32/uhubctl/uhubctl -l 1-1 -a 1')
    print(p.read())
    time.sleep(2)
    print("\033[31m completed reset usb camera link \033[0m")

#
# The heartbeat task
#
def sendMavlinkHeartBeat(fm, cID, sleepTm=1):
    fm.mavlink_send_GCS_heartbeat(cID)
    while sleepTm > 0:
        time.sleep(1)
        print(f'{sleepTm} seconds')
        sleepTm -= 1

def sendMavlinkAckData(fm, cID, sleep, cmd, rpm2, pro, res):
    fm.mavlink_send_ack_command(cID, cmd, rpm2, pro, res)
    while sleep > 0:
        #await asyncio.sleep(1)
        print(f'{sleep} seconds')
        sleep -= 1
        
#
# ================ signal handlers ==============================
#

#
# from a signal.alarm
#
def raised_signal_handler(a,b):
    print("\033[32m ============ Take Picture ==================")
    fastGlobals.take_picture = 1
    # do the action here   

#
# CTL-C
#
def ctlc_handler(signum, frame): 
    print("Signal Number:", signum, " Frame: ", frame) 

#
# CTL-Z
#   
def exit_handler(signum, frame): 
    print('Exiting....') 
    exit(0)

#
# on getting kill -SIGUSR1 
#
def sigusr1_handler(signum, frame):
    print("signal hander with a kill -SIGUSR1 (signal.SIGUSR1)")
    # what we want to do on that external signal
    print("\033[32m ============ Take Picture ==================")
    fastGlobals.take_picture = 1
    
if __name__ == '__main__':

    # Register the alarm signal with our handler signal. signal(signal. SIGALRM, alarm_handler)
    signal.signal(signal.SIGALRM, raised_signal_handler)
    # to raise this insert this anywhere in code
    # signal.alarm(1)

    # Register our signal handler with `SIGINT`(CTRL + C) 
    signal.signal(signal.SIGINT, ctlc_handler) 
    # Register the exit handler with `SIGTSTP` (Ctrl + Z) 
    signal.signal(signal.SIGTSTP, exit_handler)
    # external signal handler
    signal.signal(signal.SIGUSR1, sigusr1_handler)
    
    frame = MAVFrame()
    state = False
    while (state == False):
        try:
            cID,state = frame.makeMAVlinkConn()
        except Exception as e:
            print("Error Trap :: ", e.__class__, " occurred.")

    # wait heartbeat 
    # if it sends another sys id we need to change it
    #
    state = False
    xx = 1
    while xx == 1:
        m = cID.recv_match(type="HEARTBEAT", blocking=True, timeout=5)
        if not (m == None):
            if not ( m.autopilot == mavutil.mavlink.MAV_AUTOPILOT_INVALID ):
                xx = 2
    id = m.get_srcSystem() 
    if not ( m.get_srcSystem() == frame.DEFAULT_SYS_ID ) :
        print(f"-------- new id found -------- {id}")
        while (state == False):
            try:
                cID,state = frame.makeNewMAVlinkConn(id)
            except Exception as e:
                print("Error Trap :: ", e.__class__, " occurred.")
                
    # default logger
    #
    # multiprocessing.log_to_stderr(logging.DEBUG)
    #
    # for extra logging use this 
    # instead
    #
    # multiprocessing.log_to_stderr()
    # logger = multiprocessing.get_logger()
    # logger.setLevel(logging.INFO)
    
    #
    # create instance of sony alpha cam (new API)
    #        
    mySonyCamNo1 = sonyAlphaNewCamera()
    
    #
    # create an instance of common write structure  
    # from mavlink reader task to the camera
    #
    gcsWrites2Sony = mavlinkSonyCamWriteVals()

    #
    # init the objects with camera data 
    # & set rhw data to be written back to gcs via mavlink
    #
    #
    # Initialise all shared object data between
    # camera and mavlink processes
    #        
    expro = mySonyCamNo1.initSonyCamExProData(  )
    aper = mySonyCamNo1.initSonyApertureData(  ) 
    focusdata = mySonyCamNo1.initSonyCamFocusData(  )       
    focusarea = mySonyCamNo1.initSonyCamFocusAreaData(  )  
    iso = mySonyCamNo1.initSonyCamISOData(  )      
    shut_sp = mySonyCamNo1.initSonyCamShutSpdData(  )   
    whitebal = mySonyCamNo1.initSonyCamWhiteBalaData(  )   
    stillcap = mySonyCamNo1.initSonyCamStillCapModeData(  )

    # this is a rough trap for now but if its all zeros its not getting correct data from the camera then try reset the link first
    # no need to aquire as this is working in single task mode at this point
    if ((((((((expro.signal == 0) and (aper.signal == 0)) and (focusdata.signal == 0)) and (focusarea.signal == 0)) and (iso.signal == 0)) and (shut_sp.signal == 0)) and (whitebal.signal == 0)) and (stillcap.signal == 0)):
        reset_usb_camlink()
        retCode = mySonyCamNo1.getSonyCamExProData( expro )
        retCode = mySonyCamNo1.getSonyApertureData( aper ) 
        retCode = mySonyCamNo1.getSonyCamFocusData( focusdata )       
        retCode = mySonyCamNo1.getSonyCamFocusAreaData( focusarea )  
        retCode = mySonyCamNo1.getSonyCamISOData( iso )      
        retCode = mySonyCamNo1.getSonyCamShutSpdData( shut_sp )   
        retCode = mySonyCamNo1.getSonyCamWhiteBalaData( whitebal )   
        retCode = mySonyCamNo1.getSonyCamStillCapModeData( stillcap )
        
    # uncomment these if you dont want immediate update message
    #    
    #expro.timestamp = mySonyCamNo1.my_timestamp()
    #aper.timestamp = mySonyCamNo1.my_timestamp()   
    #focusdata.timestamp = mySonyCamNo1.my_timestamp() 
    #focusarea.timestamp = mySonyCamNo1.my_timestamp() 
    #iso.timestamp = mySonyCamNo1.my_timestamp() 
    #shut_sp.timestamp = mySonyCamNo1.my_timestamp() 
    #whitebal.timestamp = mySonyCamNo1.my_timestamp()  
    #stillcap.timestamp = mySonyCamNo1.my_timestamp() 

    # ========== send back to GCS via mavlink if a new change of state has been detected or polled if requested 
    #        
    p2 = multiprocessing.Process(name='sendMavExpro', target=sendMavExpro, args=(mySonyCamNo1, expro, cID,)).start()
    p4 = multiprocessing.Process(name='sendMavAper', target=sendMavAper, args=(mySonyCamNo1, aper, cID,)).start()
    p6 = multiprocessing.Process(name='sendMavFocusData', target=sendMavFocusData, args=(mySonyCamNo1, focusdata, focusarea, cID, )).start()
    p8 = multiprocessing.Process(name='sendMavIso', target=sendMavIso, args=(mySonyCamNo1, iso, cID, )).start()
    p10 = multiprocessing.Process(name='sendMavShutSpd', target=sendMavShutSpd, args=(mySonyCamNo1, shut_sp, cID, )).start()
    p12 = multiprocessing.Process(name='sendMavWhiteBala', target=sendMavWhiteBala, args=(mySonyCamNo1, whitebal, cID, )).start()
    p14 = multiprocessing.Process(name='sendMavStillCap', target=sendMavStillCap, args=(mySonyCamNo1, stillcap, cID, )).start() 
    if p2 is not None:        
        p2.join()
    if p4 is not None:              
        p4.join()
    if p6 is not None:          
        p6.join()
    if p8 is not None:          
        p8.join()
    if p10 is not None:          
        p10.join()
    if p12 is not None:          
        p12.join()  
    if p14 is not None:          
        p14.join() 
            
    #
    # now set the class to be initialised
    #
    gcsWrites2Sony.init_class_state()

    #
    # test iso write
    #
    active = True
    while active==True:
        run_process_messages_from_connection(frame, cID, gcsWrites2Sony)
        sendMavlinkHeartBeat(frame, cID, 0)
        serviceParamRequests( mySonyCamNo1, gcsWrites2Sony, stillcap, whitebal, shut_sp, iso, focusdata, focusarea, aper, expro )
        #manageAlphaCameraIso(mySonyCamNo1, gcsWrites2Sony, iso)
        if not (gcsWrites2Sony.set_sony_iso == gcsWrites2Sony.STATE_INIT):
            print(f"on TOP LEVEL saw {gcsWrites2Sony.set_sony_iso} {gcsWrites2Sony.prev_sony_iso} {gcsWrites2Sony.mav_req_all_param}")
            manageAlphaCameraIso(mySonyCamNo1, gcsWrites2Sony, iso)
        if not (gcsWrites2Sony.set_sony_aperture == gcsWrites2Sony.STATE_INIT):
            print(f"on TOP LEVEL saw aperture {gcsWrites2Sony.set_sony_aperture} {gcsWrites2Sony.prev_sony_aperture} {gcsWrites2Sony.mav_req_all_param}")
            manageAlphaCameraAperture(mySonyCamNo1, gcsWrites2Sony, aper)
        if not (gcsWrites2Sony.set_sony_white_bal == gcsWrites2Sony.STATE_INIT):
            print(f"on TOP LEVEL saw wb {gcsWrites2Sony.set_sony_white_bal} {gcsWrites2Sony.prev_sony_white_bal} {gcsWrites2Sony.mav_req_all_param}")
            manageAlphaWhiteBala(mySonyCamNo1, gcsWrites2Sony, whitebal)
        if not (gcsWrites2Sony.set_sony_ex_pro == gcsWrites2Sony.STATE_INIT):
            print(f"on TOP LEVEL saw expro {gcsWrites2Sony.set_sony_ex_pro} {gcsWrites2Sony.prev_sony_ex_pro} {gcsWrites2Sony.mav_req_all_param}")
            manageAlphaCameraExpro(mySonyCamNo1, gcsWrites2Sony, expro)
        if not (gcsWrites2Sony.set_sony_still_cap_mode == gcsWrites2Sony.STATE_INIT):
            print(f"on TOP LEVEL saw still cap {gcsWrites2Sony.set_sony_still_cap_mode} {gcsWrites2Sony.prev_sony_still_cap_mode} {gcsWrites2Sony.mav_req_all_param}")
            manageAlphaCameraStillCap(mySonyCamNo1, gcsWrites2Sony, stillcap)  
        if not (gcsWrites2Sony.set_sony_shutter == gcsWrites2Sony.STATE_INIT):
            print(f"on TOP LEVEL saw shutter speed {gcsWrites2Sony.set_sony_shutter} {gcsWrites2Sony.prev_sony_shutter} {gcsWrites2Sony.mav_req_all_param}")
            manageAlphaCameraShutSpd(mySonyCamNo1, gcsWrites2Sony, shut_sp)  
        if not (gcsWrites2Sony.set_sony_focus == gcsWrites2Sony.STATE_INIT) or not (gcsWrites2Sony.set_sony_focus_area == gcsWrites2Sony.STATE_INIT):
            print(f"on TOP LEVEL saw shutter speed {gcsWrites2Sony.set_sony_focus} {gcsWrites2Sony.prev_sony_focus} {gcsWrites2Sony.set_sony_focus_area} {gcsWrites2Sony.prev_sony_focus_area} {gcsWrites2Sony.mav_req_all_param}")
            manageAlphaCameraFocusData(mySonyCamNo1, gcsWrites2Sony, focusdata, focusarea)             
        mavlinkTakePhoto( mySonyCamNo1, fastGlobals.take_picture )
        if (fastGlobals.take_picture == 2):
            sendMavlinkAckData(frame, cID, 1, frame.RCV_COMMAND, frame.RPM2, 0, frame.ACK_RESULT )
            fastGlobals.take_picture = 0
            frame.RCV_COMMAND = 0
            frame.ACK_RESULT = 99
            #exit(220)
        sendMavIso(mySonyCamNo1, iso, cID )
        sendMavAper( mySonyCamNo1, aper, cID )
        sendMavFocusData( mySonyCamNo1, focusdata, focusarea, cID )
        sendMavExpro( mySonyCamNo1, expro, cID )
        sendMavShutSpd( mySonyCamNo1, shut_sp, cID )
        sendMavWhiteBala( mySonyCamNo1, whitebal, cID )
        sendMavStillCap( mySonyCamNo1, stillcap, cID )  
        if (mySonyCamNo1.error_counts >= 5):  
            reset_usb_camlink()
            mySonyCamNo1.error_counts = 0            
        #active = False        
        #exit(10)
    
    #
    # run the process managing the camera as daemons
    #
    a = True
    p0 = multiprocessing.Process(name='run_process_mavlink', target=run_process_messages_from_connection, args=(frame, cID, gcsWrites2Sony,))
    p0.daemon = True
    if not p0.is_alive() == True:
        print("\033[32m Started Mavlink Receiver \033[0m")
        p0.start() 
    p00 = multiprocessing.Process(name='serviceParamRequests', target=serviceParamRequests, args=(mySonyCamNo1, gcsWrites2Sony, stillcap, whitebal, shut_sp, iso, focusdata, focusarea, aper, expro,))      
    p00.daemon = True
    if not p00.is_alive() == True:
        print("Service Request Daemon Active")
        p00.start()  
    p000 = multiprocessing.Process(name='mavlinkTakePhoto', target=mavlinkTakePhoto, args=(mySonyCamNo1,))      
    p000.daemon = True
    if not p000.is_alive() == True:
        print("Take a photo Daemon Active")
        p000.start()  
        
    while a:
        # ========== if deamons die respawn them =================================================
        #
        if not p0.is_alive() == True:
            p0 = multiprocessing.Process(name='run_process_mavlink', target=run_process_messages_from_connection, args=(frame, cID, gcsWrites2Sony,))
            p0.daemon = True
            p0.start() 

        if not p00.is_alive() == True:
            p00 = multiprocessing.Process(name='serviceParamRequests', target=serviceParamRequests, args=(mySonyCamNo1, gcsWrites2Sony, stillcap, whitebal, shut_sp, iso, focusdata, focusarea, aper, expro,))      
            p00.daemon = True
            p00.start() 

        if not p000.is_alive() == True:
            p000 = multiprocessing.Process(name='mavlinkTakePhoto', target=mavlinkTakePhoto, args=(mySonyCamNo1,))      
            p000.daemon = True
            p000.start() 
            
        # ============= check for write actions to the camera (wait until a change of state has been made by the GCS)
        #
        v,p,st = gcsWrites2Sony.getVal_sony_ex_pro(gcsWrites2Sony.STATE_CAM_READING)
        if ((not (v == gcsWrites2Sony.STATE_INIT)) and (st == True)):            
            p1 = multiprocessing.Process(name='manageAlphaCameraExpro', target=manageAlphaCameraExpro, args=(mySonyCamNo1, gcsWrites2Sony, expro,)).start()
            if p1 is not None:
                p1.join()             
        v,p,st = gcsWrites2Sony.getVal_sony_aperture(gcsWrites2Sony.STATE_CAM_READING)                
        if ((not (v == gcsWrites2Sony.STATE_INIT)) and (st == True)):     
            p3 = multiprocessing.Process(name='manageAlphaCameraAperture', target=manageAlphaCameraAperture, args=(mySonyCamNo1, gcsWrites2Sony, aper,)).start()
            if p3 is not None:            
                p3.join()                
        v,p,st = gcsWrites2Sony.getVal_sony_focus(gcsWrites2Sony.STATE_CAM_READING)                  
        if ((not (v == gcsWrites2Sony.STATE_INIT)) and (st == True)):    
            p5 = multiprocessing.Process(name='manageAlphaCameraFocusData', target=manageAlphaCameraFocusData, args=(mySonyCamNo1, gcsWrites2Sony, focusdata, focusarea,)).start()
            if p5 is not None:              
                p5.join()
        v,p,st = gcsWrites2Sony.getVal_sony_iso(gcsWrites2Sony.STATE_CAM_READING)                
        if ((not (v == gcsWrites2Sony.STATE_INIT)) and (st == True)):   
            p7 = multiprocessing.Process(name='manageAlphaCameraIso', target=manageAlphaCameraIso, args=(mySonyCamNo1, gcsWrites2Sony, iso,)).start()
            if p7 is not None:  
                p7.join()
        v,p,st = gcsWrites2Sony.getVal_sony_shutter(gcsWrites2Sony.STATE_CAM_READING)                
        if ((not (v == gcsWrites2Sony.STATE_INIT)) and (st == True)):   
            p9 = multiprocessing.Process(name='manageAlphaCameraShutSpd', target=manageAlphaCameraShutSpd, args=(mySonyCamNo1, gcsWrites2Sony, shut_sp,)).start()
            if p9 is not None:              
                p9.join()
        v,p,st = gcsWrites2Sony.getVal_sony_white_bal(gcsWrites2Sony.STATE_CAM_READING)                
        if ((not (v == gcsWrites2Sony.STATE_INIT)) and (st == True)):  
            p11 = multiprocessing.Process(name='manageAlphaWhiteBala', target=manageAlphaWhiteBala, args=(mySonyCamNo1, gcsWrites2Sony, whitebal,)).start()
            if p11 is not None:                
                p11.join() 
        v,p,st = gcsWrites2Sony.getVal_sony_still_cap_mode(gcsWrites2Sony.STATE_CAM_READING)                
        if ((not (v == gcsWrites2Sony.STATE_INIT)) and (st == True)):                   
            p13 = multiprocessing.Process(name='manageAlphaCameraStillCap', target=manageAlphaCameraStillCap, args=(mySonyCamNo1, gcsWrites2Sony, stillcap,)).start()
            #time.sleep(0.1) 
            if p13 is not None:               
                p13.join()

        # ========== send back to GCS via mavlink if a new change of state has been detected or polled if requested 
        #        
        p2 = multiprocessing.Process(name='sendMavExpro', target=sendMavExpro, args=(mySonyCamNo1, expro, cID,)).start()
        p4 = multiprocessing.Process(name='sendMavAper', target=sendMavAper, args=(mySonyCamNo1, aper, cID,)).start()
        p6 = multiprocessing.Process(name='sendMavFocusData', target=sendMavFocusData, args=(mySonyCamNo1, focusdata, focusarea, cID, )).start()
        p8 = multiprocessing.Process(name='sendMavIso', target=sendMavIso, args=(mySonyCamNo1, iso, cID, )).start()
        p10 = multiprocessing.Process(name='sendMavShutSpd', target=sendMavShutSpd, args=(mySonyCamNo1, shut_sp, cID, )).start()
        p12 = multiprocessing.Process(name='sendMavWhiteBala', target=sendMavWhiteBala, args=(mySonyCamNo1, whitebal, cID, )).start()
        p14 = multiprocessing.Process(name='sendMavStillCap', target=sendMavStillCap, args=(mySonyCamNo1, stillcap, cID, )).start() 
        if p2 is not None:        
            p2.join()
        if p4 is not None:              
            p4.join()
        if p6 is not None:          
            p6.join()
        if p8 is not None:          
            p8.join()
        if p10 is not None:          
            p10.join()
        if p12 is not None:          
            p12.join()  
        if p14 is not None:          
            p14.join() 
        #
        # a = False
        #
        #if p0 is not None:           
           #p0.join()
        #   if p0.is_alive() == True:
        #       p0.terminate()
    
    #
    # alternative if we want in main to program we can use daemon (procs) as shown here
    # we do not wait for daemons to complete
    # https://ja.pymotw.com/2/multiprocessing/basics.html
    # https://techacademy.jp/magazine/20607 

    # we could for example put a while loop inside this function and just run continuosly in the back ground looping as a daemon proc
    #    
    # d = multiprocessing.Process(name='manageAlphaCameraStillCap', target=manageAlphaCameraStillCap, args=(mySonyCamNo1, gcsWrites2Sony, stillcap))
    # d.daemon = True
    # n = multiprocessing.Process(name='manageAlphaCameraStillCap', target=sendMavStillCap, args=(mySonyCamNo1, shut_sp, ConnID ))
    # n.daemon = False
    # d.start()
    # n.start()

    # wait for a process e.g. non-daemon with a timeout of 5 seconds
    # n.join(5)
    #
    # if its still alive and you want to kill it
    #
    # to check it is n.is_alive()
    # if n.is_alive() == True:
    #     n.terminate()
    # print(n.exitcode) # === the exit code from the routine
    
    #
    # Release the shared memory
    #	
    del expro
    del stillcap     
    del aper
    del focusdata
    del focusarea
    del shut_sp
    del whitebal
    del stillcap
	
