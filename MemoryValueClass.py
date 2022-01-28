# ===============================================================================================================================
#
# Name : MemoryValueClass.py
# Desc : Global memory value class for use with cameras and mavlink
# Auth : AIR-obots Ai-Robots
#
# ===============================================================================================================================
import time

class memoryValue():

    STATE_READY = 1
    STATE_CAM_WRITING = 2
    STATE_MAV_READING = 3
    STATE_MAV_WRITING = 4
    STATE_CAM_READING = 5
    numberOfVals = 0

    def __init__ (self, name = 'value_name_not_set', signal = None,  prev = None,  state = STATE_READY):
        self.signal = signal                                                               # signal value
        self.prev = prev                                                                   # previous signal value
        self.state = state                                                                 # state of the value
        self.nextpointer = None                                                            # pointer for chain if needed
        self.name = name                                                                   # name as a string
        self.timestamp = None                                                              # timestamp
        memoryValue.numberOfVals += 1                                                      # global counter of the number of values
    
    def __del__(self):  
        class_name = self.__class__.__name__  
        print('{} Deleted'.format(class_name))

    def get_value_counter(self):  
        print('%s: %d' % (self.name,memoryValue.numberOfVals))
        return memoryValue.numberOfVals		
  
    def get_value_data(self,YourID,timeout):  
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

    def set_value(self,value,myId,timeout):
        timeCnt = 0
        while (not (self.state == memoryValue.STATE_READY)) and (timeCnt < timeout):
            time.sleep(0.1)
            timeCnt += 1

        if (timeCnt < timeout):
            self.state = myId
            self.prev = self.signal
            self.signal = value
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


if __name__ == '__main__':

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
    
    
                            self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
