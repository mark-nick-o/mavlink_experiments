#
# Air Cam Pro 2021
# This is tests for python mavlink for camera control 
# It uses snippets and code from the sources given below
# REV 1.1 23-12-2021 1700
#
# Mark Jacobsen
# mark@syriaairlift.org
#
# example mavlink GUI
# https://github.com/markdjacobsen/hellomav
#
# Joystick readers and mavlink over UDP
# https://github.com/Smolyarov/u2/blob/master/tools/joystick/joy2mavlink.py
# https://gist.github.com/wwj718/8ebd3dcae6d04f869cf256069ba0dd42 
# https://habr.com/ru/post/130788/
#
# This is a simple demonstration of how to begin building a ground control station (GCS)
# in Python using a GUI. It allows a user to select a serial port and baud rate, connect
# to a MAVLINK device, then send a command to arm the motor. Note that this does not
# include any exception handling.
#
# The GUI is built using wxPython. MAVLINK communication is done through the pymavlink
# library.

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

# ref to multi-threading using asyncio
#
# https://python-scripts.com/sleep#threading-event
# vasile.buldumac@ati.utm.md
# 

# sudo apt-get install python3-dev python3-opencv python3-wxgtk4.0 python3-pip python3-matplotlib python3-lxml
# sudo apt-get install libxml++2.6-dev
# sudo pip install dronekit

# for the full pymavlink install guide please refer to this https://www.ardusub.com/developers/pymavlink.html
#
# e.g on Rasp pi
# Update list of available packages
# sudo apt update
# sudo apt -y upgrade
#
# Install some dependencies
# sudo apt install -y python3-pip
#
# Install mavproxy module and everything else needed
# pip3 install mavproxy
#
# pip install pymavlink
#
# to list pip list | grep link or pip3 list | grep link

# ================== Compatible Joysticks =========================================
# X-Box 360 Controller (name: "Xbox 360 Controller")
# Playstation 4 Controller (name: "PS4 Controller")
# X-Box 360 Controller (name: "Controller (XBOX 360 For Windows)")
#  
from pymavlink import mavutil   # ref:- https://www.ardusub.com/developers/pymavlink.html
import wx
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

from mypymavlink import mavutilcust as custommav

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
import RPi.GPIO as GPIO
 
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

    # defines for camera ID file
    #
    CAM_XML_FILE =  "alpha_cam_new.xml"
    NETWORK_ID = 1

    def __init__(self, pinNum=26):
        self.setUPPiRelayNumBCM()
        self.setPinINput(pinNum)

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

    def serial_ports(self):
    #"""Lists all available serial ports
    #:raises EnvironmentError:
    #    On unsupported or unknown platforms
    #:returns:
    #    A list of available serial ports
    #"""
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
            pygame.event.set_blocked(MOUSEBUTTONDOWN)
        else:
            pygame.event.set_allowed(MOUSEBUTTONDOWN)

    def blockMouseUp(self,block_flag):
        if block_flag:
            pygame.event.set_blocked(MOUSEBUTTONUP)
        else:
            pygame.event.set_allowed(MOUSEBUTTONUP)

    def checkMouseDwnBlock(self):
        print ('MOUSEBUTTONDOWN is block: ', pygame.event.get_blocked(MOUSEBUTTONDOWN))

    def checkMouseUpBlock(self):
        print ('MOUSEBUTTONUP is block: ', pygame.event.get_blocked(MOUSEBUTTONUP))

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
                    print_2_yellow("Mouse button down pressed.",event.button,event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    print_2_yellow("Mouse button up pressed.",event.button,event.pos)
                elif event.type == pygame.JOYBUTTONDOWN:
                    print_2_yellow("Joystick button down pressed.",event.button,event.joy)
                elif event.type == pygame.JOYBUTTONUP:
                    print_2_yellow("Joystick button up released.",event.button,event.joy)
                elif event.type == pygame.JOYAXISMOTION:
                    print_3_yellow("Joystick axis motion.",event.joy,event.axis,event.value)
                elif event.type == pygame.JOYBALLMOTION:
                    print_3_yellow("Joystick ball motion.",event.joy,event.ball,event.rel)
                elif event.type == pygame.JOYHATMOTION:
                    print_3_yellow("Joystick hat motion",event.joy,event.hat,event.value)
                elif event.type == pygame.VIDEORESIZE:
                    print_3_blue("video re-size.",event.size,event.w,event.h)
                elif event.type == pygame.KEYDOWN:
                    print_3_yellow("key down ",event.unicode,event.key,event.mod)
                elif event.type == pygame.KEYUP:
                    print_2_yellow("key up ",event.key,event.mod)

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
                print_yellow("Thrust value ",thrust)

                # this is the x axis
                rudder = joystick.get_axis(0)
                print_blue("Rudder value ",rudder)

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
    def makeMAVlinkConn(self):
        try:
            the_conection = custommav.mavlink_connection('udpin:0.0.0.0:14550',autoreconnect=True)
            #the_conection = mavutil.mavlink_connection('udpin:0.0.0.0:14550',autoreconnect=True)
            return the_conection,True
        except Exception as err_msg:
            print("Failed to connect : %s" % (err_msg))
            return the_conection,False

    def makeNewMAVlinkConn(self,id):
        try:
            the_conection = custommav.mavlink_connection('udpin:0.0.0.0:14550',autoreconnect=True, source_system=id)
            #the_conection = mavutil.mavlink_connection('udpin:0.0.0.0:14550',autoreconnect=True, source_system=id)
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
                CamMode, # param2
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
                CamZoomType, # param1
                CamZoomValue, # param2
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
       
    def mavlink_send_param_value(self, the_connection):
       
        print("\033[36m sending a parameter") 
        try:
            the_connection.mav.param_value_send(
            "CrISOMode".encode('ascii'),
            0,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            1,
            1)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message : %s" % (err_msg))
            ret = False
        try:
            the_connection.mav.param_value_send(
            "CrShutterSpeedSet".encode('ascii'),
            10,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            1,
            1)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message : %s" % (err_msg))
            ret = False
        try:
            the_connection.mav.param_value_send(
            "CrAperture".encode('ascii'),
            30,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            1,
            1)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message : %s" % (err_msg))
            ret = False
        try:
            the_connection.mav.param_value_send(
            "CrFocusMode".encode('ascii'),
            3,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            1,
            1)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message : %s" % (err_msg))
            ret = False
        try:
            the_connection.mav.param_value_send(
            "CrFocusArea".encode('ascii'),
            4,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            1,
            1)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message : %s" % (err_msg))
            ret = False
        try:
            the_connection.mav.param_value_send(
            "CrExposureProgram".encode('ascii'),
            5,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            1,
            1)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message : %s" % (err_msg))
            ret = False
        try:
            the_connection.mav.param_value_send(
            "CrStillCapture".encode('ascii'),
            6,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            1,
            1)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message : %s" % (err_msg))
            ret = False
        try:
            the_connection.mav.param_value_send(
            "CrWhiteBalanceSetting".encode('ascii'),
            7,
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32,
            1,
            1)
            ret = True
        except Exception as err_msg:
            print("Failed to send param value message : %s" % (err_msg))
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
        
    # process the incoming messages received
    #
    def process_messages_from_connection(self, fra, the_connection, redCam=0):
        #"""
        #This runs continuously. The mavutil.recv_match() function will call mavutil.post_message()
        #any time a new message is received, and will notify all functions in the master.message_hooks list.
        #"""
        loop = 5
        while loop >= 1:
            print("im receiving.............")

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
            #the_connection.mav.vibration_send( 1000, 1, 1, 22, 21, 10, 30 )
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
                return
            if msg.get_type() == "BAD_DATA":
                self.ACK_ERROR = self.GOT_BAD
                self.errRCV_COMMAND = 0
                self.errRPM2 = 0
                if mavutil.all_printable(msg.data):
                    sys.stdout.write(msg.data)
                    sys.stdout.flush()
            elif msg.get_type() == 'PARAM_REQUEST_LIST':
                self.mavlink_send_param_value(the_connection)
                print("PARAM_REQUEST_LIST was sent")
                # trap was found taken it out..... exit(97)
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
                        self.type_of_msg = MAV_CMD_VIDEO_STOP_STREAMING
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
                        print(f"\033[33m DO DIGICAM CONTROL {msg.param1} {msg.param1}")
                        if ((int(msg.param5) == 1) and (int(msg.param7) == 1)):
                            try:
                                if (redCam.redEdgeCaptureFivePicturesNoUpload() == 1):
                                    print("Took the micasense pictures on SD Card")
                                else:
                                    print("Error taking pictures with the micasense camera")
                            except Exception as e:
                                print(f" Tried to take picture ERROR:: {e}") 
                        elif ((int(msg.param5) == 1) and (int(msg.param7) == 0)):
                             try:
                                if (redCam.redEdgeCaptureFivePictures() == 1):
                                    print("saved the pictures to the raspberry Pi")
                                else:
                                    print("error saving the pictures to the raspberry Pi")
                             except Exception as e:
                                print(f" Tried to take picture ERROR:: {e}") 
                        self.Got_Param1 = msg.param1
                        self.Got_Param2 = msg.param2
                        self.Got_Param3 = msg.param3
                        self.Got_Param4 = msg.param4
                        self.Got_Param5 = msg.param5
                        self.Got_Param6 = msg.param6
                        self.Got_Param7 = msg.param7
                        print("\033[36m DO DIGICAM CONTROL COMPLETED")
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

    def raspberry_pi3_set_relay(self, rNum, rState):
        #if self.mavlink10():
        if (rNum == 12):                                         # only relay we defined at the top
            if (rState == True):
                GPIO.output(rNum, GPIO.HIGH)
            else:
                GPIO.output(rNum, GPIO.LOW) 
            return True                
        else:
            return False        

    #
    # set up the pi to use board numbers
    #
    def setUpPIRelayNumBoard( self ):
        GPIO.setmode(GPIO.BOARD)   
    #
    # set up the pi to use relay numbers
    #
    def setUPPiRelayNumBCM( self ):
        GPIO.setmode(GPIO.BCM)      

    #
    # define pinNum as an input pin
    #
    def setPinINput( self, pinNum ):
        GPIO.setup(pinNum, GPIO.IN)    
    #
    # define pinNum as an output pin
    # 
    def setPinOUTput( self, pinNum ):
        GPIO.setup(pinNum, GPIO.OUT)

    #
    # delete the GPIO class instance
    #    
    def delGPIOInstance( self ):
        GPIO.cleanup()

# ----------- for sony api to camera -----------------------------------
#
# ref :- https://github.com/petabite/libsonyapi
#
# on raspberry pi os you might need this first
# sudo apt-get install python3-pip
# sudo apt-get install python3-setuptools
#
# git clone https://github.com/petabite/libsonyapi.git
# cd libsonyapi
# python setup.py install
#
import numpy as np
from libsonyapi.camera import Camera
from libsonyapi.actions import Actions

# ----------- for image saving -----------------------------------------
from PIL import Image

import queue
lifo_queue = queue.LifoQueue(maxsize=20)
fifo_queue = queue.Queue(maxsize=20)

class pySony():

    # connect to the sony camera and print all info
    #
    def createCameraInstance(self):
        camera = Camera()
        camera_info = camera.info()
        print(camera_info)
        print(Camera.do("getAvailableApiList")['result'])
        print(camera.name)  
        print(camera.api_version)  
        return camera
    
    def startMovieRec(self,camera):
        res = camera.do(Actions.startMovieRec)
        return res 
    
    def stopMovieRec(self,camera):
        res = camera.do(Actions.stopMovieRec)
        return res 

    def takeOnePicture(self,camera):
        res = camera.do(Actions.actTakePicture)                             # take a picture
        if res.get('result') is not None:
            print("Result", res)	

    def saveOnePicture(self,camera):
        res = camera.do(Actions.actTakePicture)
        if res.get('result') is not None:
            stopLiveView()
            photo_path = res['result'][0][0]
            photo_name = photo_path.split('/')[-1]
            im = Image.open(requests.get(photo_path, stream=True).raw)
            im.save('images/' + photo_name) 
            lifo_queue.put(photo_name)
            fifo_queue.put(photo_name)
            return photo_path 

    def getLastPicture(self,camera):
        return lifo_queue.get()
	
    def getFirstPicture(self,camera):
        return fifo_queue.get()
	
    def listAllPictures(self):
        while not fifo.empty():
            print(fifo.get(), end=' ')

    def startLiveView(self,camera):
        res = camera.do(Actions.startLiveview)
        print("Liveview", res)
        return res
        
    def stopLiveView(self,camera):
        res = camera.do(Actions.stopLiveview)
        print("Liveview", res)    
        return res
        
    def startRecMode(self,camera):
        res = camera.do(Actions.startRecMode)
        print("Rec Mode ", res) 
        return res
        
    def stopRecMode():
        res = camera.do(Actions.stopRecMo)
        print("Rec Mode ", res)  
        return res
        
    def startContShooting(self,camera):
        res = camera.do(Actions.startContShooting)
        print("Cont Shooting ", res) 
        return res
        
    def stopContShooting(self,camera):
        res = camera.do(Actions.stopContShooting)
        print("Cont Shooting ", res)  
        return res
        
    def startMovieRec(self,camera):
        res = camera.do(Actions.startMovieRec)
        print("Movie ", res) 
        return res
        
    def stopMovieRec(self,camera):
        res = camera.do(Actions.stopMovieRec)
        print("Movie ", res)  
        return res
        
    def startAudioRec(self,camera):
        res = camera.do(Actions.startAudioRec)
        print("Audio ", res) 
        return res
        
    def stopAudioRec(self,camera):
        res = camera.do(Actions.stopAudioRec)
        print("Audio ", res)  
        return res
        
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

    def __del__(self):  
        class_name = self.__class__.__name__  
        print('{} Deleted'.format(class_name))     
 
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
                ret = -6
            
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
                ret = -6
                
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
        return capture_data.status_code,status_code 

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
        return capture_data.status_code,status_code 

        
    # Detect Panel On
    #
    def micaSenseDetectPanelOn( self ):
        dt_params = { "detect_panel" : True } 
        url = "http://" + self.CAM_HOST_IP + "/detect_panel"
        capture_data = self.micaSensePostNoRetry( url, dt_params, True )
        return capture_data.status_code,status_code         

    # Detect Panel On
    #
    def micaSenseDetectPanelOff( self ):
        dt_params = { 
        'abort_detect_panel' : False,	# When 'true', any actively running panel detection captures will be forced to complete.
        'detect_panel'	: True          # When 'true', a panel detection capture is active"detect_panel" : True } 
        }
        url = "http://" + self.CAM_HOST_IP + "/detect_panel"
        capture_data = self.micaSensePostNoRetry( url, dt_params, True )
        return capture_data.status_code,status_code 
   

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
        return capture_data.status_code,status_code 

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
        return capture_data.status_code,status_code 

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
        return capture_data.status_code,status_code 
                
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
        return capture_data.status_code,status_code 
       
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


    # Take a picture and wait for completion status and DO NOT save them to you're hard drive.
    # 
    def redEdgeCaptureFivePicturesNoUpload( self, calibON=False ):

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

            print(f"success..... {statTxt}")
            return 1
            #exit(1)
        else:
            print("====== error ========")
            return -1
            #exit(-1)
#
# The heartbeat task
#
async def sendMavlinkHeartBeat(fm, cID, sleep):
    fm.mavlink_send_GCS_heartbeat(cID)
    while sleep > 0:
        #await asyncio.sleep(1)
        print(f'{sleep} seconds')
        sleep -= 1    

#
# The continuos reading thread
#
async def readMavlinkIncomingData(fm, cID, redCam=0):
    fm.process_messages_from_connection(fm,cID,redCam)

#
# The ACK send thread
#
async def sendMavlinkAckData(fm, cID, sleep, cmd, rpm2, pro, res):
    fm.mavlink_send_ack_command(cID, cmd, rpm2, pro, res)
    while sleep > 0:
        #await asyncio.sleep(1)
        print(f'{sleep} seconds')
        sleep -= 1

#
# The handle with ACK an error during collection that might happen during the send, its told to come again later or its wrong
#
async def execptionMavlinkErrorAckData(fm, cID):
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
        relay_data_result = fm.raspberry_pi3_set_relay(fm.Got_Param1,fm.Got_Param2)
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
        print("setting the relay output %d %d"%(fm.Got_Param1,fm.Got_Param2))
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
# The main thread to run this is the camera receiver client
#        
async def main():

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
        if not ( m.autopilot == mavutil.mavlink.MAV_AUTOPILOT_INVALID ):
            xx = 2
    id = m.get_srcSystem() 
    if not ( m.get_srcSystem() == frame.DEFAULT_SYS_ID ) :
        print("-------- new id found --------")
        while (state == False):
            try:
                cID,state = frame.makeNewMAVlinkConn(id)
            except Exception as e:
                print("Error Trap :: ", e.__class__, " occurred.")
                
    # python sony class
    #
    # pysonyCam = pySony()  
    # camInst = pysonyCam.createCameraInstance()    
    
    print("connect %s"%(cID))  

    # micasense redEye class
    #
    redEdgeCam = micaSenseCamera()
    
    frame.RCV_COMMAND = 0
    frame.RPM2 = 0
    frame.ACK_RESULT = mavutil.mavlink.MAV_RESULT_UNSUPPORTED

    #read_task_1 = asyncio.create_task(readMavlinkIncomingData(frame, cID))
    print("started reader")
    
    while True: 
        read_task_1 = asyncio.create_task(readMavlinkIncomingData(frame, cID, redEdgeCam))
        #await read_task_1 
        print(f"Started in main : {time.strftime('%X')}")
        
        snd_task_1 = asyncio.create_task(sendMavlinkHeartBeat(frame, cID, 1))
        print("hb send....................................................................")
        await snd_task_1

        print("hb end....................................................................ACK RES %s"%(frame.ACK_RESULT))
        #doesnt wait its continuos ---> await read_task_1
        
        if (frame.ACK_RESULT == mavutil.mavlink.MAV_RESULT_ACCEPTED):
            snd_task_2 = asyncio.create_task(sendMavlinkAckData(frame, cID, 1, frame.RCV_COMMAND, frame.RPM2, 0, frame.ACK_RESULT ))      
            await snd_task_2
 
            print("ack end....................................................................")
            frame.task_control_1 = 1 
            #snd_task_3 = asyncio.create_task(processMavlinkMessageData(frame, cID, 1, pysonyCam, camInst, redEyeCam))
            snd_task_3 = asyncio.create_task(processMavlinkMessageData(frame, cID, 2))
            exc_task_error_handler = asyncio.create_task(execptionMavlinkErrorAckData(frame, cID))           
            await snd_task_3 
            await exc_task_error_handler
            print(f"end 2 tasks...............................{frame.RCV_COMMAND} {frame.RPM2} {frame.ACK_RESULT}") 
            snd_task_2 = asyncio.create_task(sendMavlinkAckData(frame, cID, 1, frame.RCV_COMMAND, frame.RPM2, 100, frame.ACK_RESULT )) 
            await snd_task_2
            # re-enable when you want to check this again exit(55)
            print("ack end2...................................................................")
            frame.RCV_COMMAND = 0  
            frame.ACK_RESULT = frame.ACK_ALL_DATA_COMPLETE      
        
        print("completed..................................................")    
        read_task_1.cancel()
        print(f"Ended: {time.strftime('%X')}")

if __name__ == '__main__':
    
# Create our wxPython application and show our frame
# This is the mavlink test reader it should activate the thread upon click
# 
#   app = wx.App()
#   frame = MAVFrame(None)
#   frame.Show()
#   app.MainLoop()

# This is joystick test application to send over UDP port joystick position 
#
#   frame = MAVFrame(None)
#   frame.joystickInit()
#   udpS = frame.initUDPSocket()
#   frame.joyMavlinkInit()
#   frame.processJoystickSendMavlink(udpS)
#   frame.closeUDPSocket(udpS)
#

# This is an example sending app for mavlink camera control messages going out
#
#   frame = MAVFrame()
#   connID = frame.makeMAVlinkConn()
#   print("connect %s"%(connID))
#   frame.mavlink_send_GCS_heartbeat(connID)
#   frame.mavlink_reset_camera(connID)
#   frame.mavlink_video_set_camera_focus(connID, frame.MAV_FOCUS_TYPE_METERS, 1.5)
#   frame.mavlink_image_start_capture(connID, 0.5, 2, 1)
#   frame.mavlink_image_stop_capture(connID)
#   frame.process_messages_from_connection(connID)
##

#
# ===================== Main Multi-Thread send/rcv Task ============================
#
    asyncio.run(main())
