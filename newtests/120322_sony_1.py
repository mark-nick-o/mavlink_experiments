# #############################################################################################################################
# for lint check use flake8 : I havent bothered with some asthetic issues hopefully all syntax or errors are flushed 
# install :: pip install flake8 flake8-import-order
#            pip install pep8
#            sudo apt install mypy
# run     :: flake8 <thisProgramName>
#            mypy --ignore-missing-imports <thisProgramName> 
# ##############################################################################################################################
# ===============================================================================================================================
#
# Name : mavlinkSonyCamWriteVals.py
# Desc : Global memory value class for use to write mavlink to sony cam
# Auth : AIR-obots Ai-Robots
#
# ===============================================================================================================================

import enum
import sys
#
# for paralel tasking of the camera action routines
#
# from multiprocessing import Process
import multiprocessing

# for debug
import logging

# for signal interupt handling
import signal

# for running commands in linux
import shlex, subprocess, pprint

import time
import logging

# for c++ types
import ctypes
from ctypes import *
from ctypes.util import find_library
from ctypes import CDLL

# ========= fast class of globals ===============
#
class fastGlobals:
    __slots__ = ('take_picture','start_video', 'chosen_camera') # __slots__ defines a fast variable
    take_picture: int    
    start_video: int 
    chosen_camera: int

# ==== enumerated camera state class ============
#
class camStateClass(enum.IntEnum):

    idle = 0
    taking_photo = 1
    photo_ack = 2
    uploading_photo = 3
    photo_complete = 4
    recording_vid = 5
    video_ack = 6
    uploading_vid = 7
    video_complete = 8
    configuring_photo = 9
    configuring_video = 10
    photo_continuos = 11

# ==== structure to hold the mica exposure parameters ============
#
class mica_exposure_blob(Structure):
    _fields_ = [("exp1", c_int),
                ("exp2", c_int),
                ("exp3", c_int),
                ("exp4", c_int),
                ("exp5", c_int),
                ("gain1", c_int),
                ("gain2", c_int),
                ("gain3", c_int),
                ("gain4", c_int),
                ("gain5", c_int)]
    
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
    
    # flags to incdicate write action for previous store register
    WRITE_PREV_DATA = 1
    DONT_WRITE_PREV_DATA = 0

    # mavlink write actions (requests from GCS)
    ParamStillCap = 1
    ParamWhiteBala = 2
    ParamShutSpd = 4
    ParamIso = 8
    ParamFocus = 16
    ParamFocusArea = 32
    ParamAperture = 64
    ParamExPro = 128
    ParamExPos1 = 2**8
    ParamExPos2 = 2**9
    ParamExPos3 = 2**10
    ParamExPos4 = 2**11
    ParamExPos5 = 2**12
    ParamExGain1 = 2**13
    ParamExGain2 = 2**14
    ParamExGain3 = 2**15
    ParamExGain4 = 2**16
    ParamExGain5 = 2**17
    ParamRedShut = 2**18
    ParamCamChoice = 2**19
    
    all_mica_expsoure = (ParamExPos1 | ParamExPos2 | ParamExPos3 | ParamExPos4 | ParamExPos5 | ParamExGain1 | ParamExGain2 | ParamExGain3 | ParamExGain4 | ParamExGain5)
    alpha7_options = (255 | ParamCamChoice)
    mica_options = ((2047<<8) | ParamCamChoice)
    all_options = (alpha7_options | mica_options)
    MAV_REQ_ALL_PARAM = alpha7_options                                 # >>>> to be set depending upon the camera set-up

    
    # indiviual states when a sequential priority queue is required
    FUNC_IDLE = 0
    FUNC_EX_PRO = 7
    FUNC_APER = 8
    FUNC_FOCUS = 9
    FUNC_ISO = 10
    FUNC_SS = 11
    FUNC_WB = 12
    FUNC_SC = 13

    # bit numbers representing the write protect status for each feature
    # true is write_protect state on
    #
    WriPro_EX_PRO = 1
    WriPro_APER = 2
    WriPro_FOCUS = 3
    WriPro_ISO = 4
    WriPro_SS = 5
    WriPro_WB = 6
    WriPro_SC = 7
    WriPro_FOCUSA = 8
    
    def __init__ (self):
        """this class is used  for sharing data with the other routines/claases from/to mavlink ."""
        self.set_sony_iso = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.set_sony_aperture = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.set_sony_ex_pro = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.set_sony_focus_area = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.set_sony_focus = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.set_sony_shutter = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.set_sony_white_bal = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.set_sony_still_cap_mode = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.set_mica_exposure = multiprocessing.Value(mica_exposure_blob,99,99,99,99,99,99,99,99,99,99)
        self.set_cam_choice = multiprocessing.Value('i', 0)
        self.prev_sony_iso = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.prev_sony_aperture = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.prev_sony_ex_pro = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.prev_sony_focus_area = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.prev_sony_focus = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.prev_sony_shutter = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.prev_sony_white_bal = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.prev_sony_still_cap_mode = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.prev_mica_exposure = multiprocessing.Value(mica_exposure_blob,99,99,99,99,99,99,99,99,99,99)
        self.prev_cam_choice = multiprocessing.Value('i', 99)
        self.mav_req_all_param = multiprocessing.Value(ctypes.c_ulonglong, 0)
        self.mav_ext_req_all_param = multiprocessing.Value(ctypes.c_ulonglong, 0)
        self.mav_write_pro_word = multiprocessing.Value('l', 0)
        self.take_photo = multiprocessing.Value('i', False)
        self.take_continuos = multiprocessing.Value('b', False)   
        self.cmd_wants_ack = multiprocessing.Value('b', False)  
        self.reset_cam = multiprocessing.Value('b', False)        
        self.state = multiprocessing.Value('i', mavlinkSonyCamWriteVals.STATE_INIT)
        self.mp_state = multiprocessing.Value('i', mavlinkSonyCamWriteVals.FUNC_IDLE) 
        self.clear_buffer = multiprocessing.Value('b', False) 
        mavlinkSonyCamWriteVals.numberOfVals += 8                                                      # global counter of the number of values
    
    def __del__(self):  
        """ deletes the class """
        class_name = self.__class__.__name__  
        mavlinkSonyCamWriteVals.numberOfVals -= 1                                                      # global counter of the number of values
        print('{} Deleted'.format(class_name))

    def get_value_counter(self):  
        print('mavlink to sony writes has %d set-points' % (mavlinkSonyCamWriteVals.numberOfVals))
        return mavlinkSonyCamWriteVals.numberOfVals	

    def init_class_state( self ):
        if (self.state.value == mavlinkSonyCamWriteVals.STATE_INIT):
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY

    def set_WritePro(self, myId, bit, timeout=20, reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.mav_write_pro_word.get_lock():                
                self.mav_write_pro_word.value |= (1 << bit)
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            print(f"\033[37m set the write protect word for {bit} \033[0m")
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False 

    def clear_WritePro(self, myId, bit, timeout=20, reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.mav_write_pro_word.get_lock():                
                self.mav_write_pro_word.value &= ~(1 << bit)
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            print(f"\033[37m cleared the write protect word for {bit} \033[0m")
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False
            
    def setVal_sony_iso(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            if mode == 1:
                with self.prev_sony_iso.get_lock(): 
                    self.prev_sony_iso.value = self.set_sony_iso.value
            with self.set_sony_iso.get_lock():                
                self.set_sony_iso.value = int(value)
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            print(f"\033[37m wrote the value {value} to {self.prev_sony_iso.value} {self.set_sony_iso.value} \033[0m")
            #exit(99)
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            #exit(90)
            return False 

    def clearReq_sony_iso(self,myId,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.set_sony_iso.get_lock():                
                self.set_sony_iso.value = self.prev_sony_iso.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            print(f"\033[37m Reset the sony Iso request its not writable \033[0m")
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False 
            
    def getVal_sony_iso(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = YourID
            print(' value: {} previous: {}'.format(self.set_sony_iso.value,self.prev_sony_iso.value))
            c = self.set_sony_iso.value
            p = self.prev_sony_iso.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return c,p,True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_iso.value,self.prev_sony_iso.value,False
            
    def setVal_sony_aperture(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            if mode == 1:
                with self.prev_sony_aperture.get_lock():
                    self.prev_sony_aperture.value= self.set_sony_aperture.value
            with self.set_sony_aperture.get_lock():
                self.set_sony_aperture.value = int(value)
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False 

    def clearReq_sony_aperture(self,myId,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.set_sony_aperture.get_lock():
                self.set_sony_aperture.value = self.prev_sony_aperture.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False 
            
    def getVal_sony_aperture(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = YourID
            print(' value: {} previous: {}'.format(self.set_sony_aperture.value,self.prev_sony_aperture.value))
            c = self.set_sony_aperture.value
            p = self.prev_sony_aperture.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return c,p,True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_aperture.value,self.prev_sony_aperture.value,False
            
    def setVal_sony_ex_pro(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            if mode == 1:
                with self.set_sony_ex_pro.get_lock():
                    self.prev_sony_ex_pro.value = self.set_sony_ex_pro.value
            with self.set_sony_ex_pro.get_lock():
                self.set_sony_ex_pro.value = int(value)
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False 

    def clearReq_sony_ex_pro(self,myId,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.set_sony_ex_pro.get_lock():
                self.set_sony_ex_pro.value = self.prev_sony_ex_pro.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False 
            
    def getVal_sony_ex_pro(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = YourID
            print(' value: {} previous: {}'.format(self.set_sony_ex_pro.value,self.prev_sony_ex_pro.value))
            c = self.set_sony_ex_pro.value
            p = self.prev_sony_ex_pro.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return c,p,True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_ex_pro.value,self.prev_sony_ex_pro.value,False
            
    def setVal_sony_focus_area(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            if mode == 1:
                with self.prev_sony_focus_area.get_lock():
                    self.prev_sony_focus_area.value = self.set_sony_focus_area.value
            with self.set_sony_focus_area.get_lock():
                self.set_sony_focus_area.value = int(value)
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False 

    def clearReq_sony_focus_area(self,myId,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.set_sony_focus_area.get_lock():
                self.set_sony_focus_area.value = self.prev_sony_focus_area.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False 
            
    def getVal_sony_focus_area(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = YourID
            print(' value: {} previous: {}'.format(self.set_sony_focus_area.value,self.prev_sony_focus_area.value))
            c = self.set_sony_focus_area.value
            p = self.prev_sony_focus_area.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return c,p,True
        else:
            if (reset_state == True):
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_focus_area.value,self.prev_sony_focus_area.value,False
            
    def setVal_sony_focus(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            if mode == 1:
                with self.prev_sony_focus.get_lock():
                    self.prev_sony_focus.value = self.set_sony_focus.value
            with self.set_sony_focus.get_lock():
               self.set_sony_focus.value = int(value)
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():            
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False 

    def clearReq_sony_focus(self,myId,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.set_sony_focus.get_lock():
               self.set_sony_focus.value = self.prev_sony_focus.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():            
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False
            
    def getVal_sony_focus(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = YourID
            print(' value: {} previous: {}'.format(self.set_sony_focus.value,self.prev_sony_focus.value))
            c = self.set_sony_focus.value
            p = self.prev_sony_focus.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return c,p,True
        else:
            if (reset_state == True):  
                with self.state.get_lock():            
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_focus.value,self.prev_sony_focus.value,False
            
    def setVal_sony_shutter(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            if mode == 1:
                with self.prev_sony_shutter.get_lock():
                    self.prev_sony_shutter.value = self.set_sony_shutter.value
            with self.set_sony_shutter.get_lock():
                self.set_sony_shutter.value = int(value)
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():            
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False

    def clearReq_sony_shutter(self,myId,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.set_sony_shutter.get_lock():
                self.set_sony_shutter.value = self.prev_sony_shutter.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():            
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False
            
    def getVal_sony_shutter(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = YourID
            print('value: {} previous: {}'.format(self.set_sony_shutter.value,self.prev_sony_shutter.value))
            c = self.set_sony_shutter.value
            p = self.prev_sony_shutter.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return c,p,True
        else:
            if (reset_state == True): 
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_shutter.value,self.prev_sony_shutter.value,False
            
    def setVal_sony_white_bal(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            if mode == 1:
                with self.set_sony_white_bal.get_lock():
                    self.prev_sony_white_bal.value = self.set_sony_white_bal.value
            with self.set_sony_white_bal.get_lock():
                self.set_sony_white_bal.value = int(value)
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():            
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False

    def clearReq_sony_white_bal(self,myId,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.set_sony_white_bal.get_lock():
                self.set_sony_white_bal.value = self.prev_sony_white_bal.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True):
                with self.state.get_lock():            
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False
            
    def getVal_sony_white_bal(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = YourID
            print('value: {} previous: {}'.format(self.set_sony_white_bal.value,self.prev_sony_white_bal.value))
            c = self.set_sony_white_bal.value
            p = self.prev_sony_white_bal.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return c,p,True
        else:
            if (reset_state == True): 
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_white_bal.value,self.prev_sony_white_bal.value,False
            
    def setVal_sony_still_cap_mode(self,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            if mode == 1:
                with self.set_sony_still_cap_mode.get_lock():
                    self.prev_sony_still_cap_mode.value = self.set_sony_still_cap_mode.value
            with self.set_sony_still_cap_mode.get_lock():
                self.set_sony_still_cap_mode.value = int(value)
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True): 
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False

    def clearReq_sony_still_cap_mode(self,myId,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.set_sony_still_cap_mode.get_lock():
                self.set_sony_still_cap_mode.value = self.prev_sony_still_cap_mode.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True): 
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False
            
    def getVal_sony_still_cap_mode(self,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = YourID
            print('value: {} previous: {}'.format(self.set_sony_still_cap_mode.value,self.prev_sony_still_cap_mode.value))
            c = self.set_sony_still_cap_mode.value
            p = self.prev_sony_still_cap_mode.value
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return c,p,True
        else:
            if (reset_state == True):
                with self.state.get_lock():            
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return self.set_sony_still_cap_mode.value,self.prev_sony_still_cap_mode.value,False

    def setVal_mica_exposure(self,idx,value,myId,mode=0,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            if mode == 1:
                with self.set_mica_exposure.get_lock():
                    if idx == 1:
                        self.prev_mica_exposure.exp1 = self.set_mica_exposure.exp1
                    elif idx == 2:
                        self.prev_mica_exposure.exp2 = self.set_mica_exposure.exp2
                    elif idx == 3:
                        self.prev_mica_exposure.exp3 = self.set_mica_exposure.exp3
                    elif idx == 4:
                        self.prev_mica_exposure.exp4 = self.set_mica_exposure.exp4
                    elif idx == 5:
                        self.prev_mica_exposure.exp5 = self.set_mica_exposure.exp5
                    elif idx == 6:
                        self.prev_mica_exposure.gain1 = self.set_mica_exposure.gain1
                    elif idx == 7:
                        self.prev_mica_exposure.gain2 = self.set_mica_exposure.gain2
                    elif idx == 8:
                        self.prev_mica_exposure.gain3 = self.set_mica_exposure.gain3
                    elif idx == 9:
                        self.prev_mica_exposure.gain4 = self.set_mica_exposure.gain4
                    elif idx == 10:
                        self.prev_mica_exposure.gain5 = self.set_mica_exposure.gain5
            with self.set_mica_exposure.get_lock():
                if idx == 1:
                    self.set_mica_exposure.exp1 = = int(value)
                elif idx == 2: 
                    self.set_mica_exposure.exp2 = = int(value)
                elif idx == 3: 
                    self.set_mica_exposure.exp3 = = int(value)
                elif idx == 4: 
                    self.set_mica_exposure.exp4 = = int(value)
                elif idx == 5: 
                    self.set_mica_exposure.exp5 = = int(value)
                elif idx == 6: 
                    self.set_mica_exposure.gain1 = = int(value)   
                elif idx == 7: 
                    self.set_mica_exposure.gain2 = = int(value) 
                elif idx == 8: 
                    self.set_mica_exposure.gain3 = = int(value) 
                elif idx == 9: 
                    self.set_mica_exposure.gain4 = = int(value) 
                elif idx == 10: 
                    self.set_mica_exposure.gain5 = = int(value)                     
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True): 
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False

    def clearReq_mica_exposure(self,idx,myId,timeout=20,reset_state=False):
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.set_mica_exposure.get_lock():
                if idx == 1:
                    self.set_mica_exposure.exp1 = self.prev_mica_exposure.exp1
                elif idx == 2:
                    self.set_mica_exposure.exp2 = self.prev_mica_exposure.exp2
                elif idx == 3:
                    self.set_mica_exposure.exp3 = self.prev_mica_exposure.exp3
                elif idx == 4:
                    self.set_mica_exposure.exp4 = self.prev_mica_exposure.exp4
                elif idx == 5:
                    self.set_mica_exposure.exp5 = self.prev_mica_exposure.exp5
                elif idx == 6:
                    self.set_mica_exposure.gain1 = self.prev_mica_exposure.gain1
                elif idx == 7:
                    self.set_mica_exposure.gain2 = self.prev_mica_exposure.gain2
                elif idx == 8:
                    self.set_mica_exposure.gain3 = self.prev_mica_exposure.gain3
                elif idx == 9:
                    self.set_mica_exposure.gain4 = self.prev_mica_exposure.gain4
                elif idx == 10:
                    self.set_mica_exposure.gain5 = self.set_mica_exposure.gain5
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return True
        else:
            if (reset_state == True): 
                with self.state.get_lock():
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return False
            
    def getVal_mica_exposure(self,idx,YourID,timeout=20,reset_state=False):  
        timeCnt = 0
        while (not (self.state.value == mavlinkSonyCamWriteVals.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = YourID
            if idx == 1:
                print('value: {} previous: {}'.format(self.set_mica_exposure.exp1, self.prev_mica_exposure.exp1))
                c = self.set_mica_exposure.exp1
                p = self.prev_sony_still_cap_mode.exp1
            elif idx == 2:
                print('value: {} previous: {}'.format(self.set_mica_exposure.exp2, self.prev_mica_exposure.exp2))
                c = self.set_mica_exposure.exp2
                p = self.prev_sony_still_cap_mode.exp2
            elif idx == 3:
                print('value: {} previous: {}'.format(self.set_mica_exposure.exp3, self.prev_mica_exposure.exp3))
                c = self.set_mica_exposure.exp3
                p = self.prev_sony_still_cap_mode.exp3
            elif idx == 4:
                print('value: {} previous: {}'.format(self.set_mica_exposure.exp4, self.prev_mica_exposure.exp4))
                c = self.set_mica_exposure.exp4
                p = self.prev_sony_still_cap_mode.exp4
            elif idx == 5:
                print('value: {} previous: {}'.format(self.set_mica_exposure.exp5, self.prev_mica_exposure.exp5))
                c = self.set_mica_exposure.exp5
                p = self.prev_sony_still_cap_mode.exp5
            elif idx == 6:
                print('value: {} previous: {}'.format(self.set_mica_exposure.gain1, self.prev_mica_exposure.gain1))
                c = self.set_mica_exposure.gain1
                p = self.prev_sony_still_cap_mode.gain1
            elif idx == 7:
                print('value: {} previous: {}'.format(self.set_mica_exposure.gain2, self.prev_mica_exposure.gain2))
                c = self.set_mica_exposure.gain2
                p = self.prev_sony_still_cap_mode.gain2
            elif idx == 8:
                print('value: {} previous: {}'.format(self.set_mica_exposure.gain3, self.prev_mica_exposure.gain3))
                c = self.set_mica_exposure.gain3
                p = self.prev_sony_still_cap_mode.gain3
            elif idx == 9:
                print('value: {} previous: {}'.format(self.set_mica_exposure.gain4, self.prev_mica_exposure.gain4))
                c = self.set_mica_exposure.gain4
                p = self.prev_sony_still_cap_mode.gain4
            elif idx == 10:
                print('value: {} previous: {}'.format(self.set_mica_exposure.gain5, self.prev_mica_exposure.gain5))
                c = self.set_mica_exposure.gain5
                p = self.prev_sony_still_cap_mode.gain5
            with self.state.get_lock():
                self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return c,p,True
        else:
            if (reset_state == True):
                with self.state.get_lock():            
                    self.state.value = mavlinkSonyCamWriteVals.STATE_READY
            return 0,0,False
            
    def setMavIsoModeData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_iso(dataRcv,mavlinkSonyCamWriteVals.STATE_MAV_WRITING,mavlinkSonyCamWriteVals.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavIsoModeData( self ):
    
        ret = False  
        set_sony_iso = 0
        prev_sony_iso = 0        
        set_sony_iso,prev_sony_iso,ret = self.getVal_sony_iso(mavlinkSonyCamWriteVals.STATE_MAV_READING) 
        return set_sony_iso,prev_sony_iso,ret
        
    def setMavApertureData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_aperture(dataRcv,mavlinkSonyCamWriteVals.STATE_MAV_WRITING,mavlinkSonyCamWriteVals.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavApertureData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_aperture(mavlinkSonyCamWriteVals.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavExProData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_ex_pro(dataRcv,mavlinkSonyCamWriteVals.STATE_MAV_WRITING,mavlinkSonyCamWriteVals.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavExProData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_ex_pro(mavlinkSonyCamWriteVals.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavFocusAreaData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_focus_area(dataRcv,mavlinkSonyCamWriteVals.STATE_MAV_WRITING,mavlinkSonyCamWriteVals.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavFocusAreaData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_focus_area(mavlinkSonyCamWriteVals.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavFocusData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_focus(dataRcv,mavlinkSonyCamWriteVals.STATE_MAV_WRITING,mavlinkSonyCamWriteVals.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavFocusData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_focus(mavlinkSonyCamWriteVals.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavShutterData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_shutter(dataRcv,mavlinkSonyCamWriteVals.STATE_MAV_WRITING,mavlinkSonyCamWriteVals.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavShutterData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_shutter(mavlinkSonyCamWriteVals.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavWhiteBalData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_white_bal(dataRcv,mavlinkSonyCamWriteVals.STATE_MAV_WRITING,mavlinkSonyCamWriteVals.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavWhiteBalData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_white_bal(mavlinkSonyCamWriteVals.STATE_MAV_READING) 
        return set_sony,prev_sony,ret
        
    def setMavStillCapModeData( self, dataRcv ):
    
        ret = False               
        ret = self.setVal_sony_still_cap_mode(dataRcv,mavlinkSonyCamWriteVals.STATE_MAV_WRITING,mavlinkSonyCamWriteVals.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavStillCapModeData( self ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_sony_still_cap_mode(mavlinkSonyCamWriteVals.STATE_MAV_READING) 
        return set_sony,prev_sony,ret

    def setMavMicaExposureData( self, dataRcv, idx ):
    
        ret = False               
        ret = self.setVal_mica_exposure(idx,dataRcv,mavlinkSonyCamWriteVals.STATE_MAV_WRITING,mavlinkSonyCamWriteVals.DONT_WRITE_PREV_DATA,5) 
        return ret

    def getMavMicaExposureData( self, idx ):
    
        ret = False  
        set_sony = 0
        prev_sony = 0        
        set_sony,prev_sony,ret = self.getVal_mica_exposure(idx,mavlinkSonyCamWriteVals.STATE_MAV_READING) 
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

    def __init__ (self, name = 'value_name_not_set', signal = 0,  prev = 0,  state = STATE_READY):
        """this class is for storing information in an object with real-time properties."""
        self.signal = multiprocessing.Value('i', signal)                                   # signal.value value
        self.prev = multiprocessing.Value('i', prev)                                       # previous signal value
        self.state = multiprocessing.Value('i', state)                                     # state of the value
        self.nextpointer = None                                                            # pointer for chain if needed
        self.name = name                                                                   # name as a string
        self.timestamp = multiprocessing.Value('l', 0)                                     # timestamp
        self.updateNeeded = multiprocessing.Value('b', False)                              # update required
        self.ack_send = multiprocessing.Value('b', False)                                  # param_ext_ack needed
        self.index = 0                                                                     # index number used for ack send
        memoryValue.numberOfVals += 1                                                      # global counter of the number of values
    
    def __del__(self):  
        """ deletes the class """
        class_name = self.__class__.__name__  
        memoryValue.numberOfVals -= 1                                                      # global counter of the number of values
        print('{} Deleted'.format(class_name))

    def get_value_counter(self):  
        print('%s: %d' % (self.name,memoryValue.numberOfVals))
        return memoryValue.numberOfVals		
  
    def get_value_data(self,YourID,timeout=100):  
        timeCnt = 0
        while (not (self.state.value == memoryValue.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = YourID
            print('Description: {}. value: {} previous: {}'.format(self.name, self.signal.value,self.prev.value))
            with self.state.get_lock():
                self.state.value = memoryValue.STATE_READY
            return self.name,self.signal.value,self.prev.value,True
        else:
            return self.name,self.signal.value,self.prev.value,False

    def set_value(self,value,myId,timeout=100):
        timeCnt = 0
        while (not (self.state.value == memoryValue.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            with self.state.get_lock():
                self.state.value = myId
            with self.prev.get_lock():
                self.prev.value = self.signal.value
            with self.signal.get_lock():
                self.signal.value = value
            with self.updateNeeded.get_lock():
                self.updateNeeded.value = True
            with self.state.get_lock():
                self.state.value = memoryValue.STATE_READY
            return True
        else:
            return False

    def get_value_data_if_avail(self,YourID):  
        if  (self.state.value == memoryValue.STATE_READY):
            with self.state.get_lock():
                self.state.value = YourID
            print('Description: {}. value: {}'.format(self.name, self.signal.value))
            with self.state.get_lock():
                self.state.value = memoryValue.STATE_READY
            return self.name,self.signal.value,self.prev.value,True
        else:
            return self.name,self.signal.value,self.prev.value,False

    def set_update_flag( self, stateSent, myId ):
        if (self.state.value == memoryValue.STATE_READY):
            with self.state.get_lock():
                self.state.value = myId
            with self.state.get_lock():
                self.updateNeeded.value = stateSent
            with self.state.get_lock():
                self.state.value = memoryValue.STATE_READY
            return True
        else:
            return False

    def get_update_flag( self, myId ):
        v = 0
        if (self.state.value == memoryValue.STATE_READY):
            with self.state.get_lock():
                self.state.value = myId
            v = self.updateNeeded.value 
            with self.state.get_lock():
                self.state.value = memoryValue.STATE_READY
            return v,True
        else:
            return v,False
            
    def set_ack_send( self, stateSent, myId ):
        if (self.state.value == memoryValue.STATE_READY):
            with self.state.get_lock():
                self.state.value = myId
            with self.ack_send.get_lock():
                self.ack_send.value = stateSent
            with self.state.get_lock():
                self.state.value = memoryValue.STATE_READY
            return True
        else:
            return False			

    def get_ack_send( self, myId ):
        v = 0
        if (self.state.value == memoryValue.STATE_READY):
            with self.state.get_lock():
                self.state.value = myId
            v = self.ack_send.value 
            with self.state.get_lock():
                self.state.value = memoryValue.STATE_READY
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

import multiprocessing
import ctypes

# ------------------- Linked List Class --------------------------------------
#
# typical use here is to to hold RedEdge exposure bundle of parameters
#
class LinkedListMemory:

    # stores number of objects created
    numberOfVals = 0
    
    class Node:

        def __init__(self, name = 'value_name_not_set', payload = 0,  prev = 0 ):
            """this class is for storing information in an object with real-time properties."""
            self.payload = multiprocessing.Value('f', payload)                                 # payload.value value
            self.prev = multiprocessing.Value('f', prev)                                       # previous signal value
            self.nextpointer = None                                                            # pointer for chain if needed
            self.name = name                                                                   # name as a string
            self.timestamp = multiprocessing.Value('l', 0)                                     # timestamp
            self.updateNeeded = multiprocessing.Value('b', False)                              # update required
            self.ack_send = multiprocessing.Value('b', False)                                  # param_ext_ack needed
            LinkedListMemory.numberOfVals += 1                                                 # global counter of the number of values
            self.index = multiprocessing.Value('i', LinkedListMemory.numberOfVals)             # index number used for ack send
            
        def __del__(self):  
            """ deletes the class """
            class_name = self.__class__.__name__  
            LinkedListMemory.numberOfVals -= 1                                                      # global counter of the number of values
            print('{} Deleted'.format(class_name))
        
    def __init__(self):
        self.head = None

    # add a new box to the chain of linked boxes
    #
    def addNode(self, tag, newpayload, prev):		
        newnode = LinkedListMemory.Node(tag, newpayload, prev)
        if self.head == None:
            self.head = newnode
            return
        else:   # The case of concatenating to the last node
            runner = self.head
            while runner.nextpointer != None:
                runner = runner.nextpointer
            runner.nextpointer = newnode
            
    # does it contain the value if so return the index
    #
    def contains_val(self, cat):
        lastbox = self.head
        while (lastbox):
            if cat == lastbox.payload.value:
                return True
            else:
                lastbox = lastbox.nextpointer
        return False

    # does it contain the value if so return the index
    #
    def contains_tag(self, cat):
        lastbox = self.head
        idx = 0
        while (lastbox):
            if not lastbox.name.find(cat) == -1:
                return True, idx
            else:
                lastbox = lastbox.nextpointer
            idx += 1
        return False
        
    # get the values from the index
    #
    def get_values(self, catIndex):
        lastbox = self.head
        boxIndex = 0
        while boxIndex <= catIndex:
            if boxIndex == catIndex:
                return lastbox.payload.value, lastbox.prev.value
            boxIndex = boxIndex + 1
            lastbox = lastbox.nextpointer
        return None
        
    # get the values from the index
    #
    def get_all(self, catIndex):
        lastbox = self.head
        boxIndex = 0
        while boxIndex <= catIndex:
            if boxIndex == catIndex:
                return lastbox.payload.value, lastbox.prev.value, lastbox.name
            boxIndex = boxIndex + 1
            lastbox = lastbox.nextpointer
        return None
        
    # set the current value of the index
    #
    def set_value(self, catIndex, setVal):
        lastbox = self.head
        boxIndex = 0
        while boxIndex <= catIndex:
            if boxIndex == catIndex:
                with lastbox.prev.get_lock():
                    lastbox.prev.value = lastbox.payload.value
                with lastbox.payload.get_lock():
                    lastbox.payload.value = setVal
            boxIndex = boxIndex + 1
            lastbox = lastbox.nextpointer

    # get the value of the update flag
    #
    def get_update_flag(self, catIndex):
        lastbox = self.head
        boxIndex = 0
        while boxIndex <= catIndex:
            if boxIndex == catIndex:
                return lastbox.updateNeeded.value
            boxIndex = boxIndex + 1
            lastbox = lastbox.nextpointer

    # set the current value of the update flag
    #
    def set_update_flag(self, catIndex, setVal):
        lastbox = self.head
        boxIndex = 0
        while boxIndex <= catIndex:
            if boxIndex == catIndex:
                with lastbox.updateNeeded.get_lock():
                    lastbox.updateNeeded.value = setVal
            boxIndex = boxIndex + 1
            lastbox = lastbox.nextpointer

    # get the value of the ack flag
    #
    def get_ack_send(self, catIndex):
        lastbox = self.head
        boxIndex = 0
        while boxIndex <= catIndex:
            if boxIndex == catIndex:
                return lastbox.ack_send.value
            boxIndex = boxIndex + 1
            lastbox = lastbox.nextpointer

    # set the current value of the ack flag
    #
    def set_ack_send(self, catIndex, setVal):
        lastbox = self.head
        boxIndex = 0
        while boxIndex <= catIndex:
            if boxIndex == catIndex:
                with lastbox.ack_send.get_lock():
                    lastbox.ack_send.value = setVal
            boxIndex = boxIndex + 1
            lastbox = lastbox.nextpointer

    # get the value of the timestamp
    #
    def get_timestamp(self, catIndex):
        lastbox = self.head
        boxIndex = 0
        while boxIndex <= catIndex:
            if boxIndex == catIndex:
                return lastbox.timestamp.value
            boxIndex = boxIndex + 1
            lastbox = lastbox.nextpointer
            
    # set the current value of the timestamp
    #
    def set_timestamp(self, catIndex, setVal):
        lastbox = self.head
        boxIndex = 0
        while boxIndex <= catIndex:
            if boxIndex == catIndex:
                with lastbox.timestamp.get_lock():
                    lastbox.timestamp.value = setVal
            boxIndex = boxIndex + 1
            lastbox = lastbox.nextpointer

    # get the value of the timestamp
    #
    def get_index(self, catIndex):
        lastbox = self.head
        boxIndex = 0
        while boxIndex <= catIndex:
            if boxIndex == catIndex:
                return lastbox.index.value, boxIndex
            boxIndex = boxIndex + 1
            lastbox = lastbox.nextpointer
            
if __name__ == "__main__":		
	
    # ----- unit test the class then delete the objects here -----
    red_edge_exposure = LinkedListMemory()
    red_edge_exposure.addNode("RED_EXP_1", 0.26, 0)
    red_edge_exposure.addNode("RED_EXP_2", 0.99, 99)
    red_edge_exposure.addNode("RED_EXP_3", 0.127, 99)
    red_edge_exposure.addNode("RED_EXP_4", 0.42, 99)
    red_edge_exposure.addNode("RED_EXP_5", 367.3, 99)
    red_edge_exposure.addNode("RED_GAIN_1", 26, 0)
    red_edge_exposure.addNode("RED_GAIN_2", 99, 99)
    red_edge_exposure.addNode("RED_GAIN_3", 127, 99)
    red_edge_exposure.addNode("RED_GAIN_4", 42, 99)
    red_edge_exposure.addNode("RED_GAIN_5", 367, 99)
    print(red_edge_exposure.get_values(3))
    red_edge_exposure.set_value(0,453)
    print(red_edge_exposure.get_values(0))
    print(red_edge_exposure.contains_val(99))
    print(red_edge_exposure.contains_tag("RED_GAIN_1"))
    res, x = red_edge_exposure.contains_tag("RED_GAIN_5")
    if res == True:
        red_edge_exposure.set_value(x,2.111)
    print(x)
    print(red_edge_exposure.get_values(x))

    red_edge_exposure.set_update_flag(2, True)
    print(red_edge_exposure.get_update_flag(0))
    print(red_edge_exposure.get_update_flag(2))
    red_edge_exposure.set_ack_send(1, True)
    print(red_edge_exposure.get_ack_send(1))
    
    print(red_edge_exposure.get_index(9))
    print(red_edge_exposure.get_index(0))
    
    print(f"the number {LinkedListMemory.numberOfVals} {red_edge_exposure.numberOfVals}")    
    del red_edge_exposure
    
# ------------------------------------------------------------------ micaSense Camera  Library ----------------------------------------------------------------------------------------------------------
#
#                                                                    using http request
#                                                                    air cam pro
#

# if you have minimal you might need sudo apt install libpython2.7-stdlib
#
# pip install requests
#
import requests
import json

#
# for UTC time
#
# pip install datetime
#
import datetime  as  dt

# sudo apt-get install python3-pip
# sudo pip-3.2 install pytz
#
import pytz
import time

# ntp time sync and set your clock utilities
#
#
import sys,os

# for splitting dates and times if needed
#
# pip install arrow
#
import arrow
#import maya

#
# ntp time sync 
#
import ntplib
from time import ctime

# xml parsing
#
# pip install elementpath
#
import xml.etree.ElementTree as ET 

import numpy as np
import cv2

class micaSenseCamera():

    # constants / definitions
    #
    HTTP_SUCCESS_RETURN = 200
    WIFI_CAM = "192.168.10.254"
    ETHER_CAM = "192.168.1.83"
    CAM_HOST_IP = WIFI_CAM                               # set this for the camera you want to use
    NTP_SYNC_THRESHOLD = 1000                            # frequency of ntp server syncronisation
    NTP_TIME_SYNC_ENABLE = 1                             # enable if 1 to use ntp timesync :: Internet conenction required (GPRS)

    CALIBRATE_USING_PANEL = True                         # when passed to the CaptureFivePictures method enters calibration sequence 
    
    # globals used by the class
    #
    ntp_sync_freq = 0 

    # wifi credentials (default)
    #
    WIFI_SSID = "rededgeRX03-2136114-SC"
    WIFI_PASSWD = "micasense"
    
# =================================================================================== Functions ==================================================================================================================
#
# General functions have prefix micaSense whereas specific camera actions shall have prefix by type e.g. redEye redEdge
#

    # set the system clock on linux or windows
    #
    def ntp_time_change( self, s, unixTime=0, winTimeTuple=( 0, 0, 0, 0, 0, 0, 0 ) ):
        #
        # check and change these formats to suit ntp time sync 
        #
        if s == 1:os.system('date -s unixTime')                  # date command for linux format "2 OCT 2006 18:00:00" 
        elif s == 2:
            try:
              import pywin32
            except ImportError:
              print ("pywin32 module is missing")
              sys.exit(1)
            dayOfWeek = datetime.datetime(winTimeTuple).isocalendar()[2]
            #pywin32.SetSystemTime( year, month, dayOfWeek, day, hour, minute, second, millseconds )# fill all Parameters with int numbers
            pywin32.SetSystemTime( winTimeTuple[:2] + (dayOfWeek,) + winTimeTuple[2:] )
        else:
            print ("wrong param")

    # check our operating system
    #
    def check_os( self ):
        if ((sys.platform=='linux2') or (sys.platform=='linux')): return 1
        elif  sys.platform=='win32': return 2
        else: return 3

    # split the ntp time message
    #
    def getTimeElementsFromNtpMsg( self, ntpTimeMsg ):
       vars = ntpTimeMsg.split()
       year = f"{vars[4]}"
       month = f"{vars[1]}"
       dayOfWeekString = f"{vars[0]}"
       day = f"{vars[2]}" 
       time = f"{vars[3]}"
       timeArray = time.split(",")
       hours = f"{timeArray[0]}"
       minute = f"{timeArray[1]}"
       seconds = f"{timeArray[2]}"
       miliseconds = 0
       unix_time = f"{vars[2]} {vars[1]} {vars[4]} {vars[3]}"     
       win_time_tuple = ( year,    # Year
                  month,       # Month
                  day,         # Day
                  hours,       # Hour
                  minute,      # Minute
                  seconds,     # Second
                  0,           # Millisecond
              )
       return win_time_tuple, unix_time
       
    # sync our time to the ntp time clock response
    #
    def ntp_time_sync( self ):
        c = ntplib.NTPClient()
        response = c.request('pool.ntp.org')
        print(ctime(response.tx_time))
        my_os = self.check_os()
        winTimeTuple, unixTime = self.getTimeElementsFromNtpMsg(ctime(response.tx_time))
        self.ntp_time_change( my_os, unixTime, winTimeTuple )

    # This function will try to reconenct the wifi to the camera
    #    
    # at present for linux only  
    # it also requires network manager package
    #
    # sudo apt-get install network-manager
    #
    # Try to reconnect a broken wifi connection return TRue if SSID matches 
    # that specified
    #
    def reConnectWiFi( self, ssid=WIFI_SSID, passwd=WIFI_PASSWD ):
        print("ATTEMPT:: re-connecting wifi......... ")
        if (self.check_os() == 1):
            cmd = f"sudo nmcli device wifi con {ssid} password {passwd}"
            x = os.popen(cmd, 'r')
            cmd = "iwconfig"
            x = os.popen(cmd, 'r')
            print(x)
            for line in x:
                if not line.find("wlan0") == -1:
                    zz = line.split() 
            SSIDFromRadio = zz[3].split(":")
            print(f" connected to : {SSIDFromRadio[0]} ")
            print(f" connected to : {SSIDFromRadio[1]} ")
        return not (SSIDFromRadio[1].find(self.WIFI_SSID) == -1)
        
    def print_myJson( self, cap_data ):
        try:
            if (cap_data.status_code == self.HTTP_SUCCESS_RETURN):
                print (cap_data.json())
            else:
                print (f"http REST API error {cap_data.status_code}")
        except Exception:
            print("invalid json sent to function")
            
    # Post a message to the camera commanding an action without any retry 
    #
    def micaSensePostNoRetry( self, url, json_para={ 'block' : True }, withParam=False ):
            
        try:
            #capture_data = requests.post( url, json=json_para, timeout=30)
            print(f" posting to   {url}")
            if (withParam == False):
                capture_data = requests.post( url, timeout=20 )
            else:
                capture_data = requests.post( url, json=json_para, timeout=30)             
        except requests.ConnectionError as e:
            print("OOPS!! Connection Error. Make sure you are connected to Device.\n")
            print(str(e))            
        except requests.Timeout as e:
            print("OOPS!! Timeout Error")
            print(str(e))
        except requests.RequestException as e:
            print("OOPS!! General Error")
            print(str(e))
        except KeyboardInterrupt:
            print("Someone closed the program")
            
        if capture_data:
            self.print_myJson( capture_data )
        return capture_data  

    # Post a message to the camera commanding an action with retry
    #
    def micaSensePost( self, url, json_para={ 'block' : True }, retrys=3, withParam=False ):

        retries = retrys 
        while retries >= 1:           
            try:
                print(f" posting to   {url}")
                if (withParam == True):
                    capture_data = requests.post( url, json=json_para, timeout=30)
                else:
                    capture_data = requests.post( url, timeout=3 )
                ret = 1
            except requests.ConnectionError as e:
                print("OOPS!! Connection Error. Make sure you are connected to Device.\n")
                print(str(e))  
                ret = -1          
            except requests.Timeout as e:
                print("OOPS!! Timeout Error")
                print(str(e))
                ret = -2
            except requests.RequestException as e:
                print("OOPS!! General Error")
                print(str(e))
                ret = -3
            except KeyboardInterrupt:
                print("Someone closed the program")
            
            if (ret == 1):
                retries = -1
            else:
                retries -= 1  
               
        
        if (ret>=1):    
            if (capture_data.status_code >= 200) and (capture_data.status_code <= 299) :
                self.print_myJson( capture_data )
        else:
            capture_data=0
        return ret,capture_data 
        
    # Get a message from the camera reading a status
    #
    def micaSenseGetNoRetry( self, url, json_para={ 'block' : True } ):
           
        try:
            capture_data = requests.get( url, json=json_para, timeout=30)
            #capture_data = requests.get( url, timeout=30)
        except requests.ConnectionError as e:
            print("OOPS!! Connection Error. Make sure you are connected to Device.\n")
            print(str(e))            
            #continue
        except requests.Timeout as e:
            print("OOPS!! Timeout Error")
            print(str(e))
            #continue
        except requests.RequestException as e:
            print("OOPS!! General Error")
            print(str(e))
            #continue
        except KeyboardInterrupt:
            print("Someone closed the program")
        if capture_data:
            self.print_myJson( capture_data )
        return capture_data 

    # Get a message from the camera reading a status
    #
    def micaSenseGet( self, url, json_para={ 'block' : True }, retrys=3 ):
          
        retries = retrys 
        while retries >= 1: 
            try:
                capture_data = requests.get( url, json=json_para, timeout=30)
                ret = 1
            except requests.ConnectionError as e:
                print("OOPS!! Connection Error. Make sure you are connected to Device.\n")
                print(str(e))            
                ret = -1 
            except requests.Timeout as e:
                print("OOPS!! Timeout Error")
                print(str(e))
                ret = -2 
            except requests.RequestException as e:
                print("OOPS!! General Error")
                print(str(e))
                ret = -3 
            except KeyboardInterrupt:
                print("Someone closed the program")
                
            if (ret == 1):
                retries = -1
            else:
                retries -= 1  
                
        if (ret >= 1):    
            if (capture_data.status_code >= 200) and (capture_data.status_code <= 299) :
                self.print_myJson( capture_data )
        else:
            capture_data=0
        return ret,capture_data 
        
    def micaSensePrintId( self, capture_data ):
    
        json_data_cap_resp = capture_data.json()
        id = str(json_data_cap_resp['id'])
        return id        
        
    # Post a message to the RedEye camera commanding a capture, block until complete
    #
    def redEyeCapture( self ):

        # parameters for RedEye Camera
        #       
        capture_params = { 'store_capture' : True, 'block' : True }       
        url = "http://" + self.CAM_HOST_IP + "/capture"
        
        capture_data = self.micaSensePostNoRetry( url, capture_params, True )
        if capture_data:
             self.print_myJson( capture_data )
        return capture_data.status_code,capture_data 

    # Post a message to the RedEdge camera commanding a capture, block until complete
    #        
    def redEdgeCaptureWithoutReconnect( self ):

        # parameters for RedEdge Camera
        #
        capture_params = {
            'anti_sat' : False,	                #   If true, strong anti-saturation rules are used for the capture
            'block' : True,                     #	When 'true', the HTTP request will not return until the capture is complete.
            'detect_panel' : True,              #	When 'true', the camera will not return an image until a MicaSense reflectance panel is detected
            'preview' : False,                  #	When 'true', updates the current preview image
            'cache_jpeg' : 0,	                #   /config's enabled_bands_jpeg	Bitmask for bands from which to capture and cache JPEG images  
            'cache_raw'	: 0,                    #   /config's enabled_bands_raw	Bitmask for bands from which to capture and cache RAW (tiff) images.    
            'store_capture' : True,	            #   Store this image to the SD card based on configuration settings.
            'use_post_capture_state' : False	#   When 'true', the camera will try and retrieve state information from the /capture_state route before falling back on default values.        
        }        
        url = "http://" + self.CAM_HOST_IP + "/capture"

        print(" red Edge capture ")
        capture_data = self.micaSensePostNoRetry( url, capture_params )
        if capture_data:
            self.print_myJson( capture_data )
        else:
            print("Capture Failed")
            exit(1)
        return capture_data.status_code,capture_data         

    # Post a message to the RedEdge camera commanding a capture, block until complete if no conenction attempt re-connect the wifi
    #        
    def redEdgeCapture( self, retry=2, withCalibration=False  ):

        # parameters for RedEdge Camera if you want to do a calibration
        #
        capture_params = {
            'anti_sat' : False,	                #   If true, strong anti-saturation rules are used for the capture
            'block' : True,                     #	When 'true', the HTTP request will not return until the capture is complete.
            'detect_panel' : True,              #	When 'true', the camera will not return an image until a MicaSense reflectance panel is detected
            'preview' : False,                  #	When 'true', updates the current preview image
            'cache_jpeg' : 0,	                #   /config's enabled_bands_jpeg	Bitmask for bands from which to capture and cache JPEG images  
            'cache_raw'	: 0,                    #   /config's enabled_bands_raw	Bitmask for bands from which to capture and cache RAW (tiff) images.    
            'store_capture' : True,	            #   Store this image to the SD card based on configuration settings.
            'use_post_capture_state' : False	#   When 'true', the camera will try and retrieve state information from the /capture_state route before falling back on default values.        
        }        
        url = "http://" + self.CAM_HOST_IP + "/capture"

        print(" red Edge capture begins .......")
        retries = retry
        while retries >= 1:
            print(f"retry No. {(retry+1) - retries}")
            if (withCalibration == False):
                ret,capture_data = self.micaSensePost( url, capture_params )
            else:
                ret,capture_data = self.micaSensePost( url, capture_params, 3, True )            
            if (ret == 1):
                retries = -1
            else:
                if (self.reConnectWiFi()==1):
                    retries -= 1
                else:
                    print("failed to connect to wifi")
                    retries = -2
                    
        if (retries == -2):
            return 0,0
        else: 
            if not (capture_data == 0):        
                if (capture_data.status_code >= 200) and (capture_data.status_code <= 299) :
                    self.print_myJson( capture_data )
                else:
                    print("Capture Failed")
                return capture_data.status_code,capture_data   
            return 0,0
        
    # Get the RedEye camera capture status, block until complete
    #
    def redEyeCaptureStatus( self, id ):
       
        url = "http://" + self.CAM_HOST_IP + "/capture" + id
        
        capture_data = self.micaSenseGetNoRetry( url )
        if capture_data:
             self.print_myJson( capture_data )
        return capture_data.status_code,status_code 

    # Post a message to the RedEdge camera commanding a capture, block until complete
    #        
    def redEdgeCaptureStatusNoRetry( self, id ):

        url = "http://" + self.CAM_HOST_IP + "/capture" + id

        capture_data = self.micaSenseGetNoRetry( url )
        if capture_data:
            self.print_myJson( capture_data )
        return capture_data.status_code,capture_data 

    # Post a message to the RedEdge camera commanding a capture, block until complete
    #        
    def redEdgeCaptureStatus( self, id, retry=2 ):

        url = "http://" + self.CAM_HOST_IP + "/capture" + id

        print(" red Edge capture status")
        retries = retry
        while retries >= 1:
            print(f"retry No. {(retry+1) - retries}")
            ret,capture_data = self.micaSenseGet( url )
            if (ret == 1):
                retries = -1
            else:
                if (self.reConnectWiFi()==1):
                    retries -= 1
                else:
                    print("failed to connect to wifi")
                    retries = -2
                    
        if (retries == -2):
            return 0,0
        else:            
            if (capture_data.status_code >= 200) and (capture_data.status_code <= 299):
                self.print_myJson( capture_data )
            else:
                print("Capture Failed")
        return capture_data.status_code,capture_data         
        
    # Download KMZ File
    #
    def redEyeGetKMZ( self ):
           
        url = "http://" + self.CAM_HOST_IP + "/captures.kmz"
       
        print(f"getting {url}") 
        capture_data = self.micaSenseGetNoRetry( url )
        if ((capture_data.status_code >= 200) and (capture_data.status_code <=299)):
            print( capture_data.content )
            out = open("myKMZfile.kmz", 'wb')
            out.write(capture_data.content)
        return capture_data.status_code, capture_data

    # Download KMZ File
    #
    def redEdgeGetKMZ( self ):
           
        url = "http://" + self.CAM_HOST_IP + "/captures.kmz"
        
        print(f"getting {url}") 
        capture_data = self.micaSenseGetNoRetry( url )
        if ((capture_data.status_code >= 200) and (capture_data.status_code <=299)):
            print( capture_data.content )
            out = open("myKMZfile.kmz", 'wb')
            out.write(capture_data.content)
            out.close
        return capture_data.status_code, capture_data        

    # Parse the kmz file (xml stream) and print the placemark and co-ordinates
    #
    def micaSenseParseKmzData( self, capture_data ):
    
        placeMarkNameList = []
        placeMarkPointList = []
        root = ET.fromstring(capture_data)
        #for folder_name in root.iter('Folder'):
        for cnt in root.findall('Folder'):
            placeMarkName = cnt.find('name').text
            placeMarkPoint = cnt.find('coordinates').text
            print(" %s : co-ordinates %s\n" % (placeMarkName, placeMarkPoint))
            placeMarkNameList.append = placeMarkName
            placeMarkPointList.append = placeMarkPoint
        return placeMarkNameList, placeMarkPointList
        
    # open the KMZ XML File output from the camera
    #
    # tree = ET.parse('c:\\pg\mapData.kmz')
    # XML
    # root = tree.getroot()

    # Parse the kmz file (xml stream) and print the placemark and co-ordinates
    #
    def micaSenseParseKmzStream( self, capture_data ):
    
        root = ET.fromstring(capture_data)
        #for folder_name in root.iter('Folder'):
        for cnt in root.findall('Folder'):
            placeMarkName = cnt.find('name').text
            placeMarkPoint = cnt.find('coordinates').text
            print(" %s : co-ordinates %s\n" % (placeMarkName, placeMarkPoint))

    # to write XML back out from the root object
    #
    #tree = ET.ElementTree(root)
    #tree.write('c:\\pg\mapData.kmz', encoding="UTF-8")
 
    # Post a message to the camera setting exposure, block until complete 
    #
    def micaSenseSetExposure( self, e1, e2, e3, e4, e5, g1, g2, g3, g4, g5 ):
        exposure_params = { "enable_man_exposure" : False, 
                            "exposure1" : e1, 
                            "exposure2" : e2, 
                            "exposure3" : e3, 
                            "exposure4" : e4,
                            "exposure5" : e5,
                            "gain1" : g1,
                            "gain2" : g2,
                            "gain3" : g3,
                            "gain4" : g4,
                            "gain5" : g5,
                          }
        url = "http://" + self.CAM_HOST_IP + "/exposure"
        capture_data = self.micaSensePostNoRetry( url, exposure_params, True )
        return capture_data.status_code,capture_data 

    # Post a message to the camera setting exposure, block until complete 
    #
    def micaSenseSetExposureFromMav( self, mav_class ):
        exposure_params = { "enable_man_exposure" : False, 
                            "exposure1" : mav_class.set_mica_exposure.exp1, 
                            "exposure2" : mav_class.set_mica_exposure.exp2, 
                            "exposure3" : mav_class.set_mica_exposure.exp3, 
                            "exposure4" : mav_class.set_mica_exposure.exp4,
                            "exposure5" : mav_class.set_mica_exposure.exp5,
                            "gain1" : mav_class.set_mica_exposure.gain1,
                            "gain2" : mav_class.set_mica_exposure.gain2,
                            "gain3" : mav_class.set_mica_exposure.gain3,
                            "gain4" : mav_class.set_mica_exposure.gain4,
                            "gain5" : mav_class.set_mica_exposure.gain5,
                          }
        url = "http://" + self.CAM_HOST_IP + "/exposure"
        capture_data = self.micaSensePostNoRetry( url, exposure_params, True )
        return capture_data.status_code,capture_data 
        
    # Detect Panel On
    #
    def micaSenseDetectPanelOn( self ):
        dt_params = { "detect_panel" : True } 
        url = "http://" + self.CAM_HOST_IP + "/detect_panel"
        capture_data = self.micaSensePostNoRetry( url, dt_params, True )
        return capture_data.status_code,capture_data        

    # Detect Panel On
    #
    def micaSenseDetectPanelOff( self ):
        dt_params = { 
        'abort_detect_panel' : False,	# When 'true', any actively running panel detection captures will be forced to complete.
        'detect_panel'	: True          # When 'true', a panel detection capture is active"detect_panel" : True } 
        }
        url = "http://" + self.CAM_HOST_IP + "/detect_panel"
        capture_data = self.micaSensePostNoRetry( url, dt_params, True )
        return capture_data.status_code,capture_data 
   

    # set GPS
    #
    # import time (alternative)
    # named_tuple = time.localtime() # struct_time
    # time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
    #
    # timezone_london = pytz.timezone('Europe/London')
    # london_datetime_obj = nw_datetime_obj.astimezone(timezone_london)
    #
    def micaSenseSetGPS( self, lon, lat, alt, veln, vele, veld, pacc, vacc, fix3d=True ):
        ntp_sync_freq = ntp_sync_freq + 1
        if ((ntp_sync_freq >= self.NTP_SYNC_THRESHOLD) and ( self.NTP_TIME_SYNC_ENABLE >= 1)):
           self.ntp_time_sync()    
           time.sleep(1)
           ntp_sync_freq = 0
        dtime_utc = dt.datetime.now(pytz.utc)
        dt_params = { "latitude" : lat, "longitude" : lon, "altitude" : alt, "vel_n" : veln, "vel_e" : vele, "vel_d" : veld, "p_acc" : pacc, "v_acc" : vacc, "fix3d" : fix3d, utc_time : dtime_utc } 
        url = "http://" + self.CAM_HOST_IP + "/gps"
        capture_data = self.micaSensePostNoRetry( url, dt_params, True )
        return capture_data.status_code,capture_data 

    # get GPS
    #
    def micaSenseGetGPS( self ):

        url = "http://" + self.CAM_HOST_IP + "/gps"
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data
        

    # set orientation
    #
    def micaSenseSetOrientation( self, Aphi, Atheta, Apsi, Cphi, Ctheta, Cpsi ):
    
        orintation_params = { "aircraft_phi" : Aphi, "aircraft_theta" : Atheta, "aircraft_psi" : Apsi, "camera_phi" : Cphi, "camera_theta"	: Ctheta, "camera_psi" : Cpsi }
        url = "http://" + self.CAM_HOST_IP + "/orientation"
        capture_data = self.micaSensePostNoRetry( url, orintation_params, True )
        return capture_data.status_code,capture_data 

    # get Orientation
    #
    def micaSenseSetGPS( self ):

        url = "http://" + self.CAM_HOST_IP + "/orientation"
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data      

    # set picture state (redEdge Only)
    #
    def redEdgeSetState( self, Aphi, Atheta, Apsi, Cphi, Ctheta, Cpsi, lon, lat, alt, veln, vele, veld, pacc, vacc, fix3d=True ):
    
        pic_stat_params = { "aircraft_phi" : Aphi, "aircraft_theta" : Atheta, "aircraft_psi" : Apsi, "camera_phi" : Cphi, "camera_theta"	: Ctheta, "camera_psi" : Cpsi, "latitude" : lat, "longitude" : lon, "altitude" : alt, "vel_n" : veln, "vel_e" : vele, "vel_d" : veld, "p_acc" : pacc, "v_acc" : vacc, "fix3d" : fix3d, utc_time : dtime_utc }
        url = "http://" + self.CAM_HOST_IP + "/capture_state"
        capture_data = self.micaSensePostNoRetry( url, pic_stat_params, True )
        return capture_data.status_code,capture_data 
                
    # set configuration
    #
    def micaSenseSetConfig( self, streaming_enable=True, streaming_allowed = True, preview_band = "band1", operating_alt = 11, operating_alt_tolerance = 45, overlap_along_track = 11, overlap_cross_track = 5, auto_cap_mode = "overlap", timer_period = 1.2,ext_trigger_mode = "rising", pwm_trigger_threshold = 38.2,	enabled_bands_raw = 43,	enabled_bands_jpeg = 378,enable_man_exposure = True,gain_exposure_crossover = 87.65,	ip_address = "123.456.789.012", raw_format = "TIFF",network_mode = "main", ext_trigger_out_enable = False,	ext_trigger_out_pulse_high = False, agc_minimum_mean = 0.1,	audio_enable = True,audio_select_bitfield = 1,	injected_gps_delay = 9.1 ):
        config_params = {
        "streaming_enable" : streaming_enable,	
        "streaming_allowed"	: streaming_allowed, 
        "preview_band" : preview_band,
        "operating_alt" : operating_alt,
        "operating_alt_tolerance" : operating_alt_tolerance,
        "overlap_along_track" : overlap_along_track,
        "overlap_cross_track" : overlap_cross_track,
        "auto_cap_mode" : auto_cap_mode, 
        "timer_period" : timer_period,
        "ext_trigger_mode" : ext_trigger_mode, 
        "pwm_trigger_threshold" : pwm_trigger_threshold,	
        "enabled_bands_raw" : enabled_bands_raw,	
        "enabled_bands_jpeg" : enabled_bands_jpeg,
        "enable_man_exposure" : enable_man_exposure,
        "gain_exposure_crossover" : gain_exposure_crossover,	
        "ip_address" : ip_address,
        "raw_format" : raw_format,
        "network_mode" : network_mode, 
        "ext_trigger_out_enable" : ext_trigger_out_enable,	
        "ext_trigger_out_pulse_high" : ext_trigger_out_pulse_high, 
        "agc_minimum_mean" : agc_minimum_mean,	
        "audio_enable" : audio_enable,
        "audio_select_bitfield" : audio_select_bitfield,	
        "injected_gps_delay" : injected_gps_delay,
        }
        url = "http://" + self.CAM_HOST_IP + "/config"
        capture_data = self.micaSensePostNoRetry( url, orintation_params, True )
        return capture_data.status_code,capture_data 

    # Post a message to the camera getting the exposure parameters, block until complete 
    #
    def micaSenseGetExposure( self ):
        url = "http://" + self.CAM_HOST_IP + "/exposure"
        capture_data = self.micaSenseGetNoRetry( url )        
        return capture_data
        
    # get pins
    #
    def micaSenseGetPinMux( self ):

        url = "http://" + self.CAM_HOST_IP + "/pin_mux"
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data

    # get status
    #
    def micaSenseGetStatus( self ):

        url = "http://" + self.CAM_HOST_IP + "/status"
        capture_data = self.micaSenseGetNoRetry( url )
        #drive_gigaByte_Free = capture_data.json()['sd_gb_free']
        #drive_gigaByte_Total = capture_data.json()['sd_gb_total']
        #drive_WarningNearFull = capture_data.json()['sd_warn']
        return capture_data #, drive_gigaByte_Free, drive_gigaByte_Total, drive_WarningNearFull

    # get status
    #
    def micaSenseGetNetworkStatus( self ):

        url = "http://" + self.CAM_HOST_IP + "/networkstatus"
        capture_data = self.micaSenseGetNoRetry( url )
        #drive_gigaByte_Free = capture_data.json()['sd_gb_free']
        #drive_gigaByte_Total = capture_data.json()['sd_gb_total']
        #drive_WarningNearFull = capture_data.json()['sd_warn']
        return capture_data #, drive_gigaByte_Free, drive_gigaByte_Total, drive_WarningNearFull
        
    # get status
    #
    def micaSenseGetTimeSources( self ):

        url = "http://" + self.CAM_HOST_IP + "/timesources"
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data
        
    # get time sources 
    #
    def micaSenseGetVersion( self ):

        url = "http://" + self.CAM_HOST_IP + "/version"
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data
        
    # get files
    #
    def micaSenseGetFiles( self ):

        #url = "http://" + self.CAM_HOST_IP + "/files/*"
        url = "http://" + self.CAM_HOST_IP + "/files/018SET/000/"
        #url = "http://" + self.CAM_HOST_IP + "/files/0018SET/000/IMG_0011_3.tif"
        capture_data = self.micaSenseGetNoRetry( url )
        print(f" stat {capture_data.status_code}")
        return capture_data

    # delete files (uses GET method)
    #
    def micaSenseDelFiles( self ):

        url = "http://" + self.CAM_HOST_IP + "/deletefile/*"
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data

    # delete files (uses GET method)
    #
    def micaSenseDelFile( self, fileDirs, fullFileNam ):

        url = "http://" + self.CAM_HOST_IP + "/deletefile/" + fileDirs + "/" + fullFileNam
        # or /deletefile/0000SET/000 or /deletefile/0001SET/000/IMG_1234_1.tif
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data

    # set wifi
    #
    def micaSenseSetWiFi( self ):
    
        wifi_params = { "enable" : True }
        url = "http://" + self.CAM_HOST_IP + "/wifi"
        capture_data = self.micaSensePostNoRetry( url, wifi_params, True )
        return capture_data.status_code,status_code 

    # reformat SD card 
    #
    def micaSenseReformatSDCard( self ):
    
        sd_params = { "erase_all_data" : True } 
        url = "http://" + self.CAM_HOST_IP + "/reformatsdcard"
        capture_data = self.micaSensePostNoRetry( url, sd_params, True )
        print(f"Reformat gave .... {capture_data.status_code}")
        return capture_data.status_code,capture_data

    # get information
    #
    def micaSenseGetInfo( self ):

        url = "http://" + self.CAM_HOST_IP + "/camera_info"
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data       

    # get Calibration Distortion
    #
    def micaSenseGetCaliDistortion( self ):

        url = "http://" + self.CAM_HOST_IP + "/calibration/distortion"
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data  
        
    # get Vignette Calibration 
    #
    def micaSenseGetVignetteCali( self ):

        url = "http://" + self.CAM_HOST_IP + "/calibration/vignette"
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data 
        
    # get Rig Relatives Calibration 
    #
    def micaSenseGetRigRelCali( self ):

        url = "http://" + self.CAM_HOST_IP + "/calibration/rig_relatives"
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data 

    # Prepare for Power Down 
    #
    def micaSensePreparePowerDwn( self ):
    
        po_params = { "ready_for_power_down" : True, "power_down" : False }  
        url = "http://" + self.CAM_HOST_IP + "/powerdownready"
        capture_data = self.micaSensePostNoRetry( url, po_params, True )
        return capture_data.status_code, capture_data

    # Power Down Ready
    #
    def micaSensePowerDwnRdy( self ):
    
        po_params = { "ready_for_power_down" : False, "power_down" : True }   
        url = "http://" + self.CAM_HOST_IP + "/powerdownready"
        capture_data = self.micaSensePostNoRetry( url, po_params, True )
        return capture_data.status_code, capture_data

    # get Power Down Status 
    #
    def micaSenseGetPowerDwnStatus( self ):

        url = "http://" + self.CAM_HOST_IP + "/powerdownready"
        capture_data = self.micaSenseGetNoRetry( url )
        return capture_data 

    # Thermal NUC
    #
    def micaSenseThermalNUC( self ):
    
        nuc_params = { "nuc_now" : True, "elapsed_seconds_since_nuc" : 10, "delta_deg_K_since_nuc" : -0.2, "message" : "NUC request failed" }    
        url = "http://" + self.CAM_HOST_IP + "/thermal_nuc"
        capture_data = self.micaSensePostNoRetry( url, nuc_params, True )
        return capture_data.status_code,status_code 

    def getDiskFree( self ):
        myOs = self.check_os()
        if (myOs == 1):
            cmd = "/bin/df"
            x = os.popen(cmd, 'r')
            for line in x:
                if not line.find("root") == -1:
                    x = line.split()
            y = x[4].split("%")
            print(f"disk usage percent {y[0]}")
            return y[0]
        else: # no support currently
            return 100

    # Take a picture and wait for completion status then save them to you're hard drive.
    # 
    def redEdgeCaptureFivePictures( self, calibON=False ):

        if (calibON == False):
            stat, jso = self.redEdgeCapture()
        else:
            stat, jso = self.redEdgeCapture( 3, True )
        if (stat >= 200) and (stat <= 299):
            print("in function >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            jsonStat = jso.json()
            statTxt = jsonStat['status']
            if ((calibON == True) and not (statTxt.find("complete") == -1)):
                print("Calibration Completed")
                return 2
            id = jsonStat['id']
            loop_timeout = 3
            while ((statTxt.find("complete") == -1) and (loop_timeout >= 0)) :
                print(f"doing {jsonStat['id']}")
                stat, js = self.redEdgeCaptureStatus( jsonStat['id'] )
                if (stat >= 200) and (stat <= 299):
                    statusOut = js.json()
                    statTxt = statusOut['status']
                elif not (stat == 0):
                    print(f"stat returned was {stat}")
                    statusOut = js.json()
                    print(statusOut) 
                    statTxt = statusOut['status']
                else:
                    print("invalid stat was returned !!!")
                loop_timeout -= 1
                print(f"status returned was {statTxt} stat is {stat}")
            if (loop_timeout <= 0):
                print("------- request failed on timeout---------")
                return -1
            elif not ((stat >= 200) and (stat <= 299)):
                print(f"------- returned a stat of {stat} ------")
                return -2
            picDef = statusOut['raw_cache_path']
            print(f" time = {statusOut['time']}")
            piclabels = [ 1,2,3,4,5 ]
            i = 1
            timeTag = statusOut['time'].split()
            for i in range(len(piclabels)):
                index = str(piclabels[int(i)])
                pdef = picDef[index]
                print(f"image {i} : {index}")
                url = "http://" + self.CAM_HOST_IP + "/" + pdef
                #outFileName = "imgMicaCam_" + str(id) + "_" + index + "_" + timeTag[0] + ".tiff"
                outFileName = "imgMicaCam_" + str(id) + "_" + index + ".tiff"
                dataGot = requests.get(url)
                if (dataGot.status_code >= 200) and (dataGot.status_code <= 299):
                    out = open(outFileName, 'wb')
                    out.write(dataGot.content)
                    out.close
                    if (i == 1):                                         # blue_img
                        image = cv2.imread(outFileName)
                        #image = cv2.imread("im1.png")
                        #image=np.array(np.rot90(image,-1))
                        #image = image.copy()
                        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        #blue_img,g,r = cv2.split(image)
                        blue_img = np.array(image)
                        blue_img = np.array(blue_img)
                        blue_img = blue_img.copy()
                        #blue_img = dataGot.content
                    elif (i == 2):                                        # green 
                        image = cv2.imread(outFileName)
                        #image = cv2.imread("im1.png")
                        #image=np.array(np.rot90(image,-1))
                        #image = image.copy()
                        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        #b,green_img,r = cv2.split(image)
                        green_img = np.array(image)
                        green_img = np.array(green_img)
                        green_img = green_img.copy()
                        #green_img = dataGot.content
                    elif (i == 3):                                        # red
                        image = cv2.imread(outFileName)
                        #image = cv2.imread("im1.png")
                        #image=np.array(np.rot90(image,-1))
                        #image = image.copy()
                        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        #b,g,red_img = cv2.split(image)
                        red_img = np.array(image)
                        red_img = np.array(red_img)
                        red_img = red_img.copy()
                        #red_img = dataGot.content
                        merge_image = cv2.merge([green_img,blue_img,red_img])
                        #cv2.imwrite('image.png',merge_image)
                        out = open("mergedFile.tiff", 'wb')
                        out.write(merge_image)
                        out.close 
            return 1
        else:
            print("====== error ========")
            return -1	
# ===============================================================================================================================
#
# Name : NewSonyAlphaClass.py
# Desc : Communicate with new Sony Alpha Series of Camera
# Auth : AIR-obots Ai-Robots
#
# ===============================================================================================================================

class sonyAlphaNewCamera():

    def __init__ (self, name = 'sonyAlphaCamClass'):
        """this class is for communicating with the new range of sony alpha cameras."""
        self.name = name                                                                   # name as a string
        self.error_counts = multiprocessing.Value('i', 0)
        
    def __del__(self): 
        """ deletes the class """    
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

    def take_a_picture_now( self, flag ):

        # run the API command in the shell and look for the descriptor for the field
        #
        if (flag == 1):
           cmd='/home/pi/cams/SonyTEST32/take_picture/RemoteCli ' 
           c = os.popen(cmd)
           print(c.read())
           flag = 2
           # fastGlobals.take_picture = 2
           print(f"\033[36m Took the picture {flag}")
        return flag
        
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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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

        # CONSIDER :: because we have to trap various errors and act on them we had to parse the output for other things i might modify CameraDevice.cpp to
        # cover it all and exit as quick as possible using return codes but i couldnt succeed to read them all successfully using .returncode property
        # with the pipe attached as above and we dont want too many delays
        #
        s=subprocess.run( args, stdout=subprocess.PIPE )
        output=s.stdout
        #s.stdout.close()
              
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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
        if  ( not(z.find("No cameras detected") == -1) or not(z.find("Failed to get") == -1)):            
            self.error_counts.value += 1
            print(f"\033[31m Error Reading from Camera USB Link {self.error_counts.value} \033[0m")
            return answers

        # look for the not writable option
        #
        if not(z.find("not writable") == -1):
            print("\033[31m This option is not writable \033[0m ")
            answers.append(-1) 
            answers.append(-1) 
            answers.append(0) 
            answers.append("CAN_NOT_WRITE") 
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
        
    def set_sony_aperture_orig( self, Val ):

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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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

    def set_sony_aperture( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_aperture/RemoteCli ' + ValArg
        args = shlex.split(cmd)

        # CONSIDER :: because we have to trap various errors and act on them we had to parse the output for other things i might modify CameraDevice.cpp to
        # cover it all and exit as quick as possible using return codes but i couldnt succeed to read them all successfully using .returncode property
        # with the pipe attached as above and we dont want too many delays
        #
        s=subprocess.run( args, stdout=subprocess.PIPE )
        output=s.stdout
        #s.stdout.close()
              
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []

        # new error handler sends a unique reply which means count these errors and then force a reset of the usb
        #
        if  ( not(z.find("No cameras detected") == -1) or not(z.find("Failed to get") == -1)):            
            self.error_counts.value += 1
            print(f"\033[31m Error Reading from Camera USB Link {self.error_counts.value} \033[0m")
            return answers

        # look for the not writable option
        #
        if not(z.find("not writable") == -1):
            print("\033[31m This option is not writable \033[0m ")
            answers.append(-1) 
            answers.append(-1) 
            answers.append(0) 
            answers.append("CAN_NOT_WRITE") 
            return answers
            
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
        
    def set_sony_ex_pro_orig( self, Val ):

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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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

    def set_sony_ex_pro( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_ex_pro/RemoteCli ' + ValArg
        args = shlex.split(cmd)

        # CONSIDER :: because we have to trap various errors and act on them we had to parse the output for other things i might modify CameraDevice.cpp to
        # cover it all and exit as quick as possible using return codes but i couldnt succeed to read them all successfully using .returncode property
        # with the pipe attached as above and we dont want too many delays
        #
        s=subprocess.run( args, stdout=subprocess.PIPE )
        output=s.stdout
        #s.stdout.close()
              
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []

        # new error handler sends a unique reply which means count these errors and then force a reset of the usb
        #
        if  ( not(z.find("No cameras detected") == -1) or not(z.find("Failed to get") == -1)):            
            self.error_counts.value += 1
            print(f"\033[31m Error Reading from Camera USB Link {self.error_counts.value} \033[0m")
            return answers

        # look for the not writable option
        #
        if not(z.find("not writable") == -1):
            print("\033[31m This option is not writable \033[0m ")
            answers.append(-1) 
            answers.append(-1) 
            answers.append(0) 
            answers.append("CAN_NOT_WRITE") 
            return answers
            
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
        
    def set_sony_focus_orig( self, Val ):

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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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

    def set_sony_focus( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_focus/RemoteCli ' + ValArg
        args = shlex.split(cmd)

        # CONSIDER :: because we have to trap various errors and act on them we had to parse the output for other things i might modify CameraDevice.cpp to
        # cover it all and exit as quick as possible using return codes but i couldnt succeed to read them all successfully using .returncode property
        # with the pipe attached as above and we dont want too many delays
        #
        s=subprocess.run( args, stdout=subprocess.PIPE )
        output=s.stdout
        #s.stdout.close()
              
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []

        # new error handler sends a unique reply which means count these errors and then force a reset of the usb
        #
        if  ( not(z.find("No cameras detected") == -1) or not(z.find("Failed to get") == -1)):            
            self.error_counts.value += 1
            print(f"\033[31m Error Reading from Camera USB Link {self.error_counts.value} \033[0m")
            return answers

        # look for the not writable option
        #
        if not(z.find("not writable") == -1):
            print("\033[31m This option is not writable \033[0m ")
            answers.append(-1) 
            answers.append(-1) 
            answers.append(0) 
            answers.append("CAN_NOT_WRITE") 
            return answers
            
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
        
    def set_sony_focus_area_orig( self, Val ):

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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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

    def set_sony_focus_area( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_fa/RemoteCli ' + ValArg
        args = shlex.split(cmd)

        # CONSIDER :: because we have to trap various errors and act on them we had to parse the output for other things i might modify CameraDevice.cpp to
        # cover it all and exit as quick as possible using return codes but i couldnt succeed to read them all successfully using .returncode property
        # with the pipe attached as above and we dont want too many delays
        #
        s=subprocess.run( args, stdout=subprocess.PIPE )
        output=s.stdout
        #s.stdout.close()
              
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []

        # new error handler sends a unique reply which means count these errors and then force a reset of the usb
        #
        if  ( not(z.find("No cameras detected") == -1) or not(z.find("Failed to get") == -1)):            
            self.error_counts.value += 1
            print(f"\033[31m Error Reading from Camera USB Link {self.error_counts.value} \033[0m")
            return answers

        # look for the not writable option
        #
        if not(z.find("not writable") == -1):
            print("\033[31m This option is not writable \033[0m ")
            answers.append(-1) 
            answers.append(-1) 
            answers.append(0) 
            answers.append("CAN_NOT_WRITE") 
            return answers
            
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
        
    def set_sony_shutter_orig( self, Val ):

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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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

    def set_sony_shutter( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_shutter/RemoteCli ' + ValArg
        args = shlex.split(cmd)

        # CONSIDER :: because we have to trap various errors and act on them we had to parse the output for other things i might modify CameraDevice.cpp to
        # cover it all and exit as quick as possible using return codes but i couldnt succeed to read them all successfully using .returncode property
        # with the pipe attached as above and we dont want too many delays
        #
        s=subprocess.run( args, stdout=subprocess.PIPE )
        output=s.stdout
        #s.stdout.close()
              
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
        zz = z.replace("\"","")            # get rid of the inch symbol it will crash us
        a = shlex.split(zz)                # split this unique output into fields separated by commas
       
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []

        # new error handler sends a unique reply which means count these errors and then force a reset of the usb
        #
        if  ( not(z.find("No cameras detected") == -1) or not(z.find("Failed to get") == -1)):            
            self.error_counts.value += 1
            print(f"\033[31m Error Reading from Camera USB Link {self.error_counts.value} \033[0m")
            return answers

        # look for the not writable option
        #
        if not(z.find("not writable") == -1):
            print("\033[31m This option is not writable \033[0m ")
            answers.append(-1) 
            answers.append(-1) 
            answers.append(0) 
            answers.append("CAN_NOT_WRITE") 
            return answers
            
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
        print(answers)
        return answers
        
    def set_sony_white_bal_orig( self, Val ):

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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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

    def set_sony_white_bal( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_wb/RemoteCli ' + ValArg
        args = shlex.split(cmd)

        # CONSIDER :: because we have to trap various errors and act on them we had to parse the output for other things i might modify CameraDevice.cpp to
        # cover it all and exit as quick as possible using return codes but i couldnt succeed to read them all successfully using .returncode property
        # with the pipe attached as above and we dont want too many delays
        #
        s=subprocess.run( args, stdout=subprocess.PIPE )
        output=s.stdout
        #s.stdout.close()
              
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []

        # new error handler sends a unique reply which means count these errors and then force a reset of the usb
        #
        if  ( not(z.find("No cameras detected") == -1) or not(z.find("Failed to get") == -1)):            
            self.error_counts.value += 1
            print(f"\033[31m Error Reading from Camera USB Link {self.error_counts.value} \033[0m")
            return answers

        # look for the not writable option
        #
        if not(z.find("not writable") == -1):
            print("\033[31m This option is not writable \033[0m ")
            answers.append(-1) 
            answers.append(-1) 
            answers.append(0) 
            answers.append("CAN_NOT_WRITE") 
            return answers
            
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

    def set_sony_still_cap_orig( self, Val ):

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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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

    def set_sony_still_cap( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_still_cap/RemoteCli ' + ValArg
        args = shlex.split(cmd)

        # CONSIDER :: because we have to trap various errors and act on them we had to parse the output for other things i might modify CameraDevice.cpp to
        # cover it all and exit as quick as possible using return codes but i couldnt succeed to read them all successfully using .returncode property
        # with the pipe attached as above and we dont want too many delays
        #
        s=subprocess.run( args, stdout=subprocess.PIPE )
        output=s.stdout
        #s.stdout.close()
              
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 99999
        answers = []

        # new error handler sends a unique reply which means count these errors and then force a reset of the usb
        #
        if  ( not(z.find("No cameras detected") == -1) or not(z.find("Failed to get") == -1)):            
            self.error_counts.value += 1
            print(f"\033[31m Error Reading from Camera USB Link {self.error_counts.value} \033[0m")
            return answers

        # look for the not writable option
        #
        if not(z.find("not writable") == -1):
            print("\033[31m This option is not writable \033[0m ")
            answers.append(-1) 
            answers.append(-1) 
            answers.append(0) 
            answers.append("CAN_NOT_WRITE") 
            return answers
            
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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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
        
        z = output.decode('utf-8')         # convert bytes array output to utf-8 string 
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

    def initCamChoiceData( self ):
    
        ans = 0                                                       # consider reading this from xml.tree
        if (ans is not None):
            print(f" Camera Choice = {ans}")
            try:
                SonyObject = memoryValue('CAMERA_CHOICE', ans)
                with SonyObject.updateNeeded.get_lock():
                    SonyObject.updateNeeded.value = True 
            except Exception as err_msg:
                print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
                SonyObject = memoryValue('CAMERA_CHOICE', 0)              
        else:
            print("\033[31m Cant get Camera Choice Mode \033[0m")
            SonyObject = memoryValue('CAMERA_CHOICE', 0)

        SonyObject.index = memoryValue.numberOfVals 
        print(f"Camera Choice : created object number : {SonyObject.index}")
        return SonyObject
        
    def initSonyCamExProData( self ):
    
        ans = self.get_sony_ex_pro( )
        if not (ans is None):
            if (len(ans) > 0):
                print(f" Exposure Prog Mode = {ans}")
                try:
                    SonyObject = memoryValue('CAM_EXPMODE',int(ans[0]))
                    with SonyObject.updateNeeded.get_lock():
                        SonyObject.updateNeeded.value = True 
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('CAM_EXPMODE',0) 
            else:
                print("\033[31m Failed get the camera ExPro \033[0m")
                SonyObject = memoryValue('CAM_EXPMODE',0)             
        else:
            print("\033[31m Cant get Exposure Prog Mode \033[0m")
            SonyObject = memoryValue('CAM_EXPMODE',0)

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
                    SonyObject = memoryValue('CAM_APERTURE',int(ans[0]))
                    with SonyObject.updateNeeded.get_lock():
                        SonyObject.updateNeeded.value = True 
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('CAM_APERTURE',0) 
            else:
                print("\033[31m Failed get the camera aperture \033[0m")
                SonyObject = memoryValue('CAM_APERTURE',0)  
        else:
            print("\033[31m Cant get Aperture \033[0m")
            SonyObject = memoryValue('CAM_APERTURE',0)  

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
                    with SonyObject.updateNeeded.get_lock():
                        SonyObject.updateNeeded.value = True  
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
                    with SonyObject.updateNeeded.get_lock():
                        SonyObject.updateNeeded.value = True  
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
                    SonyObject = memoryValue('CAM_ISO',int(ans[0]))
                    with SonyObject.updateNeeded.get_lock():
                        SonyObject.updateNeeded.value = True  
                except Exception as err_msg:
                    print("\033[31m Failed set the iso object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('CAM_ISO',0) 
            else:
                print("\033[31m Failed get the camera iso \033[0m")
                SonyObject = memoryValue('CAM_ISO',0) 
        else:
            print("\033[31m Cant get ISO \033[0m")
            SonyObject = memoryValue('CAM_ISO',0) 

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
                    SonyObject = memoryValue('CAM_SHUTTERSPD',int(ans[0]))
                    with SonyObject.updateNeeded.get_lock():
                        SonyObject.updateNeeded.value = True  
                except Exception as err_msg:
                    print("\033[31m Failed set the shut spd object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('CAM_SHUTTERSPD',0) 
            else:
                print("\033[31m Failed get the camera shutter speed \033[0m")
                SonyObject = memoryValue('CAM_SHUTTERSPD',0) 
        else:
            print("\033[31m Cant get Shutter Speed \033[0m")
            SonyObject = memoryValue('CAM_SHUTTERSPD',0)
            
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
                    SonyObject = memoryValue('CAM_WBMODE',int(ans[0]))
                    with SonyObject.updateNeeded.get_lock():
                        SonyObject.updateNeeded.value = True  
                except Exception as err_msg:
                    print("\033[31m Failed set the object to initial value : %s \033[0m" % (err_msg))
                    SonyObject = memoryValue('CAM_WBMODE',0) 
            else:
                print("\033[31m Failed get the camera white balance \033[0m")
                SonyObject = memoryValue('CAM_WBMODE',0)         
        else:
            print("\033[31m Cant get Shutter Speed \033[0m")
            SonyObject = memoryValue('CAM_WBMODE',0)    

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
                    with SonyObject.updateNeeded.get_lock():
                        SonyObject.updateNeeded.value = True  
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
        elif num == 524291:
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

    # Only works in movie mode
    #
    def enumerate_ex_pro_sony_a7( self, num ):

        enum_num = 0
        enum_num_state = True
        if num == 32850:
            enum_num = 2
        elif num == 32848:
            enum_num = 0
        elif num == 32849:
            enum_num = 1
        elif num == 32851:
            enum_num = 3
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

    # To enable this ensure physical switch has been set to AUTO on the Lens
    # seemed to give a different subset of options list of 4 or 5 solved in camera "c++"
    #
    def enumerate_focus_sony_a7( self, num ):

        enum_num = 0
        enum_num_state = True
        if num == 2:
            enum_num = 0
        elif num == 4:
            enum_num = 1
        elif num == 3:
            enum_num = 2
        elif num == 6:
            enum_num = 3
        elif num == 1:
            enum_num = 4
        else:
            enum_num_state = False
        return enum_num_state, enum_num
        
    # after testing can this sometimes under certain circustances change by one ??
    # Bulb 0 = 0 - This has been done in the camera "C++"
    #
    def enumerate_shutter_sony_a7( self, num ):

        enum_num = 0
        enum_num_state = True
        # this occurs under certain conditions
        # then they all shift down by one 
        #
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

        # READ_TRIGGER (0)
        while (readSuccess == False) and (timeoutS1 > 0):
            reqDat, prevDat, readSuccess  = mavObj.getVal_sony_iso(mavObj.STATE_CAM_READING,timeout1)
            timeoutS1 -= timeout1                                          # no retries
            print(f"In iterator {readSuccess} {reqDat} {prevDat}")
            
        print(f"set to ISO r={reqDat} p={prevDat} time={timeout1} state={mavObj.state.value}")
        
        # LOOK FOR CHANGE (1)
        if ((not (int(reqDat) == mavlinkSonyCamWriteVals.STATE_INIT) and not (int(reqDat) == int(prevDat))) and (readSuccess == True)):
            timeoutS2 = timeout2 * no_timeout2_retry
            ret,ee = self.enumerate_iso_sony_a7(int(reqDat))
            # INVALID CHANGE MADE (return to state == 0)
            if (ret == False):
                print(f"\033[31m Error Invalid parameter Iso {reqDat}\033[0m")
                writeSuccess = False
                while (writeSuccess == False) and (timeoutS2 > 0): 
                    writeSuccess = mavObj.setVal_sony_iso( int(prevDat),mavObj.STATE_CAM_WRITING,mavObj.DONT_WRITE_PREV_DATA,timeout2 ) 
                    timeoutS2 -= timeout2                                  # no retries  
                return writeSuccess
            print(f"enumeration value for iso {ee} req {reqDat}")
            # MAKE CHANGE CAMERA RANK1 
            ans = self.set_sony_iso( ee )                                            ### MPI_Modification ::: will have to set a GLOBAL_STATE which is used as state machine
                                                                                     ###                      this has to wait for MPI on other rank at this point
                                                                                     ###                      when rank replies we do below.                                                                                     
            # SEND_MPI_TO_RANK1 (5)
            # DO ACTION IN RANK1 (6)
            # READ MPI_REPLY FROM RANK1 (7)
            
            # PROCESS RANK1_REPLY (8)
            if not (ans is None):   
                writeSuccess = False 
                wpWrite = False                
                if (len(ans)==0):
                    print("setting iso the length of command return was zero")
                    return ret 
                if (len(ans)==4):                                                                          # thats what we return for a non-writable value
                    if not (ans[3].find("CAN_NOT_WRITE") == -1):                                           # if we get that we cant write it, we reset the request
                        writeSuccess = mavObj.clearReq_sony_iso( mavObj.STATE_CAM_WRITING )
                        while wpWrite == False:
                            wpWrite = mavObj.set_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_ISO )
                        return writeSuccessWriPro_ISO
                print(f" \033[32m set the ISO from/to :: {ans} \033[0m")                       
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_iso( int(ans[1]), mavObj.STATE_CAM_WRITING, mavObj.WRITE_PREV_DATA,timeout2 ) 
                            timeoutS2 -= timeout2                                  # no retries  
                            print(f" write {writeSuccess}")
                    else:
                        print(f" what wat {ans[1]}=={reqDat}")
                except Exception as err_msg:                
                   print("\033[31m write sony iso failed to set iso \033[0m")                    
                if ( writeSuccess == True ):
                    while wpWrite == False:
                        wpWrite = mavObj.clear_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_ISO )
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
                writeSuccess = False
                wpWrite = False  
                if (len(ans)==0):
                    print("length of command return was zero")
                    return ret       
                if (len(ans)==4):                                                                          # thats what we return for a non-writable value
                    if not (ans[3].find("CAN_NOT_WRITE") == -1):                                           # if we get that we cant write it, we reset the request
                        writeSuccess = mavObj.clearReq_sony_aperture( mavObj.STATE_CAM_WRITING )
                        while wpWrite == False:
                            wpWrite = mavObj.set_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_APER )
                        return writeSuccess
                print(f" \033[32m set the Aperture from/to :: {ans} \033[0m")                           # 
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_aperture(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony aperture failed to set aperture \033[0m")                     
                if ( writeSuccess == True ):
                    while wpWrite == False:
                        wpWrite = mavObj.clear_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_APER )
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
                writeSuccess = False       
                wpWrite = False                  
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret   
                if (len(ans)==4):                                                                          # thats what we return for a non-writable value
                    if not (ans[3].find("CAN_NOT_WRITE") == -1):                                           # if we get that we cant write it, we reset the request
                        writeSuccess = mavObj.clearReq_sony_ex_pro( mavObj.STATE_CAM_WRITING )
                        while wpWrite == False:
                            wpWrite = mavObj.set_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_EX_PRO ) 
                        return writeSuccess                    # 
                print(f" \033[32m set the ex=Pro from/to :: {ans} \033[0m")  
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_ex_pro(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony expro failed to set expro \033[0m")                    
                if ( writeSuccess == True ):
                    while wpWrite == False:
                        wpWrite = mavObj.clear_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_EX_PRO )
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
                writeSuccess = False
                wpWrite = False   
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret             # 
                if (len(ans)==4):                                                                          # thats what we return for a non-writable value
                    if not (ans[3].find("CAN_NOT_WRITE") == -1):                                           # if we get that we cant write it, we reset the request
                        writeSuccess = mavObj.clearReq_sony_focus( mavObj.STATE_CAM_WRITING )
                        while wpWrite == False:
                            wpWrite = mavObj.set_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_FOCUS  ) 
                        return writeSuccess     
                print(f" \033[32m set the focus mode from/to :: {ans} \033[0m")   
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_focus(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony focus mode failed to set focus mode \033[0m")                    
                if ( writeSuccess == True ):
                    while wpWrite == False:
                        wpWrite = mavObj.clear_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_FOCUS  )
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
                writeSuccess = False       
                wpWrite = False                 
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret             # 
                if (len(ans)==4):                                                                          # thats what we return for a non-writable value
                    if not (ans[3].find("CAN_NOT_WRITE") == -1):                                           # if we get that we cant write it, we reset the request
                        writeSuccess = mavObj.clearReq_sony_focus_area( mavObj.STATE_CAM_WRITING )
                        while wpWrite == False:
                            wpWrite = mavObj.set_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_FOCUSA  ) 
                        return writeSuccess  
                print(f" \033[32m set the focus area from/to :: {ans} \033[0m")   
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_focus_area(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony focus area failed to set focus area \033[0m")                    
                if ( writeSuccess == True ):
                    while wpWrite == False:
                        wpWrite = mavObj.clear_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_FOCUSA  )
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
            
        print(f"set to Shutter Speed r={reqDat} p={prevDat} time={timeout1} state={mavObj.state.value}")
        
        if ((not (int(reqDat) == mavObj.STATE_INIT) and not (int(reqDat) == int(prevDat))) and (readSuccess == True)):
            timeoutS2 = timeout2 * no_timeout2_retry
            ret,ee = self.enumerate_shutter_sony_a7(int(reqDat))
            if (ret == False):
                print(f"\033[31m Error Invalid parameter shutter speed {reqDat}\033[0m")
                writeSuccess = False
                while (writeSuccess == False) and (timeoutS2 > 0): 
                    writeSuccess = mavObj.setVal_sony_shutter(int(prevDat),mavObj.STATE_CAM_WRITING,mavObj.DONT_WRITE_PREV_DATA,timeout2) 
                    #while wpWrite == False:
                    #    wpWrite = set_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_SS  ) 
                    timeoutS2 -= timeout2                                  # no retries  
                return writeSuccess 
            ans = self.set_sony_shutter( ee ) 
            if not (ans is None): 
                writeSuccess = False
                wpWrite = False 
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret             # 
                if (len(ans)==4):                                                                          # thats what we return for a non-writable value
                    if not (ans[3].find("CAN_NOT_WRITE") == -1):                                           # if we get that we cant write it, we reset the request
                        writeSuccess = mavObj.clearReq_sony_shutter( mavObj.STATE_CAM_WRITING )
                        while wpWrite == False:
                            wpWrite = mavObj.set_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_SS  ) 
                        return writeSuccess  
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
                    while wpWrite == False:
                        wpWrite = mavObj.clear_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_SS  )                    
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
                writeSuccess = False   
                wpWrite = False                 
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret             # 
                if (len(ans)==4):                                                                          # thats what we return for a non-writable value
                    if not (ans[3].find("CAN_NOT_WRITE") == -1):                                           # if we get that we cant write it, we reset the request
                        writeSuccess = mavObj.clearReq_sony_white_bal( mavObj.STATE_CAM_WRITING )
                        while wpWrite == False:
                            wpWrite = mavObj.set_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_WB  ) 
                        return writeSuccess  
                print(f" \033[32m set the white balance from/to :: {ans} \033[0m")   
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_white_bal(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony white balance failed to set white balance \033[0m")                    
                if ( writeSuccess == True ):
                    while wpWrite == False:
                        wpWrite = mavObj.clear_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_WB  ) 
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
                writeSuccess = False
                wpWrite = False 
                if (len(ans)==0):
                    print("\033[31m length of command return was zero \033[0m")
                    return ret             # 
                if (len(ans)==4):                                                                          # thats what we return for a non-writable value
                    if not (ans[3].find("CAN_NOT_WRITE") == -1):                                           # if we get that we cant write it, we reset the request
                        writeSuccess = mavObj.clearReq_sony_still_cap_mode( mavObj.STATE_CAM_WRITING )
                        while wpWrite == False:
                            wpWrite = mavObj.set_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_SC  ) 
                        return writeSuccess  
                print(f" \033[32m set the still capture mode from/to :: {ans} \033[0m")   
                try:
                    if ( int(ans[1]) == int(reqDat) ) :
                        while (writeSuccess == False) and (timeoutS2 > 0): 
                            writeSuccess = mavObj.setVal_sony_still_cap_mode(ans[1],mavObj.STATE_CAM_WRITING,mavObj.WRITE_PREV_DATA,timeout2) 
                            timeoutS2 -= timeout2                                  # no retries  
                except Exception as err_msg:                
                   print("\033[31m write sony still capture mode failed to set still capture mode \033[0m")                    
                if ( writeSuccess == True ):
                    while wpWrite == False:
                        wpWrite = mavObj.clear_WritePro( mavObj.STATE_CAM_WRITING, mavObj.WriPro_SC  ) 
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

        if (obj.updateNeeded.value == True):
        
            # send mavlink message  obj.name obj.signal.value obj.numberOfVals      
            #
            getName, getValueforMAVSending, getPrev, myState = obj.get_value_data(obj.STATE_MAV_READING, Timeout) 
            print(f"-------------- obj update found for param_value {getName} {getValueforMAVSending} {getPrev} {myState}")
            sendVal = struct.unpack('f', struct.pack('I', getValueforMAVSending))[0]  
            if (myState == True):
                try:
                    the_connection.mav.param_value_send(
                        getName.encode('utf-8'),
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
                        # obj.updateNeeded.value = False
                        writeSuccess = obj.set_update_flag( False, obj.STATE_MAV_WRITING )
                        TimeCount += 1
                return ret

    #
    # would go into mavlink class if it was in multi-tasking mode
    #
    def sendMavlinkMessageForParamExtObject( self, obj, the_connection, Timeout=5 ):

        v, r = obj.get_ack_send( obj.STATE_MAV_READING )
        if ((v == True) and (r == True)):
        # if (obj.ack_send.value == True):
        
            # send mavlink message  obj.name obj.signal.value obj.numberOfVals      
            #
            getName, getValueforMAVSending, getPrev, myState = obj.get_value_data(obj.STATE_MAV_READING, Timeout) 
            print(f"-------------- obj update found for param_value {getName} {getValueforMAVSending} {getPrev} {myState}")
            if (myState == True):
                try:
                    the_connection.mav.param_ext_value_send(
                        getName.encode('utf-8'),
                        str(getValueforMAVSending).encode('utf-8'),
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
                        # obj.updateNeeded.value = False
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

import socket
import os    
import sys
import serial
import glob
import threading

# for serial message out packing
import struct

import math

#
# import array if you want to use it
#
import array as arr

#
# multithreading control via asyncio
#
import asyncio
import time

import re

import numpy as np

import time

#
# set to 1 if you want wx HMI (needs to python2) 
# TODO :: make backward compatible with python2
#
IAM_A_GCS_WITH_HMI = 0
if IAM_A_GCS_WITH_HMI == 1:
    import wx
    
# this is included for android serial and to detect the android platform using kivy
# ref:- https://github.com/frmdstryr/kivy-android-serial
# install kivy with the following in your conda environment
# conda install kivy -c conda-forge

# ================== Compatible Joysticks =========================================
# X-Box 360 Controller (name: "Xbox 360 Controller")
# Playstation 4 Controller (name: "PS4 Controller")
# X-Box 360 Controller (name: "Controller (XBOX 360 For Windows)")
#  
from pymavlink import mavutil   # ref:- https://www.ardusub.com/developers/pymavlink.html

if 'ANDROID_BOOTLOGO' in os.environ:                            # device android
    from kivy.utils import platform
    from kvserial.driver import CdcAcmSerialPort

# to list ports using the serial library
from serial.tools import list_ports

BUTTON_CONNECT = 10
BUTTON_ARM = 20

# ethernet UDP communication and joystick
#
# python3 -m pip install -U pygame --user
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


# for custom mavlink we have currently disabled
#
#from mypymavlink import mavutilcust as custommav


#import os

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
    """fifo object"""
    def __init__(self):
        self.buf = []
    def write(self, data):
        self.buf += data
        return len(data)
    def read(self):
        return self.buf.pop(0)

        
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
        """this class is for communicating with mavlink """
        #self.setUPPiRelayNumBCM()
        #self.setPinINput(pinNum)
        MAVFrame.pin_no=pinNum

    def __del__(self):  
        """ deletes the class """
        class_name = self.__class__.__name__  
        print('{} Deleted'.format(class_name))  

    #
    # check our operating system we mostly at present only support linux
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
        #textPrint = TextPrint()
        return joystick,clock
    
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
        
    def joyMavlinkInit(self, mav_ver=2):
        if mav_ver == 1:
            mav = mavutil.mavlink1.MAVLink(fifo())
        else:
            mav = mavutil.mavlink2.MAVLink(fifo())        
        mav.srcSystem = MAV_SOURCE                          # set to master
        return mav
        
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
        #for angle in xrange(1, times, 5):
        #    a = angle * math.pi / 180
        for angle in range(1, times):
            a = (angle*5) * math.pi / 180
            self.write_serial_data(serial, int(lenght * math.cos(a)), int(lenght * math.sin(a)),0,0,0,0)
            time.sleep(delta)
        self.write_serial_data(serial, 0,0,0,0,0,0)
 
    def test_angles(self, serial, lenght=200, times=1000, delta=0.05):
        #for angle in xrange(1, times, 5):
        #    a = angle * math.pi / 180
        for angle in range(1, times):
            a = (angle*5) * math.pi / 180
            self.write_serial_data(0, 0,0,0,int(30 * math.cos(a)),int(30 * math.sin(-a)))
            time.sleep(delta)
        self.write_serial_data(serial, 0,0,0,0,0,0)
 
    def test_yaw(self, serial, lenght=200, times=1000, delta=0.05):
        #for angle in xrange(1, times, 5):
        #    a = angle * math.pi / 180
        for angle in range(1, times):
            a = (angle*5) * math.pi / 180
            self.write_serial_data(serial, int(lenght * math.cos(a)),0,0,int(30 * math.sin(a)),0,0)
            time.sleep(delta)
        self.write_serial_data(serial, 0,0,0,0,0,0)
        
    def processJoystickSendMavlink(self, sock, mav, joystick):

        msgbuf = None
        # -------- Main Program Loop -----------
        doneLoop = False
        while doneLoop == False:
            btns = 0
            thrust = 0.0
            rudder = 0.0

            # EVENT PROCESSING STEP
            for event in pygame.event.get(): # User did something

                screen.fill(WHITE)
                #textPrint.reset()
                
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
                    doneLoop = True
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
                #textPrint.indent()

                for i in range( hats ):
                    hat = joystick.get_hat( i )
                    print( "Hat {} value: {}".format(i, str(hat)) )
            
                # Getting available devices
                for id in range(pygame.joystick.get_count()):
                    print( "devices list : %d %s" % (id, pygame.joystick.Joystick(id).get_name()))
                    
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
                #textPrint.indent()

                for i in range( axes ):
                    axis = joystick.get_axis( i )
                    print( "Axis {} value: {:>6.3f}".format(i, axis) )
                #textPrint.unindent()

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
            #the_conection = mavutil.mavlink_connection('udpin:127.0.0.1:14551',autoreconnect=True)
            the_conection = mavutil.mavlink_connection('udpin:0.0.0.0:14550',autoreconnect=True, source_system=1, source_component=100)
            return the_conection,True
        except Exception as err_msg:
            print("Failed to connect : %s" % (err_msg))
            return the_conection,False

    def makeNewMAVlinkConn(self,id):
        try:
            #the_conection = mavutil.mavlink_connection('udpin:127.0.0.1:14551',autoreconnect=True, source_system=id)
            the_conection = mavutil.mavlink_connection('udpin:0.0.0.0:14550',autoreconnect=True, source_system=id, source_component=100)
            return the_conection,True
        except Exception as err_msg:
            print("Failed to connect : %s" % (err_msg))
            return the_conection,False

    def makeMAVlinkSerialConn(self, usbPort='/dev/ttyAMA0', id=1, comp=100, baudrate=115200):
        try:
            #the_conection = mavutil.mavlink_connection('udpin:127.0.0.1:14551',autoreconnect=True)
            the_conection = mavutil.mavlink_connection(usbPort, baud=baudrate, autoreconnect=True, source_system=id, source_component=comp)
            return the_conection, True
        except Exception as err_msg:
            print("Failed to connect : %s" % (err_msg))
            return the_conection, False
            
    # Send heartbeat from camera to GCS (types are define as enum in the dialect file). 
    #
    def mavlink_send_GCS_heartbeat(self, the_conection): 
        print(" heartbeat..............................  %s\n"%(mavutil.mavlink.MAV_TYPE_CAMERA))
        try:
            the_conection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_CAMERA, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavutil.mavlink.MAV_STATE_ACTIVE)
            ret = True
        except Exception as err_msg:
            print("Failed to send GCS heartbeat : %s" % (err_msg))
            ret = False
        print(" heartbeat..............................  %s\n"%(ret))
        return ret

    # Send heartbeat from camera to GCS that we are calibrating 
    #
    def mavlink_send_GCS_heartbeat_cal(self, the_conection): 
        print(" heartbeat..............................  %s\n"%(mavutil.mavlink.MAV_TYPE_CAMERA))
        try:
            the_conection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_CAMERA, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavutil.mavlink.MAV_STATE_CALIBRATING)
            ret = True
        except Exception as err_msg:
            print("Failed to send GCS heartbeat : %s" % (err_msg))
            ret = False
        print(" heartbeat..............................  %s\n"%(ret))
        return ret

    # Send heartbeat from camera to GCS that we are in standby and not ready 
    #
    def mavlink_send_GCS_heartbeat_sb(self, the_conection): 
        print(" heartbeat..............................  %s\n"%(mavutil.mavlink.MAV_TYPE_CAMERA))
        try:
            the_conection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_CAMERA, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavutil.mavlink.MAV_STATE_STANDBY)
            ret = True
        except Exception as err_msg:
            print("Failed to send GCS heartbeat : %s" % (err_msg))
            ret = False
        print(" heartbeat..............................  %s\n"%(ret))
        return ret

    # Send heartbeat from camera to GCS that we are booting 
    #
    def mavlink_send_GCS_heartbeat_boot(self, the_conection): 
        print(" heartbeat..............................  %s\n"%(mavutil.mavlink.MAV_TYPE_CAMERA))
        try:
            the_conection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_CAMERA, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavutil.mavlink.MAV_STATE_BOOT)
            ret = True
        except Exception as err_msg:
            print("Failed to send GCS heartbeat : %s" % (err_msg))
            ret = False
        print(" heartbeat..............................  %s\n"%(ret))
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
    #'''return True if using MAVLink 1.0 or later'''
        return float(connID.WIRE_PROTOCOL_VERSION) >= 1

    def mavlink20(self,connID):
    #'''return True if using MAVLink 2.0 or later'''
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
                the_connection.mav.file_transfer_protocol_send(
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

    def mavlink_do_digicam_configure_old(self, the_connection, mode=4, shutter_speed=0, aperture=0, iso=0, exposure_type=0, command_id=0, engine_cut_off=0, extra_param=255, extra_value=0):
        #if self.mavlink10():
        try:
            the_connection.mav.digicam_configure_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                mode, 
                shutter_speed, 
                aperture, 
                iso, 
                exposure_type,  
                command_id, 
                engine_cut_off, 
                extra_param,
                extra_value) 
            ret = True
        except Exception as err_msg:
            print("Failed to send digicam configure using old command : %s" % (err_msg))
            ret = False
        return ret

    def mavlink_do_digicam_control_old(self, the_connection, session, zoom_pos, zoom_step, focus_lock, shot, command_id, extra_param, extra_value):
        #if self.mavlink10():
        try:
            the_connection.mav.digicam_control_send(
                the_connection.target_system,  # target_system
                the_connection.target_component, # target_component
                session, 
                zoom_pos, 
                zoom_step, 
                focus_lock, 
                shot,  
                command_id,  
                extra_param,
                extra_value) 
            ret = True
        except Exception as err_msg:
            print("Failed to send digicam control using old command : %s" % (err_msg))
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
            "CAM_ISO".encode('utf-8'),
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
            "CAM_APERTURE".encode('utf-8'),
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
            "CAM_EXPMODE".encode('utf-8'),
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
            "S_FOCUS_MODE".encode('utf-8'),
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
            "S_FOCUS_AREA".encode('utf-8'),
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
            "CAM_SHUTTERSPD".encode('utf-8'),
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
            "CAM_WBMODE".encode('utf-8'),
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
            "S_STILL_CAP".encode('utf-8'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            8)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 8: %s" % (err_msg))
            return False

    def mavlink_send_param_value_tag(self, the_connection, val. tag ):

        print(f"\033[38m sending a parameter : {tag} ")    
        d = struct.unpack('f', struct.pack('I', val))[0]
        try:
            the_connection.mav.param_value_send(
            tag.encode('utf-8'),
            d,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            8,
            8)
            return True
        except Exception as err_msg:
            print("Failed to send param value message %s : %s" % (tag, err_msg))
            return False
            
    def mavlink_send_param_ext_value_iso(self, the_connection, val ):
        
        print("\033[31m sending an ext parameter iso") 
        d = str(val)
        try:
            the_connection.mav.param_ext_value_send(
            "CAM_ISO".encode('utf-8'),
            d.encode('utf-8'),
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
            "CAM_APERTURE".encode('utf-8'),
            d.encode('utf-8'),
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
            "CAM_EXPMODE".encode('utf-8'),
            d.encode('utf-8'),
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
            "S_FOCUS_MODE".encode('utf-8'),
            d.encode('utf-8'),
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
            "S_FOCUS_AREA".encode('utf-8'),
            p.encode('utf-8'),
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
            "CAM_SHUTTERSPD".encode('utf-8'),
            d.encode('utf-8'),
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
            "CAM_WBMODE".encode('utf-8'),
            d.encode('utf-8'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            8,
            7)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 7: %s" % (err_msg))
            return False

    def mavlink_send_param_ext_value_still_cap(self, the_connection, val ):

        print("\033[37m sending an ext parameter still capture \033[0m")       
        d = str(val)
        try:
            the_connection.mav.param_ext_value_send(
            "S_STILL_CAP".encode('utf-8'),
            d.encode('utf-8'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            8,
            8)
            return True
        except Exception as err_msg:
            print("Failed to send param value message 8: %s" % (err_msg))
            return False

    def mavlink_send_param_ext_value_tag(self, the_connection, val, tag ):

        print(f"\033[37m sending an ext parameter {tag} \033[0m")       
        d = str(val)
        try:
            the_connection.mav.param_ext_value_send(
            tag.encode('utf-8'),
            d.encode('utf-8'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            8,
            8)
            return True
        except Exception as err_msg:
            print("Failed to send param value message %s : %s" % (tag, err_msg))
            return False
            
    def mavlink_send_param_ext_value_mica_exposure(self, the_connection, val, tag, idx ):

        print("\033[32m sending a parameter ext message for : redEdge exposure \033[0m") 
        if idx => 1 and idx <= 5:        
            d = str(val)
            try:
                the_connection.mav.param_ext_value_send(
                tag.encode('utf-8'),
                d.encode('utf-8'),
                mavdefs.MAV_PARAM_EXT_TYPE_REAL32,
                8,
                8+idx)
                return True
            except Exception as err_msg:
                print("Failed to send param ext value message %d: %s" % (idx, err_msg))
                return False
        else:            
            d = struct.unpack('f', struct.pack('I', val))[0]
            try:
                the_connection.mav.param_ext_value_send(
                tag.encode('utf-8'),
                d.encode('utf-8'),
                mavdefs..MAV_PARAM_EXT_TYPE_UINT32,
                8,
                8+idx)
                return True
            except Exception as err_msg:
                print("Failed to send param ext value message %d: %s" % (idx, err_msg))
                return False
                
    def mavlink_send_param_value_mica_exposure(self, the_connection, val, tag, idx ):

        print("\033[32m sending a parameter : redEdge exposure \033[0m")  
        if idx => 1 and idx <= 5:
            d = val
            try:
                the_connection.mav.param_value_send(
                tag.encode('utf-8'),
                d,
                mavutil.mavlink..MAV_PARAM_TYPE_REAL32,
                8,
                8+idx)
                return True
            except Exception as err_msg:
                print("Failed to send param value message 3: %s" % (err_msg))
                return False
        else:            
            d = struct.unpack('f', struct.pack('I', val))[0]
            try:
                the_connection.mav.param_value_send(
                tag.encode('utf-8'),
                d,
                mavutil.mavlink..MAV_PARAM_TYPE_UINT32,
                8,
                8+idx)
                return True
            except Exception as err_msg:
                print("Failed to send param value message 3: %s" % (err_msg))
                return False
            
    def mavlink_send_param_value(self, the_connection):
        
        print("\033[36m sending a parameter") 
        d = struct.unpack('f', struct.pack('I', 1))[0]
        try:
            the_connection.mav.param_value_send(
            "CAM_ISO".encode('utf-8'),
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
            "CAM_APERTURE".encode('utf-8'),
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
            "CAM_EXPMODE".encode('utf-8'),
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
            "S_FOCUS_MODE".encode('utf-8'),
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
            "S_FOCUS_AREA".encode('utf-8'),
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
            "CAM_SHUTTERSPD".encode('utf-8'),
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
            "CAM_WBMODE".encode('utf-8'),
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
            "S_STILL_CAP".encode('utf-8'),
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
        # convert string to utf-8 list and make numpy array
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

        #    "http://10.0.2.51/cam_defs/alpha_cam_new.xml".encode('utf-8'))
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
            "http://10.0.2.51/cam_defs".encode('utf-8'))
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
        # utf-8 string encoded
        #
        nm = "storenm"
        try:
            u8_model_name = (nm).encode("utf-8")
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
                u8_model_name,
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
        return True
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
                (self.videoname).encode('utf-8'),
                (self.video_uri).encode('utf-8'))
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
        print("\033[33m acking the ext parameter iso \033[0m") 
        d = str(val)
        try:
            the_connection.mav.param_ext_ack_send(
            tag.encode('ascii'),
            d.encode('ascii'),
            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
            status_code)
            ret = True
        except Exception as err_msg: 
            print("Failed to send param value message 1: %s" % (err_msg))
            ret = False
        return ret

    def writeParamSetFromMavLink( self, msgString, mavObj, dataRcv, the_connection ):

        # must be EXACT tag match
        #patternISO = re.compile(r"\bCAM_ISO\b")
        #patternAper = re.compile(r"\bCAM_APERTURE\b")
        #patternExPro = re.compile(r"\bCAM_EXPMODE\b")
        #patternFocus = re.compile(r"\bS_FOCUS_MODE\b")
        #patternFocA = re.compile(r"\bS_FOCUS_AREA\b")
        #patternShSp = re.compile(r"\bCAM_SHUTTERSPD\b")  
        #patternWhiBal = re.compile(r"CAM_WBMODE") 
        #patternStCa = re.compile(r"\bS_STILL_CAP\b") 

        if (len(msgString) == 0):
            print("zero length tag passed")
            return False
            
        if not (msgString.find("CAM_ISO") == -1):
        #if (re.search(patternISO, msgString.upper())==True): 
            print(f"saw sonISO with {dataRcv}")
            if (mavObj.setMavIsoModeData( dataRcv )==True):
                print(f"setMavIsoModeData sonISO with {dataRcv}")
                return (self.mavlink_send_param_value_iso( the_connection, dataRcv )) 
        elif not (msgString.find("CAM_APERTURE") == -1):
        #elif (re.search(patternAper, msgString.upper())==True):
            if (mavObj.setMavApertureData( dataRcv )==True):        
                return (self.mavlink_send_param_value_aper( the_connection, dataRcv ))          
        elif not (msgString.find("CAM_EXPMODE") == -1):
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
        elif not (msgString.find("CAM_SHUTTERSPD") == -1):
        #elif (re.search(patternShSp, msgString.upper())==True):
            if (mavObj.setMavShutterData( dataRcv )==True):         
                return (self.mavlink_send_param_value_shut_spd( the_connection, dataRcv ))                               
        elif not (msgString.find("CAM_WBMODE") == -1):
        #elif (re.search(patternWhiBal, msgString.upper())==True): 
            if (mavObj.setMavWhiteBalData( dataRcv )==True):        
                return (self.mavlink_send_param_value_white_bal( the_connection, dataRcv ))
        elif not (msgString.find("S_STILL_CAP") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavStillCapModeData( dataRcv )==True):        
                return (self.mavlink_send_param_value_still_cap( the_connection, dataRcv ))       
        elif not (msgString.find("RED_EXP_1") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 1 )==True):        
                return (self.mavlink_send_param_value_mica_exposure( the_connection, dataRcv, "RED_EXP_1", 1 ))   
        elif not (msgString.find("RED_EXP_2") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 2 )==True):        
                return (self.mavlink_send_param_value_mica_exposure( the_connection, dataRcv, "RED_EXP_2", 2 ))
        elif not (msgString.find("RED_EXP_3") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 3 )==True):        
                return (self.mavlink_send_param_value_mica_exposure( the_connection, dataRcv, "RED_EXP_3", 3 ))
        elif not (msgString.find("RED_EXP_4") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 4 )==True):        
                return (self.mavlink_send_param_value_mica_exposure( the_connection, dataRcv, "RED_EXP_4", 4 ))
        elif not (msgString.find("RED_EXP_5") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 5 )==True):        
                return (self.mavlink_send_param_value_mica_exposure( the_connection, dataRcv, "RED_EXP_5", 5 ))  
        elif not (msgString.find("RED_GAIN_1") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 6 )==True):        
                return (self.mavlink_send_param_value_mica_exposure( the_connection, dataRcv, "RED_GAIN_1", 6 ))   
        elif not (msgString.find("RED_GAIN_2") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 7 )==True):        
                return (self.mavlink_send_param_value_mica_exposure( the_connection, dataRcv, "RED_GAIN_2", 7 ))
        elif not (msgString.find("RED_GAIN_3") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 8 )==True):        
                return (self.mavlink_send_param_value_mica_exposure( the_connection, dataRcv, "RED_GAIN_3", 8 ))
        elif not (msgString.find("RED_GAIN_4") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 9 )==True):        
                return (self.mavlink_send_param_value_mica_exposure( the_connection, dataRcv, "RED_GAIN_4", 9 ))
        elif not (msgString.find("RED_GAIN_5") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 10 )==True):        
                return (self.mavlink_send_param_value_mica_exposure( the_connection, dataRcv, "RED_GAIN_5", 10 ))    
        elif not (msgString.find("CAMERA_CHOICE") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            with mavObj.set_cam_choice.get_lock():
                mavObj.set_cam_choice.value = dataRcv 
            return (self.mavlink_send_param_value_tag( the_connection, dataRcv, "CAMERA_CHOICE" ))                
        else:
            print("unsupported variable name %s to val=%d :: NOT SET "%(msgString,dataRcv))
            return False

    def readParamSetFromMavLink( self, msgString, mavObj, the_connection ):

        # must be EXACT tag match
        #patternISO = re.compile(r"\bCAM_ISO\b")
        #patternAper = re.compile(r"\bCAM_APERTURE\b")
        #patternExPro = re.compile(r"\bCAM_EXPMODE\b")
        #patternFocus = re.compile(r"\bS_FOCUS_MODE\b")
        #patternFocA = re.compile(r"\bS_FOCUS_AREA\b")
        #patternShSp = re.compile(r"\bCAM_SHUTTERSPD\b")  
        #patternWhiBal = re.compile(r"CAM_WBMODE") 
        #patternStCa = re.compile(r"\bS_STILL_CAP\b") 

        v = 0
        p = 0
        r = False

        if (len(msgString) == 0):
            print("zero length tag passed")
            return False
            
        if not (msgString.find("CAM_ISO") == -1):
        #if (re.search(patternISO, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamIso                                     # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavIsoModeData( )
            if (r == True):
                return ( self.mavlink_send_param_value_iso( the_connection, v ) )
            else:
                return False            
        elif not (msgString.find("CAM_APERTURE") == -1):
        #elif (re.search(patternAper, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamAperture                                # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavApertureData( )
            if (r == True):
                return ( self.mavlink_send_param_value_aper( the_connection, v ) )  
            else:
                return False                 
        elif not (msgString.find("CAM_EXPMODE") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamExPro                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavExProData( )
            if (r == True):
                return ( self.mavlink_send_param_value_expro( the_connection, v ) )
            else:
                return False                 
        elif not (msgString.find("S_FOCUS_AREA") == -1):
        #elif (re.search(patternFocA, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamFocusArea                                   # >>> set the bit to enable full read of parameter    
            v, p, r = mavObj.getMavFocusAreaData( )
            if (r == True):        
                return ( self.mavlink_send_param_value_focus_area( the_connection, v ) ) 
            else:
                return False                 
        elif not (msgString.find("S_FOCUS_MODE") == -1):
        #elif (re.search(patternFocus, msgString.upper())==True):
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamFocus                                   # >>> set the bit to enable full read of parameter  
            v, p, r = mavObj.getMavFocusData( )
            if (r == True):
                return ( self.mavlink_send_param_value_focus( the_connection, v ) )
            else:
                return False                 
        elif not (msgString.find("CAM_SHUTTERSPD") == -1):
        #elif (re.search(patternShSp, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamShutSpd                                   # >>> set the bit to enable full read of parameter  
            v, p, r = mavObj.getMavShutterData( )
            if (r == True):
                return ( self.mavlink_send_param_value_shut_spd( the_connection, v ) )      
            else:
                return False                 
        elif not (msgString.find("CAM_WBMODE") == -1):
        #elif (re.search(patternWhiBal, msgString.upper())==True):  
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamWhiteBala                                   # >>> set the bit to enable full read of parameter  
            v, p, r = mavObj.getMavWhiteBalData( )
            if (r == True):
                return ( self.mavlink_send_param_value_white_bal( the_connection, v ) )        
            else:
                return False 
        elif not (msgString.find("S_STILL_CAP") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():        
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamStillCap                                   # >>> set the bit to enable full read of parameter          
            v, p, r = mavObj.getMavStillCapModeData( )
            if (r == True):
                return ( self.mavlink_send_param_value_still_cap( the_connection, v ) )    
            else:
                return False                 
        elif not (msgString.find("RED_EXP_1") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamExPos1                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavMicaExposureData( 1 )
            if (r == True):
                return ( self.mavlink_send_param_value_mica_exposure( the_connection, v, "RED_EXP_1", 1 ) )
            else:
                return False 
        elif not (msgString.find("RED_EXP_2") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamExPos2                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavMicaExposureData( 2 )
            if (r == True):
                return ( self.mavlink_send_param_value_mica_exposure( the_connection, v, "RED_EXP_2", 2 ) )
            else:
                return False 
        elif not (msgString.find("RED_EXP_3") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamExPos3                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavMicaExposureData( 3 )
            if (r == True):
                return ( self.mavlink_send_param_value_mica_exposure( the_connection, v, "RED_EXP_3", 3 ) )
            else:
                return False 
        elif not (msgString.find("RED_EXP_4") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamExPos4                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavMicaExposureData( 4 )
            if (r == True):
                return ( self.mavlink_send_param_value_mica_exposure( the_connection, v, "RED_EXP_4", 4 ) )
            else:
                return False 
        elif not (msgString.find("RED_EXP_5") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamExPos5                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavMicaExposureData( 5 )
            if (r == True):
                return ( self.mavlink_send_param_value_mica_exposure( the_connection, v, "RED_EXP_5", 5 ) )
            else:
                return False 
        elif not (msgString.find("RED_GAIN_1") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamExGain1                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavMicaExposureData( 6 )
            if (r == True):
                return ( self.mavlink_send_param_value_mica_exposure( the_connection, v, "RED_GAIN_1", 6 ) )
            else:
                return False 
        elif not (msgString.find("RED_GAIN_2") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamExGain2                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavMicaExposureData( 7 )
            if (r == True):
                return ( self.mavlink_send_param_value_mica_exposure( the_connection, v, "RED_GAIN_2", 7 ) )
            else:
                return False 
        elif not (msgString.find("RED_GAIN_3") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamExGain3                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavMicaExposureData( 8 )
            if (r == True):
                return ( self.mavlink_send_param_value_mica_exposure( the_connection, v, "RED_GAIN_3", 8 ) )
            else:
                return False 
        elif not (msgString.find("RED_GAIN_4") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamExGain4                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavMicaExposureData( 9 )
            if (r == True):
                return ( self.mavlink_send_param_value_mica_exposure( the_connection, v, "RED_GAIN_4", 9 ) )
            else:
                return False 
        elif not (msgString.find("RED_GAIN_5") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamExGain5                                   # >>> set the bit to enable full read of parameter
            v, p, r = mavObj.getMavMicaExposureData( 10 )
            if (r == True):
                return ( self.mavlink_send_param_value_mica_exposure( the_connection, v, "RED_GAIN_5", 10 ) )
            else:
                return False 
        elif not (msgString.find("CAMERA_CHOICE") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            with mavObj.mav_req_all_param.get_lock():
                mavObj.mav_req_all_param.value |= mavlinkSonyCamWriteVals.ParamCamChoice                                   # >>> set the bit to enable full read of parameter
            return ( self.mavlink_send_param_value_tag( the_connection, mavObj.set_cam_choice.value, "CAMERA_CHOICE" ) )
        else:
            print("unsupported variable name %s :: NOT SET "%(msgString))
            return False
            
    def writeParamExtSetFromMavLink( self, msgString, mavObj, dataRcv, the_connection ):

        # must be EXACT tag match
        #patternISO = re.compile(r"\bCAM_ISO\b")
        #patternAper = re.compile(r"\bCAM_APERTURE\b")
        #patternExPro = re.compile(r"\bCAM_EXPMODE\b")
        #patternFocus = re.compile(r"\bS_FOCUS_MODE\b")
        #patternFocA = re.compile(r"\bS_FOCUS_AREA\b")
        #patternShSp = re.compile(r"\bCAM_SHUTTERSPD\b")  
        #patternWhiBal = re.compile(r"CAM_WBMODE") 
        #patternStCa = re.compile(r"\bS_STILL_CAP\b") 

        ret = False

        if (len(msgString) == 0):
            print("zero length tag passed")
            return False
            
        if not (msgString.find("CAM_ISO") == -1):
        #if (re.search(patternISO, msgString.upper())==True):
            print(f"CAM_ISO received {msgString} value {dataRcv}")
            ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_IN_PROGRESS, "CAM_ISO" )
            if ((mavObj.setMavIsoModeData( dataRcv )) == True):
                print(f"Succfully updated to Sony Cam for param_ext_set {mavdefs.PARAM_ACK_ACCEPTED}")
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "CAM_ISO" )
                print(f"Ack of ISO : {ret}")
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "CAM_ISO" )            
        elif not (msgString.find("CAM_APERTURE") == -1):
        #elif (re.search(patternAper, msgString.upper())==True): 
            if ((mavObj.setMavApertureData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "CAM_APERTURE" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "CAM_APERTURE" )   
        elif not (msgString.find("CAM_EXPMODE") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            if ((mavObj.setMavExProData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "CAM_EXPMODE" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "CAM_EXPMODE" )                        
        elif not (msgString.find("S_FOCUS_AREA") == -1):
        #elif (re.search(patternFocA, msgString.upper())==True):    
            if ((mavObj.setMavFocusAreaData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "S_FOCUS_AREA" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "S_FOCUS_AREA" )              
        elif not (msgString.find("S_FOCUS_MODE") == -1):
        #elif (re.search(patternFocus, msgString.upper())==True):
            if ((mavObj.setMavFocusData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "S_FOCUS_MODE" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "S_FOCUS_MODE" )                 
        elif not (msgString.find("CAM_SHUTTERSPD") == -1):
        #elif (re.search(patternShSp, msgString.upper())==True):   
            if ((mavObj.setMavShutterData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "CAM_SHUTTERSPD" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "CAM_SHUTTERSPD" )                           
        elif not (msgString.find("CAM_WBMODE") == -1):
        #elif (re.search(patternWhiBal, msgString.upper())==True):  
            if ((mavObj.setMavWhiteBalData( dataRcv )) == True):
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "CAM_WBMODE" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "CAM_WBMODE" )          
        elif not (msgString.find("S_STILL_CAP") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):    
            if ((mavObj.setMavStillCapModeData( dataRcv )) == True):
                    ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "S_STILL_CAP" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "S_STILL_CAP" )  
        elif not (msgString.find("RED_EXP_1") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 1 )==True):        
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "RED_EXP_1" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "RED_EXP_1" )   
        elif not (msgString.find("RED_EXP_2") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 2 )==True):        
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "RED_EXP_2" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "RED_EXP_2" ) 
        elif not (msgString.find("RED_EXP_3") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 3 )==True):        
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "RED_EXP_3" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "RED_EXP_3" ) 
        elif not (msgString.find("RED_EXP_4") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 4 )==True):        
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "RED_EXP_4" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "RED_EXP_4" ) 
        elif not (msgString.find("RED_EXP_5") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 5 )==True):        
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "RED_EXP_5" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "RED_EXP_5" )                 
        elif not (msgString.find("RED_GAIN_1") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 6 )==True):        
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "RED_GAIN_1" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "RED_GAIN_1" )   
        elif not (msgString.find("RED_GAIN_2") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 7 )==True):        
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "RED_GAIN_2" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "RED_GAIN_2" ) 
        elif not (msgString.find("RED_GAIN_3") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 8 )==True):        
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "RED_GAIN_3" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "RED_GAIN_3" ) 
        elif not (msgString.find("RED_GAIN_4") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 9 )==True):        
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "RED_GAIN_4" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "RED_GAIN_4" ) 
        elif not (msgString.find("RED_GAIN_5") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            if (mavObj.setMavMicaExposureData( dataRcv, 10 )==True):        
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "RED_GAIN_5" )
            else:
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_FAILED, "RED_GAIN_5" ) 
        elif not (msgString.find("CAMERA_CHOICE") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True): 
            with mavObj.set_cam_choice.get_lock():
                mavObj.set_cam_choice.value = dataRcv      
                ret = self.mavlink_send_param_ext_ack( the_connection, dataRcv, mavdefs.PARAM_ACK_ACCEPTED, "CAMERA_CHOICE" )
        else:
            print("unsupported variable name %s to val=%d :: NOT SET "%(msgString,dataRcv))
            return False

        return ret
                
    def readParamExtSetFromMavLink( self, msgString, mavObj, the_connection ):

        # must be EXACT tag match
        #patternISO = re.compile(r"\bCAM_ISO\b")
        #patternAper = re.compile(r"\bCAM_APERTURE\b")
        #patternExPro = re.compile(r"\bCAM_EXPMODE\b")
        #patternFocus = re.compile(r"\bS_FOCUS_MODE\b")
        #patternFocA = re.compile(r"\bS_FOCUS_AREA\b")
        #patternShSp = re.compile(r"\bCAM_SHUTTERSPD\b")  
        #patternWhiBal = re.compile(r"CAM_WBMODE") 
        #patternStCa = re.compile(r"\bS_STILL_CAP\b") 

        v = 0
        p = 0
        r = False

        if (len(msgString) == 0):
            print("zero length tag passed")
            return False
            
        if not (msgString.find("CAM_ISO") == -1):
        #if (re.search(patternISO, msgString.upper())==True): 
            v, p, r = mavObj.getMavIsoModeData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_iso( the_connection, v ) == True ):
                    print(f"\033[33m Value ISO is : {v}\033[0m")
                    with mavObj.mav_ext_req_all_param.get_lock():
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamIso                                     # >>> set the bit to enable full read of parameter
                    return r
            return False            
        elif not (msgString.find("CAM_APERTURE") == -1):
        #elif (re.search(patternAper, msgString.upper())==True): 
            v, p, r = mavObj.getMavApertureData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_aper( the_connection, v ) == True ):
                    with mavObj.mav_ext_req_all_param.get_lock():                
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamAperture                                # >>> set the bit to enable full read of parameter                
                    return r
            return False                 
        elif not (msgString.find("CAM_EXPMODE") == -1):
        #elif (re.search(patternExPro, msgString.upper())==True): 
            v, p, r = mavObj.getMavExProData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_expro( the_connection, v ) == True ):
                    with mavObj.mav_ext_req_all_param.get_lock():                  
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamExPro                                   # >>> set the bit to enable full read of parameter
                    return r
            return False                  
        elif not (msgString.find("S_FOCUS_AREA") == -1):
        #elif (re.search(patternFocA, msgString.upper())==True): 
            v, p, r = mavObj.getMavFocusAreaData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_focus_area( the_connection, v ) == True ):
                    with mavObj.mav_ext_req_all_param.get_lock(): 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamFocusArea                               # >>> set the bit to enable full read of parameter                  
                    return r
            return False                 
        elif not (msgString.find("S_FOCUS_MODE") == -1):
        #elif (re.search(patternFocus, msgString.upper())==True):
            v, p, r = mavObj.getMavFocusData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_focus( the_connection, v ) == True ):
                    with mavObj.mav_ext_req_all_param.get_lock(): 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamFocus                                   # >>> set the bit to enable full read of parameter 
                    return r
            return False                  
        elif not (msgString.find("CAM_SHUTTERSPD") == -1):
        #elif (re.search(patternShSp, msgString.upper())==True): 
            v, p, r = mavObj.getMavShutterData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_shut_spd( the_connection, v ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock(): 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamShutSpd                                 # >>> set the bit to enable full read of parameter                 
                    return r
            return False                     
        elif not (msgString.find("CAM_WBMODE") == -1):
        #elif (re.search(patternWhiBal, msgString.upper())==True):  
            v, p, r = mavObj.getMavWhiteBalData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_white_bal( the_connection, v ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock(): 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamWhiteBala                               # >>> set the bit to enable full read of parameter                  
                    return r
            return False 
        elif not (msgString.find("S_STILL_CAP") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavStillCapModeData( )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_still_cap( the_connection, v ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock():                 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamStillCap                                # >>> set the bit to enable full read of parameter                  
                    return r
            return False    
        elif not (msgString.find("RED_EXP_1") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavMicaExposureData( 1 )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_mica_exposure( the_connection, v, "RED_EXP_1", 1 ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock():                 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamExPos1                                # >>> set the bit to enable full read of parameter                  
                    return r
            return False  
        elif not (msgString.find("RED_EXP_2") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavMicaExposureData( 2 )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_mica_exposure( the_connection, v, "RED_EXP_2", 2 ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock():                 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamExPos2                                # >>> set the bit to enable full read of parameter                  
                    return r
            return False 
        elif not (msgString.find("RED_EXP_3") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavMicaExposureData( 3 )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_mica_exposure( the_connection, v, "RED_EXP_3", 3 ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock():                 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamExPos3                                # >>> set the bit to enable full read of parameter                  
                    return r
            return False 
        elif not (msgString.find("RED_EXP_4") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavMicaExposureData( 4 )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_mica_exposure( the_connection, v, "RED_EXP_4", 4 ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock():                 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamExPos4                                # >>> set the bit to enable full read of parameter                  
                    return r
            return False 
        elif not (msgString.find("RED_EXP_5") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavMicaExposureData( 5 )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_mica_exposure( the_connection, v, "RED_EXP_5", 5 ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock():                 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamExPos5                                # >>> set the bit to enable full read of parameter                  
                    return r
            return False 
        elif not (msgString.find("RED_GAIN_1") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavMicaExposureData( 6 )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_mica_exposure( the_connection, v, "RED_GAIN_1", 6 ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock():                 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamExGain1                                # >>> set the bit to enable full read of parameter                  
                    return r
            return False  
        elif not (msgString.find("RED_GAIN_2") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavMicaExposureData( 7 )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_mica_exposure( the_connection, v, "RED_GAIN_2", 7 ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock():                 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamExGain2                                # >>> set the bit to enable full read of parameter                  
                    return r
            return False 
        elif not (msgString.find("RED_GAIN_3") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavMicaExposureData( 8 )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_mica_exposure( the_connection, v, "RED_GAIN_3", 8 ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock():                 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamExGain3                                # >>> set the bit to enable full read of parameter                  
                    return r
            return False 
        elif not (msgString.find("RED_GAIN_4") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavMicaExposureData( 9 )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_mica_exposure( the_connection, v, "RED_GAIN_4", 9 ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock():                 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamExGain4                                # >>> set the bit to enable full read of parameter                  
                    return r
            return False 
        elif not (msgString.find("RED_GAIN_5") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v, p, r = mavObj.getMavMicaExposureData( 10 )
            if (r == True):
                if ( self.mavlink_send_param_ext_value_mica_exposure( the_connection, v, "RED_GAIN_5", 10 ) == True ): 
                    with mavObj.mav_ext_req_all_param.get_lock():                 
                        mavObj.mav_ext_req_all_param.value |= mavObj.ParamExGain5                                # >>> set the bit to enable full read of parameter                  
                    return r
            return False       
        elif not (msgString.find("CAMERA_CHOICE") == -1):
        #elif (re.search(patternStCa, msgString.upper())==True):   
            v = mavObj.set_cam_choice.value
            if ( self.mavlink_send_param_ext_value_tag( the_connection, v, "CAMERA_CHOICE" ) == True ): 
                with mavObj.mav_ext_req_all_param.get_lock():                 
                     mavObj.mav_ext_req_all_param.value |= mavObj.ParamCamChoice                                # >>> set the bit to enable full read of parameter                  
                return r
            return False              
        else:
            print("unsupported variable name %s to val=%d :: NOT SET " % (msgString, v))
            return False
            
    # process the incoming messages received
    #
    def process_messages_from_connection(self, the_connection, sharedObj, loop=5, redCam=0):
        #"""
        #This runs continuously. The mavutil.recv_match() function will call mavutil.post_message()
        #any time a new message is received, and will notify all functions in the master.message_hooks list.
        #"""
        
        # define the cameras on board or in use at any one time
        # TODO :: consider reading this from the xml definition file
        #
        sony_a7_only = 1
        micasense_red_edge = 2
        both_camera = 3
                
        while loop >= 1:
        #while True:
            #print("im receiving.............")
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
            #if (loop == 4):
            #    self.mavlink_send_camera_capture_status(the_connection)
            #print(f" video stream returned {self.mavlink_send_video_stream_information(the_connection)}")
            #self.mavlink_send_camera_image_captured(the_connection)
            #the_connection.mav.camera_feedback_send( 1000, 1, 1, 22, 21, 10, 30, 21, 2, 3, 5, 2, 3)
            #the_connection.mav.gps_raw_int_send( 1000, self.g_count, 77, 66, 76, 3, 1, 2, 3, 5)
            #the_connection.mav.vibration_send( 1000, 1, 1, 22, 21, 10, 30 )
            #self.mavlink_send_camera_information(the_connection)
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
                if (sharedObj.set_cam_choice.value == sony_a7_only):
                    mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM = mavlinkSonyCamWriteVals.alpha7_options   
                elif (sharedObj.set_cam_choice.value == micasense_red_edge):
                    mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM = mavlinkSonyCamWriteVals.mica_options
                elif (sharedObj.set_cam_choice.value == both_camera):
                    mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM = mavlinkSonyCamWriteVals.all_options                    
                with sharedObj.mav_req_all_param.get_lock():
                    sharedObj.mav_req_all_param.value = mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM
                print("\033[35m PARAM_REQUEST_LIST was sent - shared object set to %d" % (sharedObj.mav_req_all_param.value))
                # ===== TRAP ======
                #exit(99)
            elif msg.get_type() == 'PARAM_EXT_REQUEST_LIST':
                #
                #
                if (sharedObj.set_cam_choice.value == sony_a7_only):
                    mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM = mavlinkSonyCamWriteVals.alpha7_options   
                elif (sharedObj.set_cam_choice.value == micasense_red_edge):
                    mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM = mavlinkSonyCamWriteVals.mica_options
                elif (sharedObj.set_cam_choice.value == both_camera):
                    mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM = mavlinkSonyCamWriteVals.all_options   
                with sharedObj.mav_ext_req_all_param.get_lock(): 
                    sharedObj.mav_ext_req_all_param.value = mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM
                print("\033[35m PARAM_EXT_REQUEST_LIST was sent - shared object set to %d" % (sharedObj.mav_ext_req_all_param.value))  
                # ===== TRAP ======
                #exit(99)                
            elif msg.get_type() == 'PARAM_SET':
                print(f"\033[32m whole dump {msg}\033[0m")
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
                #exit(96)
            elif msg.get_type() == 'PARAM_EXT_SET':
                #
                # self.mavlink_send_param_value(the_connection) there are two different data types from various senders
                #
                converted = True
                try:
                    valueSet = int(msg.param_value)
                    print(valueSet)
                except Exception as err_msg:
                    print(f"\033[31m PARAM_EXT_SET :: Error converting type {err_msg} and value {msg.param_value} and dump {msg} \033[0m")
                    #exit(95)
                    #try:
                    #    valueSetActual = msg.param_value
                    #    valueSet = int(valueSetActual.decode('utf-8'))
                    #except Exception as err_msg:
                    #    print(f"\033[31m PARAM_EXT_SET :: Error converting type {err_msg} it says {msg.param_value} \033[0m")
                    converted = False
                if ( converted == True):
                    print(f"Setting Param_Ext_Set Value : {valueSet} : param id : {msg.param_id}")
                    #ee = self.mav_param_type_conv( msg.param_type, valueSet )
                    #print(f"ee value is {ee}")
                    if (self.writeParamExtSetFromMavLink( msg.param_id, sharedObj, valueSet, the_connection ) == True):
                        print("\033[35m PARAM_EXT_SET :: was sent for %s :: %d \033[0m" % (msg.param_id, valueSet))
                        ## =======> send_ext_ack
                    else:
                        print("\033[31m PARAM_EXT_SET :: write fail for %s :: %d \033[0m" % (msg.param_id, valueSet))
                #exit(95)
                # ===== TRAP =====
            elif msg.get_type() == 'PARAM_VALUE':
                print(f"Recieved a param value for :- {msg.param_id} = {msg.param_value}")
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

                if not (sharedObj.cmd_wants_ack.value == True):
                    self.RCV_COMMAND = int(msg.command)
                    print(f"\033[35m IN LOOP :: self ACK RES {self.ACK_RESULT} RCV {self.RCV_COMMAND} == {mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE}")
 
                    if (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE):
                        self.RPM2 = int(msg.param1) 
                        print(f"Is it here {self.RPM2} == {self.CAMERA_INFORMATION}")
                        if (self.RPM2 == self.CAMERA_INFORMATION):                                  #camera_information
                            self.type_of_msg = 6500
                            print("\033[34m >>>>>> camera information \033[36m >>>>>>>>>>>>>>>>>>>>>>")
                            self.mavlink_send_camera_information(the_connection)
                        elif (self.RPM2 == self.CAMERA_SETTINGS):                                   #camera_settings
                            self.type_of_msg = 6501                        
                        elif (self.RPM2 == self.STORAGE_INFORMATION):                               #storage information
                            self.type_of_msg = 6502
                        elif (self.RPM2 == self.CAMERA_CAPTURE_STATUS):                             #camera capture status
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
                        # test here..... self.mavlink_send_camera_information(the_connection)
                        if (msg.param1 == 1):
                            self.type_of_msg = mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_INFORMATION
                            print("\033[32m =========== !! sending to QGround Camera Information !! ==========\033[0m ")
                            self.mavlink_send_camera_information(the_connection)
                        else:
                            print("\033[33m =========== !! not sending to QGround Camera Information !! ==========\033[0m ")                        
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_REQUEST_VIDEO_STREAM_INFORMATION):
                        print("request video stream Info OLD MESSAGE.....")
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_REQUEST_VIDEO_STREAM_INFORMATION
                        print("=========== !! send to QGround VideoStream !! ==========")
                        self.mavlink_send_video_stream_information(the_connection)
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_SETTINGS):
                        print("request camera settings Info OLD MESSAGE.....")
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_SETTINGS
                        print("\033[35m =========== !! sending to QGround Camera settings !! ========== \033[0m")
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
                        sharedObj.take_continuos = True
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_IMAGE_STOP_CAPTURE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_IMAGE_STOP_CAPTURE
                        self.Got_Param1 = msg.param3
                        self.Got_Param2 = msg.param4
                        sharedObj.take_continuos = False
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
                        # Taking a picture on the sony is via the global slot being set
                        #
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL
                        print(f"\033[33m DO DIGICAM CONTROL {msg.param5} {msg.param7}")
                        if (sharedObj.set_cam_choice.value == sony_a7_only):
                            if ((int(msg.param5) == 1) and (int(msg.param7) == 0)):
                                #fastGlobals.take_picture = 1 
                                with sharedObj.take_photo.get_lock():   
                                    sharedObj.take_photo.value = 1
                                print("\033[34m asked to take a sony photo ....... set it to 1 \033[0m")
                        #
                        # Taking a picture is hard coded to here for micasense as it needs no delay
                        #
                        elif (sharedObj.set_cam_choice.value == micasense_red_edge):
                            if ((int(msg.param5) == 1) and (int(msg.param7) == 1)):
                                try:
                                    if (redCam.redEdgeCaptureFivePicturesNoUpload() == 1):
                                        print("\033[32m Took the micasense pictures on SD Card \033[0m")
                                    else:
                                        print("Error taking pictures with the micasense camera")
                                except Exception as e:
                                    print(f" Tried to take picture ERROR:: {e}") 
                            elif ((int(msg.param5) == 1) and (int(msg.param7) == 0)):
                                try:
                                    if (redCam.redEdgeCaptureFivePictures() == 1):
                                        print("\033[33m saved the micasense pictures to the raspberry Pi \033[0m")
                                    else:
                                        print("error saving the pictures to the raspberry Pi")
                                except Exception as e:
                                    print(f" Tried to take picture ERROR:: {e}") 
                        #
                        # Taking a picture for both cameras together
                        #
                        elif (sharedObj.set_cam_choice.value == both_camera):
                            if ((int(msg.param5) == 1) and (int(msg.param7) == 1)):
                                try:
                                    if (redCam.redEdgeCaptureFivePicturesNoUpload() == 1):
                                        print("\033[32m Took the micasense pictures on SD Card \033[0m")
                                    else:
                                        print("Error taking pictures with the micasense camera")
                                except Exception as e:
                                    print(f" Tried to take picture ERROR:: {e}") 
                            elif ((int(msg.param5) == 1) and (int(msg.param7) == 0)):
                                try:
                                    if (redCam.redEdgeCaptureFivePictures() == 1):
                                        print("\033[33m saved the micasense pictures to the raspberry Pi \033[0m")
                                    else:
                                        print("error saving the pictures to the raspberry Pi")
                                except Exception as e:
                                    print(f" Tried to take picture ERROR:: {e}") 
                            if ((int(msg.param5) == 1) and (int(msg.param7) == 0)):
                                #fastGlobals.take_picture = 1 
                                with sharedObj.take_photo.get_lock():
                                    sharedObj.take_photo.value = 1
                                print("\033[34m asked to take a sony photo ....... set it to 1 \033[0m")
                        #
                        # set the other digicam configure parameters for later processing if needed
                        #                        
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        self.Got_Param3 = msg.param3
                        self.Got_Param4 = msg.param4
                        self.Got_Param5 = msg.param5
                        self.Got_Param6 = msg.param6
                        self.Got_Param7 = msg.param7
                        print(f"\033[36m DO DIGICAM CONTROL RECEIVED \033[0m {msg.param5} {msg.param7} ")
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
                        sharedObj.reset_cam = True
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
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAVLINK_MSG_ID_BATTERY_STATUS):
                        self.type_of_msg = mavutil.mavlink.MAVLINK_MSG_ID_BATTERY_STATUS
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        print("\033[32m saw the battery status request come in")
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_PREFLIGHT_STORAGE):
                        print(f"\033[33m Asks for storage params paramStorage={msg.param1}  missionStorage={msg.param2} \033[0m")
                    elif (self.RCV_COMMAND == 42428):
                        print(f"\033[37m Command 42428 was sent not sure what im meant to do..... \033[0m")	
                    else:
                        print(f"got this id {self.RCV_COMMAND} {msg.command}")
                        self.RPM2 = 0
                        self.type_of_msg = self.RCV_COMMAND
                    with sharedObj.cmd_wants_ack.get_lock():
                        sharedObj.cmd_wants_ack.value = True
                    print("\033[36m >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ACK RES %d %d"%(self.ACK_RESULT,mavutil.mavlink.MAV_RESULT_ACCEPTED))
                    print("\033[31m")
                else:
                    # photo taking always takes precedence over anything else otherwise report busy therefore it overrides any other command long here
                    #                       
                    self.ACK_ERROR = self.GOT_ERROR
                    self.errRCV_COMMAND = msg.command
                    self.errRPM2 = msg.param1

                    if (self.errRCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL):
                        store = self.RCV_COMMAND
                        self.RCV_COMMAND = self.errRCV_COMMAND
                        self.errRCV_COMMAND = store
                        store = self.RPM2
                        self.RPM2 = self.errRPM2
                        self.errRPM2 = store                        
                        #
                        # Taking a picture on the sony is via the global slot being set
                        #
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL
                        print(f"\033[33m DO DIGICAM CONTROL {msg.param5} {msg.param7}")
                        if (sharedObj.set_cam_choice.value == sony_a7_only):
                            if ((int(msg.param5) == 1) and (int(msg.param7) == 0)):
                                #fastGlobals.take_picture = 1 
                                with sharedObj.take_photo.get_lock():   
                                    sharedObj.take_photo.value = 1
                                print("\033[34m asked to take a sony photo ....... set it to 1 \033[0m")
                        #
                        # Taking a picture is hard coded to here for micasense as it needs no delay
                        #
                        elif (sharedObj.set_cam_choice.value == micasense_red_edge):
                            if ((int(msg.param5) == 1) and (int(msg.param7) == 1)):
                                try:
                                    if (redCam.redEdgeCaptureFivePicturesNoUpload() == 1):
                                        print("\033[32m Took the micasense pictures on SD Card \033[0m")
                                    else:
                                        print("Error taking pictures with the micasense camera")
                                except Exception as e:
                                    print(f"Tried to take picture ERROR:: {e}") 
                            elif ((int(msg.param5) == 1) and (int(msg.param7) == 0)):
                                try:
                                    if (redCam.redEdgeCaptureFivePictures() == 1):
                                        print("\033[33m saved the micasense pictures to the raspberry Pi \033[0m")
                                    else:
                                        print("error saving the pictures to the raspberry Pi")
                                except Exception as e:
                                    print(f"Tried to take picture ERROR:: {e}") 
                        #
                        # Taking a picture for both cameras together
                        #
                        elif (sharedObj.set_cam_choice.value == both_camera):
                            if ((int(msg.param5) == 1) and (int(msg.param7) == 1)):
                                try:
                                    if (redCam.redEdgeCaptureFivePicturesNoUpload() == 1):
                                        print("\033[32m Took the micasense pictures on SD Card \033[0m")
                                    else:
                                        print("Error taking pictures with the micasense camera")
                                except Exception as e:
                                    print(f"Tried to take picture ERROR:: {e}") 
                            elif ((int(msg.param5) == 1) and (int(msg.param7) == 0)):
                                try:
                                    if (redCam.redEdgeCaptureFivePictures() == 1):
                                        print("\033[33m saved the micasense pictures to the raspberry Pi \033[0m")
                                    else:
                                        print("error saving the pictures to the raspberry Pi")
                                except Exception as e:
                                    print(f"Tried to take picture ERROR:: {e}") 
                            if ((int(msg.param5) == 1) and (int(msg.param7) == 0)):
                                #fastGlobals.take_picture = 1 
                                with sharedObj.take_photo.get_lock():
                                    sharedObj.take_photo.value = 1
                                print("\033[34m asked to take a sony photo ....... set it to 1 \033[0m")
                        #
                        # set the other digicam configure parameters for later processing if needed
                        #                        
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        self.Got_Param3 = msg.param3
                        self.Got_Param4 = msg.param4
                        self.Got_Param5 = msg.param5
                        self.Got_Param6 = msg.param6
                        self.Got_Param7 = msg.param7
                        print(f"\033[36m DO DIGICAM CONTROL RECEIVED \033[0m {msg.param5} {msg.param7} ")
                    else:
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
                if "Disarming motors" in msg.text:                        # denoted as a shutdown to clear the receive buffer and shutdown
                    with sharedObj.clear_buffer.get_lock():
                        sharedObj.clear_buffer.value = True               # set the flag to clear the buffer
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
    # send a linked list object as a PARAM_VALUE over mavlink
    #
    def sendMavlinkMessageForParamLinkedList( self, obj, the_connection, no_of_std_obj, Timeout=5 ):

        for node in range(0, LinkedListMemory.numberOfVals):
            if (obj.get_update_flag(node) == True): 
        
                # send mavlink message  obj.name obj.payload.value obj.numberOfVals      
                # 
                getValueforMAVSending, getPrev, getName = obj.get_all(node)
                print(f"-------------- obj update found for param_value {getName} {getValueforMAVSending} {getPrev} ")
                sendVal = struct.unpack('f', struct.pack('I', getValueforMAVSending))[0]  
                if (myState == True):
                    try:
                        the_connection.mav.param_value_send(
                            getName.encode('utf-8'),
                            sendVal,
                            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
                            obj.numberOfVals + no_of_std_obj,
                            obj.get_index(node) + no_of_std_obj)
                        ret = True
                    except Exception as err_msg:
                        print("Failed to send param value message : %s" % (err_msg))
                        ret = False
                    if (ret == True):
                        writeSuccess = False
                        TimeCount = 0
                        while (writeSuccess == False) and (Timeout > TimeCount):
                            # obj.updateNeeded.value = False
                            writeSuccess = obj.set_update_flag( node, False )
                            TimeCount += 1
                    return ret
                    
    #
    # send a linked list object as a PARAM_EXT_VALUE over mavlink
    #
    def sendMavlinkMessageForParamExtLinkedList( self, obj, the_connection, no_of_std_obj, Timeout=5 ):

        for node in range(0, LinkedListMemory.numberOfVals):
            if (obj.get_ack_send( node ) == True):  
        
                # send mavlink message  obj.name obj.payload.value obj.numberOfVals      
                #
                getValueforMAVSending, getPrev, getName = obj.get_all( node ) 
                print(f"-------------- obj update found for param_value {getName} {getValueforMAVSending} {getPrev}")
                if not (getValueforMAVSending == None):
                    try:
                        the_connection.mav.param_ext_value_send(
                            getName.encode('utf-8'),
                            str(getValueforMAVSending).encode('utf-8'),
                            mavdefs.MAV_PARAM_EXT_TYPE_UINT32,
                            obj.numberOfVals + no_of_std_obj,
                            obj.get_index(node) + no_of_std_obj)
                        ret = True
                    except Exception as err_msg:
                        print("Failed to send param value message : %s" % (err_msg))
                        ret = False
                    if (ret == True):
                        writeSuccess = False
                        TimeCount = 0
                        while (writeSuccess == False) and (Timeout > TimeCount):
                            # obj.updateNeeded.value = False
                            writeSuccess = obj.set_ack_send( node, False )
                            TimeCount += 1
                    return ret
#
# ============================================================= multi-process threads =====================================================================
#                               Camera Action Routines
#                               Mavlink Response Signals
#
        
async def doAlphaCameraExpro( mySonyCam, mav2SonyVals, expro, tm_upd_disable=False, time_delta = 1000 ):
    """asyncio wrapper for performing exposure program control"""
    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_EX_PRO
        
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
    if ((timenow - expro.timestamp.value) > time_delta):
        if (mySonyCam.getSonyCamExProData( expro )==True):
            with expro.timestamp.get_lock():
                expro.timestamp.value = timenow

    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_IDLE
        #print(f"\033[36m Time Delta occurred {timenow} {expro.timestamp.value}")
    #else:
        #print(f"\033[34m No time diff {timenow} {expro.timestamp.value}")
    print ('Exiting Exposure Program :', multiprocessing.current_process().name)
    
async def sendMavExpro( mySonyCam, expro, ConnID ):
    """asyncio wrapper for sending exposure program mode setting over mavlink"""
    p = multiprocessing.current_process()
    print ('Starting Exposure Program:', p.name, p.pid)
    success = mySonyCam.sendMavlinkMessageForParamObject( expro, ConnID )
    success = mySonyCam.sendMavlinkMessageForParamExtObject( expro, ConnID )
    print ('Exiting Exposure Program :', multiprocessing.current_process().name)             

async def doAlphaCameraAperture( mySonyCam, mav2SonyVals, aper, tm_upd_disable=False, time_delta = 1000 ):
    """asyncio wrapper for performing aperture control"""
    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_APER
        
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

    if ((timenow - aper.timestamp.value) > time_delta):
        if (mySonyCam.getSonyApertureData( aper )==True):
            with aper.timestamp.get_lock():
                aper.timestamp.value = timenow
                
    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_IDLE
        
    print ('Exiting  Aperture :', multiprocessing.current_process().name)
    
async def sendMavAper( mySonyCam, aper, ConnID ):
    """asyncio wrapper for sending aperture setting over mavlink"""
    p = multiprocessing.current_process()
    print ('Starting Mavlink Aperture :', p.name, p.pid)
    success = mySonyCam.sendMavlinkMessageForParamObject( aper, ConnID )
    success = mySonyCam.sendMavlinkMessageForParamExtObject( aper, ConnID )
    print ('Exiting Mavlink Aperture :', multiprocessing.current_process().name)
    
async def doAlphaCameraFocusData( mySonyCam, mav2SonyVals, focusdata, focusarea, tm_upd_disable=False, time_delta = 1000 ):
    """asyncio wrapper for performing focus mode control"""
    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_FOCUS
        
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
    if ((timenow - focusdata.timestamp.value) > time_delta):
        if (mySonyCam.getSonyCamFocusData( focusdata )==True):
            with focusdata.timestamp.get_lock():
                focusdata.timestamp.value = timenow

    if ((timenow - focusarea.timestamp.value) > time_delta):
        if (mySonyCam.getSonyCamFocusAreaData( focusarea )==True):
            with focusarea.timestamp.get_lock():
                focusarea.timestamp.value = timenow

    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_IDLE
    print ('Exiting Focus :', multiprocessing.current_process().name)
    
async def sendMavFocusData( mySonyCam, focusdata, focusarea, ConnID ):
    """asyncio wrapper for sending focus data setting over mavlink"""
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

    
async def doAlphaCameraIso( mySonyCam, mav2SonyVals, iso, retries=3, tm_upd_disable=False, time_delta = 1000 ):
    """asyncio wrapper for performing iso control"""
    p = multiprocessing.current_process()
    print ('Starting ISO set :', p.name, p.pid)

    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_ISO
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
    if ((timenow - iso.timestamp.value) > time_delta):
        if (mySonyCam.getSonyCamISOData( iso )==True):
            print(f"\033[36;45m ISO timeupdate required @ {iso.timestamp.value} {timenow}")
            with iso.timestamp.get_lock():
                iso.timestamp.value = timenow
                
    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_IDLE
    print ('Exiting ISO Set :', multiprocessing.current_process().name)
    
async def sendMavIso( mySonyCam, iso, ConnID ):
    """asyncio wrapper for sending iso setting over mavlink"""
    p = multiprocessing.current_process()
    print ('Starting ISO :', p.name, p.pid)
    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    #     
    success = mySonyCam.sendMavlinkMessageForParamObject( iso, ConnID )
    success = mySonyCam.sendMavlinkMessageForParamExtObject( iso, ConnID )
    print ('Exiting ISO :', multiprocessing.current_process().name)   
    
async def doAlphaCameraShutSpd( mySonyCam, mav2SonyVals, shut_sp, tm_upd_disable=False, time_delta = 1000 ):
    """asyncio wrapper for performing shutter speed control"""
    p = multiprocessing.current_process()
    print ('Starting Shutter Speed :', p.name, p.pid)

    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_SS    
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
    if ((timenow - shut_sp.timestamp.value) > time_delta):
        if (mySonyCam.getSonyCamShutSpdData( shut_sp )==True):
            with shut_sp.timestamp.get_lock():
                shut_sp.timestamp.value = timenow   
                
    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_IDLE                
    print ('Exiting Shutter Speed :', multiprocessing.current_process().name)

async def doRedExposure( myMicaCam, mav2SonyVals, expos_obj ):
    """asyncio wrapper for performing micaSense exposure adjustment via the HTTP API"""
    p = multiprocessing.current_process()
    print ('Starting micaSense exposure change :', p.name, p.pid)

    #with mav2SonyVals.mp_state.get_lock():
    #   mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_SS    
    #
    # initialise general program control flags
    #
    success = 0
    code = 0

    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    #
    success, code = myMicaCam.micaSenseSetExposureFromMav( mav2SonyVals )
    if (success == myMicaCam.HTTP_SUCCESS_RETURN):
        with prev_mica_exposure.get_lock():
            mav2SonyVals.prev_mica_exposure.exp1 = mav2SonyVals.set_mica_exposure.exp1
            mav2SonyVals.prev_mica_exposure.exp2 = mav2SonyVals.set_mica_exposure.exp2
            mav2SonyVals.prev_mica_exposure.exp3 = mav2SonyVals.set_mica_exposure.exp3
            mav2SonyVals.prev_mica_exposure.exp4 = mav2SonyVals.set_mica_exposure.exp4
            mav2SonyVals.prev_mica_exposure.exp5 = mav2SonyVals.set_mica_exposure.exp5
            mav2SonyVals.prev_mica_exposure.gain1 = mav2SonyVals.set_mica_exposure.gain1
            mav2SonyVals.prev_mica_exposure.gain2 = mav2SonyVals.set_mica_exposure.gain2
            mav2SonyVals.prev_mica_exposure.gain3 = mav2SonyVals.set_mica_exposure.gain3
            mav2SonyVals.prev_mica_exposure.gain4 = mav2SonyVals.set_mica_exposure.gain4
            mav2SonyVals.prev_mica_exposure.gain5 = mav2SonyVals.set_mica_exposure.gain5
        expos_obj.set_value(0, mav2SonyVals.set_mica_exposure.exp1)
        expos_obj.set_value(1, mav2SonyVals.set_mica_exposure.exp2)
        expos_obj.set_value(2, mav2SonyVals.set_mica_exposure.exp3)
        expos_obj.set_value(3, mav2SonyVals.set_mica_exposure.exp4)
        expos_obj.set_value(4, mav2SonyVals.set_mica_exposure.exp5)
        expos_obj.set_value(5, mav2SonyVals.set_mica_exposure.gain1)
        expos_obj.set_value(6, mav2SonyVals.set_mica_exposure.gain2)
        expos_obj.set_value(7, mav2SonyVals.set_mica_exposure.gain3)
        expos_obj.set_value(8, mav2SonyVals.set_mica_exposure.gain4)
        expos_obj.set_value(9, mav2SonyVals.set_mica_exposure.gain5)
        for node in range(0,10):
            expos_obj.set_update_flag(node, True)
    else:
        with set_mica_exposure.get_lock():    
            mav2SonyVals.set_mica_exposure.exp1 = mav2SonyVals.prev_mica_exposure.exp1
            mav2SonyVals.set_mica_exposure.exp2 = mav2SonyVals.prev_mica_exposure.exp2
            mav2SonyVals.set_mica_exposure.exp3 = mav2SonyVals.prev_mica_exposure.exp3
            mav2SonyVals.set_mica_exposure.exp4 = mav2SonyVals.prev_mica_exposure.exp4
            mav2SonyVals.set_mica_exposure.exp5 = mav2SonyVals.prev_mica_exposure.exp5
            mav2SonyVals.set_mica_exposure.gain1 = mav2SonyVals.prev_mica_exposure.gain1
            mav2SonyVals.set_mica_exposure.gain2 = mav2SonyVals.prev_mica_exposure.gain2
            mav2SonyVals.set_mica_exposure.gain3 = mav2SonyVals.prev_mica_exposure.gain3
            mav2SonyVals.set_mica_exposure.gain4 = mav2SonyVals.prev_mica_exposure.gain4
            mav2SonyVals.set_mica_exposure.gain5 = mav2SonyVals.prev_mica_exposure.gain5    
              
    print ('Exiting micaSense set exposure :', multiprocessing.current_process().name)
    
async def sendMavShutSpd( mySonyCam, shut_sp, ConnID ):
    """asyncio wrapper for sending shutter speed setting over mavlink"""
    p = multiprocessing.current_process()
    print ('Starting Mavlink Shutter Speed :', p.name, p.pid)
    #
    # check to see if mavlink wrote something if so write to cam
    # and update the update flag to get the mavlink send
    #     
    success = mySonyCam.sendMavlinkMessageForParamObject( shut_sp, ConnID )
    success = mySonyCam.sendMavlinkMessageForParamExtObject( shut_sp, ConnID )
    print ('Exiting Mavlink Shutter Speed :', multiprocessing.current_process().name)
    
async def doAlphaWhiteBala( mySonyCam, mav2SonyVals, whitebal, tm_upd_disable=False, time_delta = 1000 ):
    """asyncio wrapper for performing white balance control"""
    p = multiprocessing.current_process()
    print ('Starting White Balance :', p.name, p.pid)

    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_WB      
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
    if ((timenow - whitebal.timestamp.value) > time_delta):
        if (mySonyCam.getSonyCamWhiteBalaData( whitebal )==True):
            with whitebal.timestamp.get_lock():
                whitebal.timestamp.value = timenow 

    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_IDLE  
    print ('Exiting White Balance :', multiprocessing.current_process().name)
    
async def sendMavWhiteBala( mySonyCam, whitebal, ConnID ):
    """asyncio wrapper for sending white balance setting over mavlink"""
    p = multiprocessing.current_process()
    print ('Starting Mavlink White Balance :', p.name, p.pid)
    success = mySonyCam.sendMavlinkMessageForParamObject( whitebal, ConnID )  
    success = mySonyCam.sendMavlinkMessageForParamExtObject( whitebal, ConnID )     
    print ('Exiting Mavlink White Balance :', multiprocessing.current_process().name)    
    
async def doAlphaCameraStillCap( mySonyCam, mav2SonyVals, stillcap, tm_upd_disable=False, time_delta = 1000 ):
    """asyncio wrapper for performing still capture mode control"""
    #
    # initialise general program control flags
    #
    success = False
    timenow = 0

    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_SC 
        
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
    if ((timenow - stillcap.timestamp.value) > time_delta):
        if (mySonyCam.getSonyCamStillCapModeData( stillcap )==True):
            with stillcap.timestamp.get_lock():
                stillcap.timestamp.value = timenow 

    with mav2SonyVals.mp_state.get_lock():
        mav2SonyVals.mp_state.value = mavlinkSonyCamWriteVals.FUNC_IDLE 
    print ('Exiting Still Capture :', multiprocessing.current_process().name)


# -------------------------------- SEQUENTIAL ------------------------------------------------------------------------------
#
# These tasks runs sequentially the camera actions and interface back with the scheduler 
#       
def manageAlphaCameraExpro( cam, classObj, pvar, mpc, state_of_task ):
    """asyncio wrapper for managing exposure proram setting changes over mavlink"""
    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING

    doAlphaCameraExpro( cam, classObj, pvar )

    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_APER
    print(f"Task1:: Expro {pvar}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY    

#
# this task runs sequentially and doesnt set the variables (attributes) of the class passed to it.
#       
def manageAlphaCameraAperture( cam, classObj, pvar, mpc, state_of_task ):
    """asyncio wrapper for managing aperture setting changes over mavlink"""
    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING

    doAlphaCameraAperture( cam, classObj, pvar )

    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_FOCUS
    print(f"Task2:: Aperture {pvar}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         

def manageAlphaCameraFocusData( cam, classObj, pvar, c, mpc, state_of_task ):
    """asyncio wrapper for managing focus data setting changes over mavlink"""
    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING

    doAlphaCameraFocusData( cam, classObj, pvar, c )
    
    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_ISO
    print(f"Task3:: Focus parameters {pvar}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         

def manageAlphaCameraIso( cam, classObj, pvar, mpc, state_of_task ):
    """asyncio wrapper for managing iso setting changes over mavlink"""
    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING

    doAlphaCameraIso( cam, classObj, pvar )
    
    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_SS
    print(f"Task4:: Iso {pvar}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         

def manageAlphaCameraShutSpd( cam, classObj, pvar, mpc, state_of_task ):
    """asyncio wrapper for managing shutter speed setting changes over mavlink"""
    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING

    doAlphaCameraShutSpd( cam, classObj, pvar )

    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_WB
    print(f"Task5:: Shutter Speed {pvar}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         

def manageAlphaWhiteBala( cam, classObj, pvar, mpc, state_of_task ):
    """asyncio wrapper for managing white balance setting changes over mavlink"""
    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING

    doAlphaWhiteBala( cam, classObj, pvar )

    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_SC
    print(f"Task6:: White Balance {pvar}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         

def manageAlphaCameraStillCap( cam, classObj, pvar, mpc, state_of_task ):
    """asyncio wrapper for managing still capture mode setting changes over mavlink """
    state_of_task.value = mavlinkSonyCamWriteVals.STATE_CAM_WRITING

    doAlphaCameraStillCap( cam, classObj, pvar )

    with mpc.get_lock():
        mpc.value = mavlinkSonyCamWriteVals.FUNC_EX_PRO
    print(f"Task7:: Still Capture {pvar}")
    # advance to the next routine in the queued sequence
    with state_of_task.get_lock():
        state_of_task.value = mavlinkSonyCamWriteVals.STATE_READY         

async def sendMavCamChoice( mySonyCam, cam_selection, ConnID ): 
    """asyncio wrapper for sending camera choice information over mavlink"""
    p = multiprocessing.current_process()
    print ('Starting Mavlink Camera Choice :', p.name, p.pid)   
    success = mySonyCam.sendMavlinkMessageForParamObject( cam_selection, ConnID )  
    success = mySonyCam.sendMavlinkMessageForParamExtObject( cam_selection, ConnID )     
    print ('Exiting Mavlink Camera Choice :', multiprocessing.current_process().name) #
    
async def sendMavStillCap( mySonyCam, stillcap, ConnID ): 
    """asyncio wrapper for sending still capture mode information over mavlink"""
    p = multiprocessing.current_process()
    print ('Starting Mavlink Still Capture :', p.name, p.pid)   
    success = mySonyCam.sendMavlinkMessageForParamObject( stillcap, ConnID )  
    success = mySonyCam.sendMavlinkMessageForParamExtObject( stillcap, ConnID )     
    print ('Exiting Mavlink Still Capture :', multiprocessing.current_process().name) #

async def sendMavCamChoice( mySonyCam, cam_chosen, ConnID ): 
    """asyncio wrapper for sending camera chocie information over mavlink"""
    p = multiprocessing.current_process()
    print ('Starting Mavlink Camera Choice :', p.name, p.pid)   
    success = mySonyCam.sendMavlinkMessageForParamObject( cam_chosen, ConnID )  
    success = mySonyCam.sendMavlinkMessageForParamExtObject( cam_chosen, ConnID )     
    print ('Exiting Mavlink Camera Choice :', multiprocessing.current_process().name) #
    
async def sendMavRedExpos( mav_class, re_obj, ConnID ): 
    """asyncio wrapper for sending micaSense expsoure information over mavlink"""
    p = multiprocessing.current_process()
    print ('Starting Mavlink RedEdge Exposure :', p.name, p.pid) 
    success = mav_class.sendMavlinkMessageForParamLinkedList(re_obj, ConnID, memoryValue.numberOfVals) 
    success = mav_class.sendMavlinkMessageForParamExtLinkedList(re_obj, ConnID, memoryValue.numberOfVals)           
    print ('Exiting Mavlink RedEdge Exposure :', multiprocessing.current_process().name) #

async def setRedShutterSpd( mav_class, serial_mica_handle, shutter_speed_req ): 
    """asyncio wrapper for sending micaSense shutter speed over serial mavlink"""
    # to send shutter speed value to the camera TODO :: add timeout wrapper
    msg = serial_mica_handle.recv_match(type='HEARTBEAT', blocking=True)
    mav_class.mavlink_do_digicam_configure_old(serial_mica_handle, shutter_speed_req)
    
# EXT param is just read directly from memory and sent back for speed
#
def mavlinkExtReqGetParam(  mySonyCam, obj ):
    """handle gcs request ext_param get"""
    with obj.updateNeeded.get_lock():
        obj.updateNeeded.value = True
    with obj.timestamp.get_lock():
        obj.timestamp.value = mySonyCam.my_timestamp()
        return True
        
def mavlinkReqGetParamStillCap(  mySonyCam, obj ):
    """handle gcs request for still capture mode"""
    if (mySonyCam.getSonyCamStillCapModeData( obj )==True):
        with obj.timestamp.get_lock():
            obj.timestamp.value = mySonyCam.my_timestamp()
        return True
    else:
        return False
        
def mavlinkReqGetParamWhiteBala(  mySonyCam, obj ):
    """handle gcs request for white balance"""
    if (mySonyCam.getSonyCamWhiteBalaData( obj )==True):
        with obj.timestamp.get_lock():    
            obj.timestamp.value  = mySonyCam.my_timestamp()
        return True
    else:
        return False
        
def mavlinkReqGetParamShutSpd(  mySonyCam, obj ):
    """handle gcs request for shutter speed"""
    if (mySonyCam.getSonyCamShutSpdData( obj )==True):
        with obj.timestamp.get_lock():    
            obj.timestamp.value  = mySonyCam.my_timestamp()
        return True
    else:
        return False
        
def mavlinkReqGetParamIso(  mySonyCam, obj ):
    """handle gcs request for iso"""
    if (mySonyCam.getSonyCamISOData( obj )==True):
        with obj.timestamp.get_lock():    
            obj.timestamp.value  = mySonyCam.my_timestamp()
        return True
    else:
        return False
        
def mavlinkReqGetParamFocus(  mySonyCam, obj ):
    """handle gcs request for focus"""
    if (mySonyCam.getSonyCamFocusData( obj )==True):
        with obj.timestamp.get_lock():    
            obj.timestamp.value  = mySonyCam.my_timestamp()
        return True
    else:
        return False
        
def mavlinkReqGetParamFocusArea(  mySonyCam, obj ):
    """handle gcs request for focus area"""
    if (mySonyCam.getSonyCamFocusAreaData( obj )==True):
        with obj.timestamp.get_lock():    
            obj.timestamp.value  = mySonyCam.my_timestamp()
        return True
    else:
        return False
        
def mavlinkReqGetParamAperture(  mySonyCam, obj ):
    """handle gcs request for aperture"""
    if (mySonyCam.getSonyApertureData( obj )==True):
        with obj.timestamp.get_lock():    
            obj.timestamp.value  = mySonyCam.my_timestamp()
        return True
    else:
        return False
        
def mavlinkReqGetParamExPro(  mySonyCam, obj ):
    """handle gcs request for expro"""
    if (mySonyCam.getSonyCamExProData( obj )==True):
        with obj.timestamp.get_lock():    
            obj.timestamp.value  = mySonyCam.my_timestamp()
        return True
    else:
        return False

def mavlinkReqGetParamRedExpos(  myRedEdge, re_obj ):
    """handle gcs request for exposure data from RedEdge Camera """
    json_out = myRedEdge.micaSenseGetExposure()
    if (len(json_out) > 0):
        re_obj.set_value(0, json_out['exposure1'])
        re_obj.set_value(1, json_out['exposure2'])
        re_obj.set_value(2, json_out['exposure3'])
        re_obj.set_value(3, json_out['exposure4'])
        re_obj.set_value(4, json_out['exposure5'])
        re_obj.set_value(5, json_out['gain1'])
        re_obj.set_value(6, json_out['gain2'])
        re_obj.set_value(7, json_out['gain3'])
        re_obj.set_value(8, json_out['gain4'])
        re_obj.set_value(9, json_out['gain5'])
        for box in range(0,10):
            re_obj.set_update_flag(box, True)
            re_obj.set_timestamp(box, libc.time(None))
        return True
    else:
        return False
        
def mavlinkTakePhoto( mySonyCam, flg ):
    """takes a photo on the sony camera"""
    return (mySonyCam.take_a_picture_now(flg))                 
    
def get_cam_enum( nameS ):
    """gets the enum from a name"""
    for s in sorted(camStateClass):
        if not s.name.find(nameS) == -1:
            return s.value
    return -1
    
def serviceParamRequestsOneAtATime( mySonyCam, mav2SonyVals, stcap, wb, ss, iso, pf, pfa, pa, expro, myRedCam, ms_expos, camera_choice ):
    """wrapper for asyncio to service parameter change requests"""
    p = multiprocessing.current_process()
    print ('Starting Service Mavlink incoming request packets ONE AT A TIME :', p.name, p.pid)

    if not (mav2SonyVals.mav_req_all_param.value == 0) and not (mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM == mav2SonyVals.mav_ext_req_all_param.value):
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamStillCap)) == 0):   
            stcap.set_update_flag( True, memoryValue.STATE_MAV_WRITING )
            if (mavlinkReqGetParamStillCap(  mySonyCam, stcap ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamStillCap                
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamWhiteBala)) == 0):  
            wb.set_update_flag( True, memoryValue.STATE_MAV_WRITING )        
            if (mavlinkReqGetParamWhiteBala(  mySonyCam, wb ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamWhiteBala               
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamShutSpd)) == 0):   
            ss.set_update_flag( True, memoryValue.STATE_MAV_WRITING )  
            if (mavlinkReqGetParamShutSpd(  mySonyCam, ss ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamShutSpd             
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamIso)) == 0):  
            iso.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          
            if (mavlinkReqGetParamIso(  mySonyCam, iso ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamIso 
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamFocus)) == 0):   
            pf.set_update_flag( True, memoryValue.STATE_MAV_WRITING )   
            if (mavlinkReqGetParamFocus(  mySonyCam, pf ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamFocus 
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamFocusArea)) == 0): 
            pfa.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          
            if (mavlinkReqGetParamFocusArea(  mySonyCam, pfa ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamFocusArea 
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamAperture)) == 0): 
            pa.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          
            if (mavlinkReqGetParamAperture(  mySonyCam, pa ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamAperture 
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPro)) == 0):  
            expro.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamExPro(  mySonyCam, expro ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamExPro
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamCamChoice)) == 0):  
            camera_choice.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamExPro(  mySonyCam, camera_choice ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamCamChoice
                    
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos1)) == 0):  
            ms_expos.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos2)) == 0):  
            ms_expos.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos3)) == 0):  
            ms_expos.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos4)) == 0):  
            ms_expos.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos5)) == 0):  
            ms_expos.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain1)) == 0):  
            ms_expos.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain1)) == 0):  
            ms_expos.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain2)) == 0):  
            ms_expos.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain3)) == 0):  
            ms_expos.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain4)) == 0):  
            ms_expos.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain5)) == 0):  
            ms_expos.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           
            if (mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
                    
    if not (mav2SonyVals.mav_ext_req_all_param.value == 0) and not (mav2SonyVals.mav_ext_req_all_param.value == mavlinkSonyCamWriteVals.MAV_REQ_ALL_PARAM):
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamStillCap)) == 0): 
            stcap.set_ack_send( True, memoryValue.STATE_MAV_WRITING )        
            if ( mavlinkReqGetParamStillCap(  mySonyCam, stcap ) == True ):
                if ( stcap.set_ack_send( True, stcap.STATE_CAM_READING ) == True ):                                                      # additional PARAM_EXT_VALUE message requested
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamStillCap                
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamWhiteBala)) == 0):   
            wb.set_ack_send( True, memoryValue.STATE_MAV_WRITING )  
            if ( mavlinkReqGetParamWhiteBala(  mySonyCam, wb ) == True ):
                if ( wb.set_ack_send( True, wb.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested            
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamWhiteBala               
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamShutSpd)) == 0):  
            ss.set_ack_send( True, memoryValue.STATE_MAV_WRITING )          
            if ( mavlinkReqGetParamShutSpd(  mySonyCam, ss ) == True ):
                if ( ss.set_ack_send( True, ss.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested                   
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamShutSpd             
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamIso)) == 0):   
            iso.set_ack_send( True, memoryValue.STATE_MAV_WRITING )         
            if ( mavlinkReqGetParamIso(  mySonyCam, iso ) == True ):
                if ( iso.set_ack_send( True, iso.STATE_CAM_READING ) == True ):                                                          # additional PARAM_EXT_VALUE message requested                  
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamIso 
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamFocus)) == 0):  
            pf.set_ack_send( True, memoryValue.STATE_MAV_WRITING )           
            if ( mavlinkReqGetParamFocus(  mySonyCam, pf ) == True ):
                if ( pf.set_ack_send( True, pf.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested                 
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamFocus 
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamFocusArea)) == 0):  
            pfa.set_ack_send( True, memoryValue.STATE_MAV_WRITING )          
            if ( mavlinkReqGetParamFocusArea(  mySonyCam, pfa ) == True ):
                if ( pfa.set_ack_send( True, pfa.STATE_CAM_READING ) == True ):                                                          # additional PARAM_EXT_VALUE message requested                 
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamFocusArea 
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamAperture)) == 0):   
            pa.set_ack_send( True, memoryValue.STATE_MAV_WRITING ) 
            if ( mavlinkReqGetParamAperture(  mySonyCam, pa ) == True ):
                if ( pa.set_ack_send( True, pa.STATE_CAM_READING ) == True ):                                                           # additional PARAM_EXT_VALUE message requested              
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamAperture 
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPro)) == 0): 
            expro.set_ack_send( True, memoryValue.STATE_MAV_WRITING )         
            if ( mavlinkReqGetParamExPro(  mySonyCam, expro ) == True ):
                if ( expro.set_ack_send( True, expro.STATE_CAM_READING ) == True ):                                                      # additional PARAM_EXT_VALUE message requested               
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamExPro
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamCamChoice)) == 0): 
            camera_choice.set_ack_send( True, memoryValue.STATE_MAV_WRITING )         
            if ( mavlinkReqGetParamExPro(  mySonyCam, camera_choice ) == True ):
                if ( camera_choice.set_ack_send( True, camera_choice.STATE_CAM_READING ) == True ):                                                      # additional PARAM_EXT_VALUE message requested               
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamCamChoice
                        
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos1)) == 0): 
            ms_expos.set_ack_send( 0, True )         
            if ( mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True ):
                    for box in range(0,10):
                        ms_expos.set_ack_send( box, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos1)) == 0): 
            ms_expos.set_ack_send( 0, True )         
            if ( mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True ):
                    for box in range(0,10):
                        ms_expos.set_ack_send( box, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)               
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos2)) == 0): 
            ms_expos.set_ack_send( 1, True )         
            if ( mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True ):
                    for box in range(0,10):
                        ms_expos.set_ack_send( box, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)                
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos3)) == 0): 
            ms_expos.set_ack_send( 2, True )         
            if ( mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True ):
                    for box in range(0,10):
                        ms_expos.set_ack_send( box, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos4)) == 0): 
            ms_expos.set_ack_send( 3, True )         
            if ( mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True ):
                    for box in range(0,10):
                        ms_expos.set_ack_send( box, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos5)) == 0): 
            ms_expos.set_ack_send( 4, True )         
            if ( mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True ):
                    for box in range(0,10):
                        ms_expos.set_ack_send( box, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)               
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain1)) == 0): 
            ms_expos.set_ack_send( 5, True )         
            if ( mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True ):
                    for box in range(0,10):
                        ms_expos.set_ack_send( box, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)               
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain2)) == 0): 
            ms_expos.set_ack_send( 6, True )         
            if ( mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True ):
                    for box in range(0,10):
                        ms_expos.set_ack_send( box, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)               
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain3)) == 0): 
            ms_expos.set_ack_send( 7, True )         
            if ( mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True ):
                    for box in range(0,10):
                        ms_expos.set_ack_send( box, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)               
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain4)) == 0): 
            ms_expos.set_ack_send( 8, True )         
            if ( mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True ):
                    for box in range(0,10):
                        ms_expos.set_ack_send( box, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)               
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain5)) == 0): 
            ms_expos.set_ack_send( 9, True )         
            if ( mavlinkReqGetParamRedExpos(  myRedCam, ms_expos ) == True ):
                    for box in range(0,10):
                        ms_expos.set_ack_send( box, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)               
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
                                            
                      
    print ('Exiting Service Mavlink incoming packet requests :', multiprocessing.current_process().name) #

async def serviceParamRequests( mySonyCam, mav2SonyVals, stcap, wb, ss, iso, pf, pfa, pa, expro, redCam, re_expos, camera_choice ):
    """wrapper for asyncio to service parameter change requests"""
    p = multiprocessing.current_process()
    print ('Starting Service Mavlink incoming request packets :', p.name, p.pid)

    if not (mav2SonyVals.mav_req_all_param.value == 0):
    
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamStillCap)) == 0):   
            stcap.set_update_flag( True, memoryValue.STATE_MAV_WRITING )
                
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamWhiteBala)) == 0):  
            wb.set_update_flag( True, memoryValue.STATE_MAV_WRITING )        
             
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamShutSpd)) == 0):   
            ss.set_update_flag( True, memoryValue.STATE_MAV_WRITING )  
         
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamIso)) == 0):  
            iso.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamFocus)) == 0):   
            pf.set_update_flag( True, memoryValue.STATE_MAV_WRITING )   

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamFocusArea)) == 0): 
            pfa.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamAperture)) == 0): 
            pa.set_update_flag( True, memoryValue.STATE_MAV_WRITING )          

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPro)) == 0):  
            expro.set_update_flag( True, memoryValue.STATE_MAV_WRITING )           

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamCamChoice)) == 0):  
            camera_choice.set_update_flag( True, memoryValue.STATE_MAV_WRITING )  
            
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos1)) == 0):  
            re_expos.set_update_flag( 0, True ) 

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos2)) == 0):  
            re_expos.set_update_flag( 1, True ) 

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos3)) == 0):  
            re_expos.set_update_flag( 2, True ) 

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos4)) == 0):  
            re_expos.set_update_flag( 3, True ) 

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos5)) == 0):  
            re_expos.set_update_flag( 4, True ) 

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain1)) == 0):  
            re_expos.set_update_flag( 5, True ) 

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain2)) == 0):  
            re_expos.set_update_flag( 6, True ) 

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain3)) == 0):  
            re_expos.set_update_flag( 7, True ) 

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain4)) == 0):  
            re_expos.set_update_flag( 8, True ) 

        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain5)) == 0):  
            re_expos.set_update_flag( 9, True ) 
            
    if not (mav2SonyVals.mav_ext_req_all_param.value == 0):
    
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamStillCap)) == 0): 
            stcap.set_ack_send( True, memoryValue.STATE_MAV_WRITING )        
               
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamWhiteBala)) == 0):   
            wb.set_ack_send( True, memoryValue.STATE_MAV_WRITING )  
              
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamShutSpd)) == 0):  
            ss.set_ack_send( True, memoryValue.STATE_MAV_WRITING )          
          
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamIso)) == 0):   
            iso.set_ack_send( True, memoryValue.STATE_MAV_WRITING )         

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamFocus)) == 0):  
            pf.set_ack_send( True, memoryValue.STATE_MAV_WRITING )           

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamFocusArea)) == 0):  
            pfa.set_ack_send( True, memoryValue.STATE_MAV_WRITING )          

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamAperture)) == 0):   
            pa.set_ack_send( True, memoryValue.STATE_MAV_WRITING ) 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPro)) == 0): 
            expro.set_ack_send( True, memoryValue.STATE_MAV_WRITING )  

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamCamChoice)) == 0): 
            camera_choice.set_ack_send( True, memoryValue.STATE_MAV_WRITING ) 
            
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos1)) == 0): 
            re_expos.set_ack_send( 0, True ) 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos2)) == 0): 
            re_expos.set_ack_send( 1, True ) 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos3)) == 0): 
            re_expos.set_ack_send( 2, True ) 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos4)) == 0): 
            re_expos.set_ack_send( 3, True ) 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos5)) == 0): 
            re_expos.set_ack_send( 4, True ) 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain1)) == 0): 
            re_expos.set_ack_send( 5, True ) 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain2)) == 0): 
            re_expos.set_ack_send( 6, True ) 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain3)) == 0): 
            re_expos.set_ack_send( 7, True ) 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain4)) == 0): 
            re_expos.set_ack_send( 8, True ) 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain5)) == 0): 
            re_expos.set_ack_send( 9, True )
            
    if not (mav2SonyVals.mav_req_all_param.value == 0):
    
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamStillCap)) == 0): 
            if (mavlinkExtReqGetParam(  mySonyCam, stcap ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamStillCap 
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamWhiteBala)) == 0):  
            if (mavlinkExtReqGetParam(  mySonyCam, wb ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamWhiteBala  
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamShutSpd)) == 0):  
            if (mavlinkExtReqGetParam(  mySonyCam, ss ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamShutSpd    
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamIso)) == 0):  
            if (mavlinkExtReqGetParam(  mySonyCam, iso ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamIso 
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamFocus)) == 0):   
            if (mavlinkExtReqGetParam(  mySonyCam, pf ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamFocus 
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamFocusArea)) == 0): 
            if (mavlinkExtReqGetParam(  mySonyCam, pfa ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamFocusArea 
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamAperture)) == 0): 
            if (mavlinkExtReqGetParam(  mySonyCam, pa ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamAperture 
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPro)) == 0):  
            if (mavlinkExtReqGetParam(  mySonyCam, expro ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamExPro   
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamCamChoice)) == 0):  
            if (mavlinkExtReqGetParam(  mySonyCam, camera_choice ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~mav2SonyVals.ParamCamChoice  
                    
        if not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos1)) == 0):  
            if (mavlinkReqGetParamRedExpos(  redCam, re_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos2)) == 0):  
            if (mavlinkReqGetParamRedExpos(  redCam, re_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos3)) == 0):  
            if (mavlinkReqGetParamRedExpos(  redCam, re_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos4)) == 0):  
            if (mavlinkReqGetParamRedExpos(  redCam, re_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExPos5)) == 0):  
            if (mavlinkReqGetParamRedExpos(  redCam, re_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain1)) == 0):  
            if (mavlinkReqGetParamRedExpos(  redCam, re_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain2)) == 0):  
            if (mavlinkReqGetParamRedExpos(  redCam, re_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain3)) == 0):  
            if (mavlinkReqGetParamRedExpos(  redCam, re_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain4)) == 0):  
            if (mavlinkReqGetParamRedExpos(  redCam, re_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_req_all_param.value) & int(mav2SonyVals.ParamExGain5)) == 0):  
            if (mavlinkReqGetParamRedExpos(  redCam, re_expos ) == True):
                with mav2SonyVals.mav_req_all_param.get_lock():
                    mav2SonyVals.mav_req_all_param.value = mav2SonyVals.mav_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
                                                                                                                                                      
                   

    # QGC does not work like Mission Planner it may send this message many times
    # therefore request has been made to report back the obkect state rather than obtaining the data from the camera
    #
    if not (mav2SonyVals.mav_ext_req_all_param.value == 0):
    
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamStillCap)) == 0): 
            if ( mavlinkExtReqGetParam( mySonyCam, stcap ) == True ):
                if ( stcap.set_ack_send( True, stcap.STATE_CAM_READING ) == True ):                                                      # additional PARAM_EXT_VALUE message requested
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamStillCap          

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamWhiteBala)) == 0): 
            if ( mavlinkExtReqGetParam( mySonyCam, wb ) == True ):
                if ( wb.set_ack_send( True, wb.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested            
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamWhiteBala 
                    
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamShutSpd)) == 0):  
            if ( mavlinkExtReqGetParam( mySonyCam, ss ) == True ):
                if ( ss.set_ack_send( True, ss.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested                   
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamShutSpd   

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamIso)) == 0):   
            if ( mavlinkExtReqGetParam( mySonyCam, iso ) == True ):
                if ( iso.set_ack_send( True, iso.STATE_CAM_READING ) == True ):                                                          # additional PARAM_EXT_VALUE message requested                  
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamIso 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamFocus)) == 0):  
            if ( mavlinkExtReqGetParam( mySonyCam, pf ) == True ):
                if ( pf.set_ack_send( True, pf.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested                 
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamFocus 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamFocusArea)) == 0):  
            if ( mavlinkExtReqGetParam( mySonyCam, pfa ) == True ):
                if ( pfa.set_ack_send( True, pfa.STATE_CAM_READING ) == True ):                                                          # additional PARAM_EXT_VALUE message requested                 
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamFocusArea 

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamAperture)) == 0):   
            if ( mavlinkExtReqGetParam( mySonyCam, pa ) == True ):
                if ( pa.set_ack_send( True, pa.STATE_CAM_READING ) == True ):                                                            # additional PARAM_EXT_VALUE message requested              
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamAperture 
                    
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPro)) == 0): 
            if ( mavlinkExtReqGetParam( mySonyCam, expro ) == True ):
                if ( expro.set_ack_send( True, expro.STATE_CAM_READING ) == True ):                                                      # additional PARAM_EXT_VALUE message requested               
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamExPro

        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamCamChoice)) == 0): 
            if ( mavlinkExtReqGetParam( mySonyCam, camera_choice ) == True ):
                if ( camera_choice.set_ack_send( True, camera_choice.STATE_CAM_READING ) == True ):                                                      # additional PARAM_EXT_VALUE message requested               
                    with mav2SonyVals.mav_ext_req_all_param.get_lock():
                        mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~mav2SonyVals.ParamCamChoice
                        
        if not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos1)) == 0): 
            if ( mavlinkReqGetParamRedExpos( redCam, re_expos ) == True ):
                for node in range(0,10):
                    ms_expos.set_ack_send( node, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                with mav2SonyVals.mav_ext_req_all_param.get_lock():
                    mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos2)) == 0): 
            if ( mavlinkReqGetParamRedExpos( redCam, re_expos ) == True ):
                for node in range(0,10):
                    ms_expos.set_ack_send( node, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                with mav2SonyVals.mav_ext_req_all_param.get_lock():
                    mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos3)) == 0): 
            if ( mavlinkReqGetParamRedExpos( redCam, re_expos ) == True ):
                for node in range(0,10):
                    ms_expos.set_ack_send( node, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                with mav2SonyVals.mav_ext_req_all_param.get_lock():
                    mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos4)) == 0): 
            if ( mavlinkReqGetParamRedExpos( redCam, re_expos ) == True ):
                for node in range(0,10):
                    ms_expos.set_ack_send( node, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                with mav2SonyVals.mav_ext_req_all_param.get_lock():
                    mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExPos5)) == 0): 
            if ( mavlinkReqGetParamRedExpos( redCam, re_expos ) == True ):
                for node in range(0,10):
                    ms_expos.set_ack_send( node, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                with mav2SonyVals.mav_ext_req_all_param.get_lock():
                    mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain1)) == 0): 
            if ( mavlinkReqGetParamRedExpos( redCam, re_expos ) == True ):
                for node in range(0,10):
                    ms_expos.set_ack_send( node, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                with mav2SonyVals.mav_ext_req_all_param.get_lock():
                    mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain2)) == 0): 
            if ( mavlinkReqGetParamRedExpos( redCam, re_expos ) == True ):
                for node in range(0,10):
                    ms_expos.set_ack_send( node, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                with mav2SonyVals.mav_ext_req_all_param.get_lock():
                    mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain3)) == 0): 
            if ( mavlinkReqGetParamRedExpos( redCam, re_expos ) == True ):
                for node in range(0,10):
                    ms_expos.set_ack_send( node, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                with mav2SonyVals.mav_ext_req_all_param.get_lock():
                    mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain4)) == 0): 
            if ( mavlinkReqGetParamRedExpos( redCam, re_expos ) == True ):
                for node in range(0,10):
                    ms_expos.set_ack_send( node, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                with mav2SonyVals.mav_ext_req_all_param.get_lock():
                    mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
        elif not ((int(mav2SonyVals.mav_ext_req_all_param.value) & int(mav2SonyVals.ParamExGain5)) == 0): 
            if ( mavlinkReqGetParamRedExpos( redCam, re_expos ) == True ):
                for node in range(0,10):
                    ms_expos.set_ack_send( node, True )                                                 # additional PARAM_EXT_VALUE message requested (do the whole group)              
                with mav2SonyVals.mav_ext_req_all_param.get_lock():
                    mav2SonyVals.mav_ext_req_all_param.value = mav2SonyVals.mav_ext_req_all_param.value & ~(mav2SonyVals.all_mica_expsoure)
                                                                                                            
                        
    print ('Exiting Service Mavlink incoming packet requests :', multiprocessing.current_process().name) #
    
async def run_process_messages_from_connection_single(fra, the_connect, sharedObj, loop=5, redCamera=0):
    """wrapper for asyncio to read messages from mavlink port"""
    fra.process_messages_from_connection(the_connect, sharedObj, loop, redCamera)

#
# @#= delete above after daemon fully tested
#
def run_process_messages_from_connection(fra, the_connect, sharedObj, loop=5, redCamera=0):
    """read messages from mavlink port"""
    while True:
        p = multiprocessing.current_process()
        print ('Starting: MavReader ', p.name, p.pid) 
        fra.process_messages_from_connection(the_connect, sharedObj, loop, redCamera)
        time.sleep(0.2)
        print ('Exiting MavReader :', multiprocessing.current_process().name)
        
# ================ error handler if the camera fails (powers link on off) ============

# uses https://github.com/mvp/uhubctl
#
def reset_usb_camlink():
    """perfrom usb power down/up reset sequence"""
    print("\033[31;43m executing reset usb camera link \033[0m")
    #
    p = os.popen('sudo /home/pi/cams/SonyTEST32/uhubctl/uhubctl -l 1-1 -a 0')
    print(p.read())
    #cmd='sudo /home/pi/cams/SonyTEST32/uhubctl/uhubctl -l 1-1 -a 0' 
    #args = shlex.split(cmd)
    #s=subprocess.run( args, stdout=subprocess.PIPE )
    #output=s.stdout
    #print(output)
    time.sleep(2)
    p = os.popen('sudo /home/pi/cams/SonyTEST32/uhubctl/uhubctl -l 1-1 -a 1')
    print(p.read())
    #cmd='sudo /home/pi/cams/SonyTEST32/uhubctl/uhubctl -l 1-1 -a 1'   
    #args = shlex.split(cmd)
    #s=subprocess.run( args, stdout=subprocess.PIPE )
    #output=s.stdout
    #print(output)
    #
    # had to add this to prevent a Killed occurring - no idea why?
    #
    time.sleep(50)
    print("\033[31m completed reset usb camera link \033[0m")

def perform_usb_reset( mySonyCam ):
    """wrapper for usb power down/up reset sequence"""
    if (mySonyCam.error_counts.value >= 5):  
        reset_usb_camlink()
        with mySonyCam.error_counts.get_lock():
            mySonyCam.error_counts.value = 0    
#
# The heartbeat task that says we are ready
#
async def sendMavlinkHeartBeat_single(fm, cID, sleepTm=1):
    """send heartbeat to say we are ready and waiting"""
    fm.mavlink_send_GCS_heartbeat(cID)
    while sleepTm > 0:
        time.sleep(1)
        print(f'{sleepTm} seconds')
        sleepTm -= 1

#
# The heartbeat task that says we are in standby
#
async def sendMavlinkHeartBeat_standby(fm, cID, sleepTm=1):
    """send heartbeat to say we are standby (doing a slow action on the camera)"""
    fm.mavlink_send_GCS_heartbeat_sb(cID)
    while sleepTm > 0:
        time.sleep(1)
        print(f'{sleepTm} seconds')
        sleepTm -= 1
        
#
# The ACK send thread 
#
async def sendMavlinkAckData(fm, cID, sleep, cmd, rpm2, pro, res):
    """send ACK"""
    fm.mavlink_send_ack_command(cID, cmd, rpm2, pro, res)
    while sleep > 0:
        #await asyncio.sleep(1)
        print(f'{sleep} seconds')
        sleep -= 1
 
#
# The handle with ACK an error during collection that might happen during the send, its told to come again later or its wrong
#
async def execptionMavlinkErrorAckData(fm, cID):
    """send NACK"""
    while fm.task_control_1 > 0:
        #await asyncio.sleep(1)
        if (fm.ACK_ERROR == fm.GOT_ERROR):
            fm.mavlink_send_ack_command(cID, fm.errRCV_COMMAND, fm.errRPM2, 0, mavutil.mavlink.MAV_RESULT_TEMPORARILY_REJECTED)
            fm.ACK_ERROR = 0
            fm.errRCV_COMMAND = 0
            fm.errRPM2 = 0
        elif (fm.ACK_ERROR == fm.GOT_BAD):
            fm.mavlink_send_ack_command(cID, fm.errRCV_COMMAND, fm.errRPM2, 0, mavutil.mavlink.MAV_RESULT_FAILED)
            fm.ACK_ERROR = 0   

#
# The MSG send thread
#
async def processMavlinkMessageData(fm, cID, sleep, sonycam=0, caminst=0, redeyecam=0 ):
    """processes the requested action with ACK"""
    # define what is sent in param1
    myRedEyeCamera = 1
    mySonyCamera = 2
    mySonyCameraContShoot = 3 
   
    print(f"=================================== !!!!! in process !!!!!! ======================== {fm.type_of_msg}")
 
    if (fm.type_of_msg == 6500):
        #
        ## TODO :: Add the cmera retrieval class cam_data_result = fm.getCameraInfomationFromCam()
        #
        cam_data_result = fm.GOT_SUCCESS
        if (cam_data_result == fm.GOT_SUCCESS):
            fm.mavlink_send_camera_information(cID)
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
            #exit(99)
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED        
    elif (fm.type_of_msg == 6501):
        #
        ## TODO :: Add the cmera retrieval class cam_data_result = fm.getCameraSettingsFromCam()
        #
        cam_data_result = fm.GOT_SUCCESS
        if (cam_data_result == fm.GOT_SUCCESS):
            fm.mavlink_send_camera_settings(cID)
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == 6502):
        #
        ## TODO :: Add the cmera retrieval class cam_data_result = fm.getStorageInfomationFromCam()
        #
        cam_data_result = fm.GOT_SUCCESS
        if (cam_data_result == fm.GOT_SUCCESS):
            fm.mavlink_send_storage_information(cID)
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        elif (fm.cam_data_result == fm.GOT_UNFORMAT):
            fm.mavlink_send_storage_information(cID)
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED 
    elif (fm.type_of_msg == 6503):
        #
        ## TODO :: Add the cmera retrieval class cam_data_result = fm.getCameraCaptureStatusFromCam()
        #
        cam_data_result = fm.GOT_SUCCESS
        if (cam_data_result == fm.GOT_SUCCESS):
            fm.mavlink_send_camera_capture_status(cID)
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == 6504):
        #
        ## TODO :: Add the cmera retrieval class cam_data_result = fm.getCameraCaptureInformationFromCam(self.Got_Param1)
        #
        cam_data_result = fm.GOT_SUCCESS
        if (cam_data_result == fm.GOT_SUCCESS):
            fm.mavlink_send_camera_capture_information(cID)
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == 6505):
        #
        ## TODO :: Add the cmera retrieval class cam_data_result = fm.getVideoStreamInformationFromCam()
        #
        cam_data_result = fm.GOT_SUCCESS
        if (cam_data_result == fm.GOT_SUCCESS):
            fm.mavlink_send_video_stream_information(cID)
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_DO_SET_RELAY):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        relay_data_result = fm.raspberry_pi3_set_relay(fm.Got_Param1, fm.Got_Param2)
        if (relay_data_result == True):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_VIDEO_STOP_CAPTURE):
        #
        #
        ## TODO :: add the camera control
        #
        # if (self.Got_Param1 == mySonyCamera):
        #     cam_action_result = sonycam.stopMovieRec(caminst) 
        #     if not cam_action_result.find("OK") == -1:
        #         cam_action_result = fm.GOT_SUCCESS  
        #   
        cam_action_result = fm.GOT_SUCCESS         
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED  
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_VIDEO_START_CAPTURE):
        #
        #
        ## TODO :: add the camera control
        #
        # if (self.Got_Param1 == mySonyCamera):
        #     cam_action_result = sonycam.startMovieRec(caminst) 
        #     if not cam_action_result.find("OK") == -1:
        #         cam_action_result = fm.GOT_SUCCESS          
        # 
        cam_action_result = fm.GOT_SUCCESS        
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED 
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_IMAGE_START_CAPTURE):
        #
        #
        ## TODO :: add the camera control
        #
        # if (self.Got_Param1 == myRedEyeCamera):
        #     cam_action_result = redeyecam.redEyeCapture()
        #     if (cam_action_result == redeyecam.HTTP_SUCCESS_RETURN):
        #         cam_action_result = fm.GOT_SUCCESS     
        # elif (self.Got_Param1 == mySonyCamera):
        #     cam_action_result = sonycam.saveOnePicture(caminst) 
        #     if not cam_action_result.find("OK") == -1:
        #         cam_action_result = fm.GOT_SUCCESS   
        # elif (self.Got_Param1 == mySonyCameraContShoot):
        #     cam_action_result = sonycam.startContShooting(caminst) 
        #     if not cam_action_result.find("OK") == -1:
        #         cam_action_result = fm.GOT_SUCCESS         
        # 
        cam_action_result = fm.GOT_SUCCESS        
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED             
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_IMAGE_STOP_CAPTURE):
        #
        #
        ## TODO :: add the camera control
        #
        # if (self.Got_Param1 == mySonyCameraContShoot):
        #     cam_action_result = sonycam.stopContShooting(caminst)
        #     if not cam_action_result.find("OK") == -1:
        #         cam_action_result = fm.GOT_SUCCESS  
        #
        cam_action_result = fm.GOT_SUCCESS        
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED  
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_VIDEO_STOP_STREAMING):
        #
        #
        ## TODO :: add the camera control
        #
        # if (self.Got_Param1 == mySonyCam):
        #     cam_action_result = sonycam.stopLiveView(caminst) 
        #     if not cam_action_result.find("OK") == -1:
        #         cam_action_result = fm.GOT_SUCCESS 
        #
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED 
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_VIDEO_START_STREAMING):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        #
        # if (self.Got_Param1 == mySonyCam):
        #     cam_action_result = sonycam.startLiveView(caminst) 
        #     if not cam_action_result.find("OK") == -1:
        #         cam_action_result = fm.GOT_SUCCESS 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED 
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_SET_CAMERA_MODE):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED  
    elif (fm.type_of_msg == mavdefs.MAV_CMD_SET_CAMERA_ZOOM):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavdefs.MAV_CMD_SET_CAMERA_FOCUS):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONFIGURE):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_DO_CONTROL_VIDEO):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_DO_SET_CAM_TRIGG_INTERVAL):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_RESET_CAMERA_SETTINGS):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL_QUAT):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    #elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
    #   cam_action_result = fm.GOT_SUCCESS          
    #   if (cam_action_result == fm.GOT_SUCCESS):
    #       fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
    #   else:
    #       fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_DO_TRIGGER_CONTROL):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == 2004):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == 2005):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == 2010):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_STORAGE_FORMAT):
        #
        ## Sets the relay No passed from the mavlink command to the state requested
        #
        ## TODO :: add the camera control
        # 
        #  
        cam_action_result = fm.GOT_SUCCESS          
        if (cam_action_result == fm.GOT_SUCCESS):
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_REQUEST_CAMERA_INFORMATION):
        print("============================= CAMERA INFO MESSAGE ================================== ")
        fm.mavlink_send_camera_information(cID)
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_REQUEST_VIDEO_STREAM_INFORMATION):
        print("requested video stream information")
        fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_DO_SET_SERVO):
        print("setting the relay output %d %d" % (fm.Got_Param1,fm.Got_Param2))
        fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
    else:
        print(f"unknown message {fm.type_of_msg}")
        fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS

    while sleep > 0:
        #await asyncio.sleep(1)
        print(f'{sleep} seconds')
        sleep -= 1
    fm.task_control_1 = 0

# 
# =================================================================== buffer flushing routines ==================================================================
#
async def read_mav_buffer(the_connection, loop=100):
    """this functions purpose is to just read the overloaded buffer quick and flush out the records."""
    #loop = 100                                                                                  # realistic records to read under overload in the tome period (timeout means normal input rate)
    while loop >= 1:
        print("im flushing.............")
        msg = the_connection.recv_match(blocking=True, timeout=2)
        if (msg is None):                                                                       # timeout with nothing just return 
            return None
        loop -= 1
    return loop

async def flush_mavlink_buffer(the_connection, loop=100):
    """flush_mavlink_buffer: Flush the buffer -> if we timeout then we have read all the records in it, otherwise repeat the read attempts number of times."""
    print("\033[32m Buffer Flushing Active ! \033[0m")
    attempts = 3                                                                                # number of times we read before returning
    timeout_s = 1.0                                                                             # timeout on buffer 
    result = None
    while attempts >= 1:
        try:
            result = await asyncio.wait_for(read_mav_buffer(the_connection,loop), timeout=timeout_s)
        except asyncio.TimeoutError:
            print('\033[32m Buffer Flushing Completed ! \033[0m')
            return None
        if result == None:
            attempts = 1
        attempts -= 1
    print(f"\033[32m Buffer Flushing after 3 operations returned {result} records in {timeout_s} seconds ! \033[0m")
    return result

#
# @#= delete above after daemon tested
#
def sendMavlinkHeartBeat(fm, cID, sleepTm=1):
    """sends mavlink heartbeat."""
    while True:
        fm.mavlink_send_GCS_heartbeat(cID)
        time.sleep(sleepTm)
        print(f"\033[36;44m HeartBEAT !!!!! ============= {sleepTm} seconds ================= \033[0m")
        # sleepTm -= 1
        
#def sendMavlinkAckData(fm, cID, sleep, cmd, rpm2, pro, res):
#    ret = fm.mavlink_send_ack_command(cID, cmd, rpm2, pro, res)
#    while sleep > 0:
#        #await asyncio.sleep(1)
#        print(f'{sleep} seconds')
#        sleep -= 1
#    return ret

# ================ mpi writer and reader functions ==============
#
from mpi4py import MPI

# import numpy as np

def sendTagOverMPILink( tag_name ):
    """sends tag/string over mpi link ."""
    #
    # convert string to utf-8 list and make numpy array from it.
    #
    vn = []
    k = 0
    for k in range(len(tag_name)):
        vn.append(ord(tag_name[k]))
    u8_tag_name = np.array(vn, np.uint8)
    data = np.array(u8_tag_name, dtype="float64")
    comm.Send(data, dest=1, tag=0)
    print('\033[33m MPI Process {} sent string data: \033[9m'.format(rank), data)   

def sendValueListOverMPILink( tagValues ):
    """sends value over mpi link ."""
    loop = 0
    for loop in range(0,len(tagValues)):
        tagValue = tagValues[loop]
        list1 = []
        list1.append(tagValue)   
        data = np.array(list1, dtype="float64")
        comm.Send(data, dest=1, tag=0)
        print('\033[35m MPI Process {} sent data values list: \033[0m'.format(rank), data)    

def readTagOverMPILink():
    """reads tag over mpi link ."""
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
    for s in range(0, len(list1)):
        tagName = tagName + chr(int(list1[s]))
    print(f"\033[32m MPI Process {rank} received the tagname \033[31;46m {tagName} \033[0m") 
    return tagName 

def readValueListOverMPILink():
    """reads tag over mpi link ."""
    # initialize the receiving buffer to 20 elements max char size for tag
    #
    data = np.zeros(20)
    
    # receive data from master process (second its the values associated as floating point numbers) 
    #        
    comm.Recv(data, source=0, tag=0)
        
    # convert it back to a list and parse its values to the variables
    #
    list1 = []
    list1 = data.tolist()
    if (len(list1) >= 2):
        print('Process {} received data index number :'.format(rank), int(list1[1]))
        print('Process {} received data value :'.format(rank), list1[0]) 
    return list1
    
#
# ================ signal handlers ==============================
#

#
# from a signal.alarm
#
def raised_signal_handler(a, b):
    """runs this when a signal.alarm(1) issued """
    print("\033[32m ============ Take Picture ==================")
    fastGlobals.take_picture = 1
    # do the action here   

#
# CTL-C
#
def ctlc_handler(signum, frame): 
    """runs this when a ctl-c issued """
    print("Signal Number:", signum, " Frame: ", frame) 

#
# CTL-Z
#   
def exit_handler(signum, frame): 
    """runs this when a ctl-z issued """
    print('Exiting....') 
    exit(0)

#
# on getting kill -SIGUSR1 
#
def sigusr1_handler(signum, frame):
    """runs this when a -sigusr1 issued from another shell """
    print("signal hander with a kill -SIGUSR1 (signal.SIGUSR1)")
    # what we want to do on that external signal
    print("\033[32m ============ Take Picture ==================")
    fastGlobals.take_picture = 1

#
# The main thread to run this is the camera receiver client
#        
async def main():

    # ========================== SIGNAL HANDLERS =================================================
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

    # ========================== MULTI_TASKING ====================================================
    # create the sequential state variable for the scheduler working on
    # the camera operations that must be in series
    # and the choice of operation (camera feature) that will execute at each state     
    #
    mp_heart = multiprocessing.Value('i', 0)

    # initialise pool data - this is the maximum number of operations for the paralel operations group
    #
    max_number_processes = 8 

    # ========================== USE OF EXTERNAL LIBRARIES ===========================================
    # libc points to the C Library 
    #
    libc = CDLL(find_library("c"))

    # ========================= MAVLINK =============================================================    
    frame = MAVFrame()
    state = False
    while (state == False):
        try:
            cID,state = frame.makeMAVlinkConn()
        except Exception as e:
            print("Error Trap :: ", e.__class__, " occurred.")

    print("\033[31m connected to mavlink \033[0m")
    
    # wait heartbeat 
    # if it sends another sys id we need to change it
    #
    state = False
    xx = 1
    while xx == 1:
        print(f"\033[31m receive ? {xx} \033[0m")
        try:
            m = cID.recv_match(type="HEARTBEAT", blocking=True, timeout=10)
        except Exception as e:
            print("Error Trap :: ", e.__class__, " occurred.")           
        if not (m == None):
            if not ( m.autopilot == mavutil.mavlink.MAV_AUTOPILOT_INVALID ):
                xx = 2
        print(f"\033[33m receive ? {xx} \033[0m")
        
    print(f"\033[32m receive complete ? {xx} \033[0m")                
    id = m.get_srcSystem() 
    print("\033[31m heartbeat \033[0m")
    if not ( m.get_srcSystem() == frame.DEFAULT_SYS_ID ) :
        print(f"-------- new id found -------- {id}")
        while (state == False):
            try:
                cID, state = frame.makeNewMAVlinkConn(id)
            except Exception as e:
                print("Error Trap :: ", e.__class__, " occurred.")

    print("\033[31m to logger \033[0m")                
    # default logger
    #
    # multiprocessing.log_to_stderr(logging.DEBUG)
    #
    # for extra logging use this 
    # instead
    #
    multiprocessing.log_to_stderr()
    #logger = multiprocessing.get_logger()
    #logger.setLevel(logging.INFO)
    
    #
    # create instance of sony alpha cam (new API)
    #        
    mySonyCamNo1 = sonyAlphaNewCamera()
    
    #
    # create an instance of common write structure  
    # from mavlink reader task to the camera
    #
    gcsWrites2Sony = mavlinkSonyCamWriteVals()

    print("\033[31m getting data \033[0m")
    #
    # init the objects with camera data 
    # & set rhw data to be written back to gcs via mavlink
    #
    #
    # Initialise all shared object data between
    # sony camera and mavlink processes
    #        
    expro = mySonyCamNo1.initSonyCamExProData(  )
    aper = mySonyCamNo1.initSonyApertureData(  ) 
    focusdata = mySonyCamNo1.initSonyCamFocusData(  )       
    focusarea = mySonyCamNo1.initSonyCamFocusAreaData(  )  
    iso = mySonyCamNo1.initSonyCamISOData(  )      
    shut_sp = mySonyCamNo1.initSonyCamShutSpdData(  )   
    whitebal = mySonyCamNo1.initSonyCamWhiteBalaData(  )   
    stillcap = mySonyCamNo1.initSonyCamStillCapModeData(  )
    # GUI variable to choose the camera set-up
    cam_choice = mySonyCamNo1.initCamChoiceData( )
    
    print("\033[31m got sony data \033[0m")
    
    # this is a rough trap for now but if its all zeros its not getting correct data from the camera then try reset the link first
    # no need to aquire as this is working in single task mode at this point
    if ((((((((expro.signal.value == 0) and (aper.signal.value == 0)) and (focusdata.signal.value == 0)) and (focusarea.signal.value == 0)) and (iso.signal.value == 0)) and (shut_sp.signal.value == 0)) and (whitebal.signal.value == 0)) and (stillcap.signal.value == 0)):
        reset_usb_camlink()
        retCode = mySonyCamNo1.getSonyCamExProData( expro )
        retCode = mySonyCamNo1.getSonyApertureData( aper ) 
        retCode = mySonyCamNo1.getSonyCamFocusData( focusdata )       
        retCode = mySonyCamNo1.getSonyCamFocusAreaData( focusarea )  
        retCode = mySonyCamNo1.getSonyCamISOData( iso )      
        retCode = mySonyCamNo1.getSonyCamShutSpdData( shut_sp )   
        retCode = mySonyCamNo1.getSonyCamWhiteBalaData( whitebal )   
        retCode = mySonyCamNo1.getSonyCamStillCapModeData( stillcap )
        
    # uncomment these if you dont want an immediate update message
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
    doMavIsoTask = asyncio.create_task(sendMavIso(mySonyCamNo1, iso, cID ))
    doMavAperTask = asyncio.create_task(sendMavAper( mySonyCamNo1, aper, cID ))
    doMavFocusTask = asyncio.create_task(sendMavFocusData( mySonyCamNo1, focusdata, focusarea, cID ))
    doMavExproTask = asyncio.create_task(sendMavExpro( mySonyCamNo1, expro, cID ))
    doMavShutSpdTask = asyncio.create_task(sendMavShutSpd( mySonyCamNo1, shut_sp, cID ))
    doMavWhiteBalTask = asyncio.create_task(sendMavWhiteBala( mySonyCamNo1, whitebal, cID ))
    doMavStillCapTask = asyncio.create_task(sendMavStillCap( mySonyCamNo1, stillcap, cID )) 

    doMavCamChoiceTask = asyncio.create_task(sendMavCamChoice( mySonyCamNo1, cam_choice, cID ))
    
    await doMavIsoTask
    await doMavAperTask
    await doMavFocusTask
    await doMavExproTask
    await doMavShutSpdTask
    await doMavWhiteBalTask
    await doMavStillCapTask

    await doMavCamChoiceTask
    
    # ========= micaSense RedEdge Exposure object ===========
    #
    # initialisation of linked list to store variables
    # and read data via HTTP API
    #
    red_edge_exposure = LinkedListMemory()
    redEdgeCamNo1 = micaSenseCamera()
    expos_json = redEdgeCamNo1.micaSenseGetExposure()
    red_edge_exposure.addNode("RED_EXP_1", expos_json['exposure1'])
    red_edge_exposure.addNode("RED_EXP_2", expos_json['exposure2'])
    red_edge_exposure.addNode("RED_EXP_3", expos_json['exposure3'])
    red_edge_exposure.addNode("RED_EXP_4", expos_json['exposure4'])
    red_edge_exposure.addNode("RED_EXP_5", expos_json['exposure5'])
    red_edge_exposure.addNode("RED_GAIN_1", expos_json['gain1'])
    red_edge_exposure.addNode("RED_GAIN_2", expos_json['gain2'])
    red_edge_exposure.addNode("RED_GAIN_3", expos_json['gain3'])
    red_edge_exposure.addNode("RED_GAIN_4", expos_json['gain4'])
    red_edge_exposure.addNode("RED_GAIN_5", expos_json['gain5'])
    for z in range(0, LinkedListMemory.numberOfVals):
        red_edge_exposure.set_update_flag(z, True)
        
    #
    # now set the class to be initialised
    #
    gcsWrites2Sony.init_class_state()
        
    #
    # test iso write (single task mode) 
    #
    # ### If you want this in single task mode ###
    #
    active = True
    #
    # ### If you want this in multi mode ###
    #
    # active = False

    # initialise the scheduler the list is rotational each time we re-schedule (uncomment if requried)
    # 
    #schedule = list(range(1,8))

    #
    # ### latch for serial connection has been made ###
    #
    lockout = False
    
    while active==True:
        recieveTask = asyncio.create_task(run_process_messages_from_connection_single(frame, cID, gcsWrites2Sony, 5, redEdgeCamNo1))
        if (mp_heart.value == 0):
            heartTask = asyncio.create_task(sendMavlinkHeartBeat_single(frame, cID, 0))
        paramReqTask = asyncio.create_task(serviceParamRequests( mySonyCamNo1, gcsWrites2Sony, stillcap, whitebal, shut_sp, iso, focusdata, focusarea, aper, expro, redEdgeCamNo1, red_edge_exposure, camera_choice ))

        # to connect with the micasense camera on serial link if we have just changed to use the micasense camera
        # TO CHECK not sure if this is best or if i should just shell a one off conection occasioanly for this
        #
        if ((not (cam_choice.signal.value == cam_choice.prev.value)) and (cam_choice.signal.value >= 2)) and (lockout == False):
            attempts = 3
            while ((attempts > 0) and (lockout == False)):
                try:
                    serial_mica_handle, state = frame.makeMAVlinkSerialConn()
                    with cam_choice.prev.get_lock():
                        cam_choice.prev.value = cam_choice.signal.value
                    lockout = state
                except Exception as e:
                    print("Error Trap :: ", e.__class__, " occurred.")
                attempts -= 1
                
        # this task is in the main loop and is managing taking a sony picture with acknowledgement
        #
        print(f"taking a picture on the sony alpha7 camera ..... {fastGlobals.take_picture}")
        
        if (gcsWrites2Sony.take_photo.value == 1) and (fastGlobals.take_picture == get_cam_enum("idle")):
            fastGlobals.take_picture = get_cam_enum("taking_photo")
            with gcsWrites2Sony.take_photo.get_lock():
                gcsWrites2Sony.take_photo.value = 2

        if (gcsWrites2Sony.take_photo.value == 2):            
            if (fastGlobals.take_picture == get_cam_enum("taking_photo")): 
                frame.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
                try = 3
                while try > 0:
                    if (sendMavlinkAckData(frame, cID, 0, frame.RCV_COMMAND, frame.RPM2, 0, frame.ACK_RESULT) == True):
                        try = -2
                    else:
                        try -= 1        
                fastGlobals.take_picture = mavlinkTakePhoto( mySonyCamNo1, fastGlobals.take_picture )
            
            if (fastGlobals.take_picture == get_cam_enum("photo_ack")):
                frame.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
                try = 3
                while try > 0:
                    if (sendMavlinkAckData(frame, cID, 0, frame.RCV_COMMAND, frame.RPM2, 100, frame.ACK_RESULT) == True):
                        try = -2
                    else:
                        try -= 1
                fastGlobals.take_picture = get_cam_enum("photo_complete")                  
            else:
                frame.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
                try = 3            
                while try > 0:
                    if (sendMavlinkAckData(frame, cID, 0, frame.RCV_COMMAND, frame.RPM2, 0, frame.ACK_RESULT) == True):
                        try = -2
                    else:
                        try -= 1
                fastGlobals.take_picture = get_cam_enum("idle")
            
            if (fastGlobals.take_picture == get_cam_enum("photo_complete")):
                frame.ACK_RESULT = mavutil.mavlink.MAV_RESULT_ACCEPTED
                try = 3                  
                while try > 0:
                    if (sendMavlinkAckData(frame, cID, 0, frame.RCV_COMMAND, frame.RPM2, 100, frame.ACK_RESULT) == True):
                        try = -2
                    else:
                        try -= 1
                fastGlobals.take_picture = get_cam_enum("idle")    
                
            if (fastGlobals.take_picture == get_cam_enum("idle"))
                frame.RCV_COMMAND = 0
                with gcsWrites2Sony.take_photo.get_lock():
                    gcsWrites2Sony.take_photo.value == 0
                with gcsWrites2Sony.cmd_wants_ack.get_lock():
                    gcsWrites2Sony.cmd_wants_ack.value = False
                
        if (gcsWrites2Sony.mp_state.value == mavlinkSonyCamWriteVals.FUNC_IDLE):
            # change schedule first = last (not deemed neccessary here... uncomment if required)
            #                
            # schedule.append(schedule[0])
            # schedule.pop(0)
            if not (gcsWrites2Sony.set_sony_iso.value == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_sony_iso.value == gcsWrites2Sony.prev_sony_iso.value):
                print(f"on TOP LEVEL saw {gcsWrites2Sony.set_sony_iso.value} {gcsWrites2Sony.prev_sony_iso.value} {gcsWrites2Sony.mav_req_all_param.value}")
                # send a heartbeat that says we are going into standby until we complete the camera action
                heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0))      
                fastGlobals.take_picture = get_cam_enum("configuring_photo")                
                doIsoTask = asyncio.create_task(doAlphaCameraIso(mySonyCamNo1, gcsWrites2Sony, iso))
                await doIsoTask 
                fastGlobals.take_picture = get_cam_enum("idle") 
            if not (gcsWrites2Sony.set_sony_aperture.value == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_sony_aperture.value == gcsWrites2Sony.prev_sony_aperture.value):
                print(f"on TOP LEVEL saw aperture {gcsWrites2Sony.set_sony_aperture.value} {gcsWrites2Sony.prev_sony_aperture.value} {gcsWrites2Sony.mav_req_all_param.value}")
                # send a heartbeat that says we are going into standby until we complete the camera action
                heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
                fastGlobals.take_picture = get_cam_enum("configuring_photo")  
                doAperTask = asyncio.create_task(doAlphaCameraAperture(mySonyCamNo1, gcsWrites2Sony, aper))
                await doAperTask
                fastGlobals.take_picture = get_cam_enum("idle")
            if not (gcsWrites2Sony.set_sony_white_bal.value == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_sony_white_bal.value == gcsWrites2Sony.prev_sony_white_bal.value):
                print(f"on TOP LEVEL saw wb {gcsWrites2Sony.set_sony_white_bal.value} {gcsWrites2Sony.prev_sony_white_bal.value} {gcsWrites2Sony.mav_req_all_param.value}")
                # send a heartbeat that says we are going into standby until we complete the camera action
                heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
                fastGlobals.take_picture = get_cam_enum("configuring_photo")  
                doWhiBalTask = asyncio.create_task(doAlphaWhiteBala(mySonyCamNo1, gcsWrites2Sony, whitebal))
                await doWhiBalTask
                fastGlobals.take_picture = get_cam_enum("idle") 
            if not (gcsWrites2Sony.set_sony_ex_pro.value == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_sony_ex_pro.value == gcsWrites2Sony.prev_sony_ex_pro.value):
                print(f"on TOP LEVEL saw expro {gcsWrites2Sony.set_sony_ex_pro.value} {gcsWrites2Sony.prev_sony_ex_pro.value} {gcsWrites2Sony.mav_req_all_param.value}")
                # send a heartbeat that says we are going into standby until we complete the camera action
                heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
                fastGlobals.take_picture = get_cam_enum("configuring_photo")  
                doExProTask = asyncio.create_task(doAlphaCameraExpro(mySonyCamNo1, gcsWrites2Sony, expro))
                await doExProTask 
                fastGlobals.take_picture = get_cam_enum("idle")
            if not (gcsWrites2Sony.set_sony_still_cap_mode.value == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_sony_still_cap.value == gcsWrites2Sony.prev_sony_still_cap_mode.value):
                print(f"on TOP LEVEL saw still cap {gcsWrites2Sony.set_sony_still_cap_mode.value} {gcsWrites2Sony.prev_sony_still_cap_mode.value} {gcsWrites2Sony.mav_req_all_param.value}")
                # send a heartbeat that says we are going into standby until we complete the camera action
                heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
                fastGlobals.take_picture = get_cam_enum("configuring_photo") 
                doStillCapTask = asyncio.create_task(doAlphaCameraStillCap(mySonyCamNo1, gcsWrites2Sony, stillcap))  
                await doStillCapTask
                fastGlobals.take_picture = get_cam_enum("idle")
            if not (gcsWrites2Sony.set_sony_shutter.value == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_sony_shutter.value == gcsWrites2Sony.prev_sony_shutter.value):
                print(f"on TOP LEVEL saw shutter speed {gcsWrites2Sony.set_sony_shutter.value} {gcsWrites2Sony.prev_sony_shutter.value} {gcsWrites2Sony.mav_req_all_param.value}")
                # send a heartbeat that says we are going into standby until we complete the camera action
                heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
                fastGlobals.take_picture = get_cam_enum("configuring_photo")
                doShutSpdTask = asyncio.create_task(doAlphaCameraShutSpd(mySonyCamNo1, gcsWrites2Sony, shut_sp))  
                await doShutSpdTask
                fastGlobals.take_picture = get_cam_enum("idle")
            if not (gcsWrites2Sony.set_sony_focus.value == gcsWrites2Sony.STATE_INIT) or not (gcsWrites2Sony.set_sony_focus_area.value == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_sony_focus.value == gcsWrites2Sony.prev_sony_focus.value) and not (gcsWrites2Sony.set_sony_focus_area.value == gcsWrites2Sony.prev_sony_focus_area.value):
                print(f"on TOP LEVEL saw focus change {gcsWrites2Sony.set_sony_focus.value} {gcsWrites2Sony.prev_sony_focus.value} {gcsWrites2Sony.set_sony_focus_area.value} {gcsWrites2Sony.prev_sony_focus_area.value} {gcsWrites2Sony.mav_req_all_param.value}")
                # send a heartbeat that says we are going into standby until we complete the camera action
                heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
                fastGlobals.take_picture = get_cam_enum("configuring_photo")
                doFocusTask = asyncio.create_task(doAlphaCameraFocusData(mySonyCamNo1, gcsWrites2Sony, focusdata, focusarea))             
                await doFocusTask
                fastGlobals.take_picture = get_cam_enum("idle")
                
        if not (gcsWrites2Sony.set_cam_choice.value == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_cam_choice.value == gcsWrites2Sony.prev_cam_choice.value):
            print(f"on TOP LEVEL saw camera_choice change {gcsWrites2Sony.set_cam_choice.value} {gcsWrites2Sony.prev_cam_choice.value}")
            # check if the choice is valid and if so set the object for update otherwise remove the request
            validcams = [ 0, 1, 2, 3 ]                                               # list contains valid enumerations for the cameras
            found = False
            for num in range(0, len(validcams)):
                if (validcams[num] == gcsWrites2Sony.set_cam_choice.value):               
                    if (cam_choice.set_value(gcsWrites2Sony.set_cam_choice.value, memoryValue.STATE_MAV_WRITING, 20) == True)
                        with gcsWrites2Sony.prev_cam_choice.get_lock():
                            gcsWrites2Sony.prev_cam_choice.value = gcsWrites2Sony.set_cam_choice.value
                            found = True
            if (found == False):
                with gcsWrites2Sony.set_cam_choice.get_lock():
                    gcsWrites2Sony.set_cam_choice.value = gcsWrites2Sony.prev_cam_choice.value  
                        
        if not (gcsWrites2Sony.set_mica_exposure.exp1 == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_mica_exposure.exp1 == gcsWrites2Sony.prev_mica_exposure.exp1):
            print(f"on TOP LEVEL micaSense exposure change {gcsWrites2Sony.set_mica_exposure.exp1} {gcsWrites2Sony.prev_mica_exposure.exp1} ")
            # send a heartbeat that says we are going into standby until we complete the camera action
            heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
            doReExpos = asyncio.create_task(doRedExposure(redEdgeCamNo1, gcsWrites2Sony, red_edge_exposure))              
            await doReExpos
        elif not (gcsWrites2Sony.set_mica_exposure.exp2 == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_mica_exposure.exp2 == gcsWrites2Sony.prev_mica_exposure.exp2):
            print(f"on TOP LEVEL micaSense exposure change {gcsWrites2Sony.set_mica_exposure.exp2} {gcsWrites2Sony.prev_mica_exposure.exp2} ")
            # send a heartbeat that says we are going into standby until we complete the camera action
            heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
            doReExpos = asyncio.create_task(doRedExposure(redEdgeCamNo1, gcsWrites2Sony, red_edge_exposure))             
            await doReExpos
        elif not (gcsWrites2Sony.set_mica_exposure.exp3 == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_mica_exposure.exp3 == gcsWrites2Sony.prev_mica_exposure.exp3):
            print(f"on TOP LEVEL micaSense exposure change {gcsWrites2Sony.set_mica_exposure.exp3} {gcsWrites2Sony.prev_mica_exposure.exp3} ")
            # send a heartbeat that says we are going into standby until we complete the camera action
            heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
            doReExpos = asyncio.create_task(doRedExposure(redEdgeCamNo1, gcsWrites2Sony, red_edge_exposure))             
            await doReExpos
        elif not (gcsWrites2Sony.set_mica_exposure.exp4 == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_mica_exposure.exp4 == gcsWrites2Sony.prev_mica_exposure.exp4):
            print(f"on TOP LEVEL micaSense exposure change {gcsWrites2Sony.set_mica_exposure.exp4} {gcsWrites2Sony.prev_mica_exposure.exp4} ")
            # send a heartbeat that says we are going into standby until we complete the camera action
            heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
            doReExpos = asyncio.create_task(doRedExposure(redEdgeCamNo1, gcsWrites2Sony, red_edge_exposure))             
            await doReExpos
        elif not (gcsWrites2Sony.set_mica_exposure.exp5 == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_mica_exposure.exp5 == gcsWrites2Sony.prev_mica_exposure.exp5):
            print(f"on TOP LEVEL micaSense exposure change {gcsWrites2Sony.set_mica_exposure.exp5} {gcsWrites2Sony.prev_mica_exposure.exp5} ")
            # send a heartbeat that says we are going into standby until we complete the camera action
            heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
            doReExpos = asyncio.create_task(doRedExposure(redEdgeCamNo1, gcsWrites2Sony, red_edge_exposure))             
            await doReExpos
        elif not (gcsWrites2Sony.set_mica_exposure.gain1 == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_mica_exposure.gain1 == gcsWrites2Sony.prev_mica_exposure.gain1):
            print(f"on TOP LEVEL micaSense exposure change {gcsWrites2Sony.set_mica_exposure.gain1} {gcsWrites2Sony.prev_mica_exposure.gain1} ")
            # send a heartbeat that says we are going into standby until we complete the camera action
            heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
            doReExpos = asyncio.create_task(doRedExposure(redEdgeCamNo1, gcsWrites2Sony, red_edge_exposure))             
            await doReExpos
        elif not (gcsWrites2Sony.set_mica_exposure.gain2 == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_mica_exposure.gain2 == gcsWrites2Sony.prev_mica_exposure.gain2):
            print(f"on TOP LEVEL micaSense exposure change {gcsWrites2Sony.set_mica_exposure.gain2} {gcsWrites2Sony.prev_mica_exposure.gain2} ")
            # send a heartbeat that says we are going into standby until we complete the camera action
            heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
            doReExpos = asyncio.create_task(doRedExposure(redEdgeCamNo1, gcsWrites2Sony, red_edge_exposure))             
            await doReExpos
        elif not (gcsWrites2Sony.set_mica_exposure.gain3 == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_mica_exposure.gain3 == gcsWrites2Sony.prev_mica_exposure.gain3):
            print(f"on TOP LEVEL micaSense exposure change {gcsWrites2Sony.set_mica_exposure.gain3} {gcsWrites2Sony.prev_mica_exposure.gain3} ")
            # send a heartbeat that says we are going into standby until we complete the camera action
            heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
            doReExpos = asyncio.create_task(doRedExposure(redEdgeCamNo1, gcsWrites2Sony, red_edge_exposure))             
            await doReExpos
        elif not (gcsWrites2Sony.set_mica_exposure.gain4 == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_mica_exposure.gain4 == gcsWrites2Sony.prev_mica_exposure.gain4):
            print(f"on TOP LEVEL micaSense exposure change {gcsWrites2Sony.set_mica_exposure.gain1} {gcsWrites2Sony.prev_mica_exposure.gain4} ")
            # send a heartbeat that says we are going into standby until we complete the camera action
            heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
            doReExpos = asyncio.create_task(doRedExposure(redEdgeCamNo1, gcsWrites2Sony, red_edge_exposure))             
            await doReExpos
        elif not (gcsWrites2Sony.set_mica_exposure.gain5 == gcsWrites2Sony.STATE_INIT) and not (gcsWrites2Sony.set_mica_exposure.gain5 == gcsWrites2Sony.prev_mica_exposure.gain5):
            print(f"on TOP LEVEL micaSense exposure change {gcsWrites2Sony.set_mica_exposure.gain5} {gcsWrites2Sony.prev_mica_exposure.gain5} ")
            # send a heartbeat that says we are going into standby until we complete the camera action
            heartTask = asyncio.create_task(sendMavlinkHeartBeat_standby(frame, cID, 0)) 
            doReExpos = asyncio.create_task(doRedExposure(redEdgeCamNo1, gcsWrites2Sony, red_edge_exposure))             
            await doReExpos
                
        if (gcsWrites2Sony.clear_buffer.value == True):
            # in simple terms without a return value
            #
            # flushBufferTask = asyncio.create_task(flush_mavlink_buffer(cID)) 
            # await flushBufferTask
            # https://www.integralist.co.uk/posts/python-asyncio/ python 3.8 running asyncio with a returned result
            # https://note.crohaco.net/2019/python-asyncio/
            #
            if (sys.version_info.major == 3 and sys.version_info.minor >= 7):
                tasks = [flush_mavlink_buffer(cID)]
                for future in asyncio.as_completed(tasks):
                    res = await future
                    print(f"completed the buffer flush with {res} records remaining")  
                    if (res == None):                   
                        with gcsWrites2Sony.clear_buffer.get_lock(): 
                            gcsWrites2Sony.clear_buffer.value == False                    
            elif (sys.version_info.major == 3 and sys.version_info.minor <= 6) and (sys.version_info.major == 3 and sys.version_info.minor >= 5):
                loop = asyncio.get_event_loop()
                loop.run_until_complete(flush_mavlink_buffer(cID))
                future = loop.create_future()
                loop.run_until_complete(future)
                res = future
                print(f"completed the buffer flush with {res} records remaining")  
                if (res == None):                   
                    with gcsWrites2Sony.clear_buffer.get_lock(): 
                        gcsWrites2Sony.clear_buffer.value == False
            else:
                print("\033[31m --------------- buffer flush not supported in python {sys.version_info.major}.{sys.version_info.minor} \033[0m")
                
        if not (gcsWrites2Sony.cmd_wants_ack.value == True) and (gcsWrites2Sony.take_photo.value == 0):                                   # we have something to process and completed any photo taking
            snd_task_2 = asyncio.create_task(sendMavlinkAckData(frame, cID, 1, frame.RCV_COMMAND, frame.RPM2, 0, frame.ACK_RESULT ))      
            await snd_task_2
 
            print("ack end....................................................................")
            frame.task_control_1 = 1 
            #snd_task_3 = asyncio.create_task(processMavlinkMessageData(frame, cID, 1, pysonyCam, camInst, redEyeCam))
            snd_task_3 = asyncio.create_task(processMavlinkMessageData(frame, cID, 0))
            exc_task_error_handler = asyncio.create_task(execptionMavlinkErrorAckData(frame, cID))           
            await snd_task_3 
            await exc_task_error_handler
            print(f"end 2 tasks...............................{frame.RCV_COMMAND} {frame.RPM2} {frame.ACK_RESULT}") 
            snd_task_2 = asyncio.create_task(sendMavlinkAckData(frame, cID, 1, frame.RCV_COMMAND, frame.RPM2, 100, frame.ACK_RESULT )) 
            await snd_task_2
            # re-enable when you want to check this again exit(55)
            print("ack end2...................................................................")
            frame.ACK_RESULT = mavutil.mavlink.MAV_RESULT_ACCEPTED
            print(f"sending final completed ack...............................{frame.RCV_COMMAND} {frame.RPM2} {frame.ACK_RESULT}") 
            snd_task_2_1 = asyncio.create_task(sendMavlinkAckData(frame, cID, 1, frame.RCV_COMMAND, frame.RPM2, 100, frame.ACK_RESULT )) 
            await snd_task_2_1
            frame.RCV_COMMAND = 0  
            with gcsWrites2Sony.cmd_wants_ack.get_lock():
                gcsWrites2Sony.cmd_wants_ack.value = False 
            
        doMavIsoTask = asyncio.create_task(sendMavIso(mySonyCamNo1, iso, cID ))
        doMavAperTask = asyncio.create_task(sendMavAper( mySonyCamNo1, aper, cID ))
        doMavFocusTask = asyncio.create_task(sendMavFocusData( mySonyCamNo1, focusdata, focusarea, cID ))
        doMavExproTask = asyncio.create_task(sendMavExpro( mySonyCamNo1, expro, cID ))
        doMavShutSpdTask = asyncio.create_task(sendMavShutSpd( mySonyCamNo1, shut_sp, cID ))
        doMavWhiteBalTask = asyncio.create_task(sendMavWhiteBala( mySonyCamNo1, whitebal, cID ))
        doMavStillCapTask = asyncio.create_task(sendMavStillCap( mySonyCamNo1, stillcap, cID )) 
        doMavCamSelectTask = asyncio.create_task(sendMavCamChoice( mySonyCamNo1, camera_choice, cID )) 
        

        # send the RedEdge information
        doMavRedExpos = asyncio.create_task(sendMavRedExpos( frame, red_edge_exposure, cID ))
        
        await doMavIsoTask
        await doMavAperTask
        await doMavFocusTask
        await doMavExproTask
        await doMavShutSpdTask
        await doMavWhiteBalTask
        await doMavStillCapTask   
        await doMavCamSelectTask
        
        #if (mySonyCamNo1.error_counts.value >= 5):  
        #    reset_usb_camlink()
        #    with mySonyCamNo1.error_counts.get_lock():
        #        mySonyCamNo1.error_counts.value = 0            
        await doMavRedExpos 
        
        print("completed..................................................")    
        recieveTask.cancel()
        
        print(f"Ended: {time.strftime('%X')}")
        with mp_heart.get_lock():
            mp_heart.value += 1 
            mp_heart.value = mp_heart.value % 12
 
        await paramReqTask
    
    #
    # Release the shared memory dealing with sony camera
    #	
    del expro
    del stillcap     
    del aper
    del focusdata
    del focusarea
    del shut_sp
    del whitebal

    del camera_choice
    
    #
    # Release the shared memory dealing with micasense RedEdge camera
    #	
    del red_edge_exposure
    
if __name__ == '__main__':

    if (sys.version_info.major == 3 and sys.version_info.minor >= 7):
        asyncio.run(main())
    elif (sys.version_info.major == 3 and sys.version_info.minor <= 6) and (sys.version_info.major == 3 and sys.version_info.minor >= 5):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(main()))
    else:
        print("you currently need to have python 3.5 at least")