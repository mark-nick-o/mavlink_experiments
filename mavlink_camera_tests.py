# mavlink_camera_tests.py
#
# Air Cam Pro 2021
# This is tests for python mavlink for camera control 
# It uses snippets and code from the sources given below
#
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


MAV_TARGET = 20
MAV_SOURCE = 255

# import pymavlink.dialects.v10.lapwing as mavlink
# this is a custom dialect which i cant find
from mavlink_python_libs import com1 as commonV1
import com1 as mavdefs
import math
import time

#
# multithreading control via asyncio
#
import asyncio
import time

#
# set to zero if you are not using on rasspberry pi as output trigger command
#
FOR_RASPBERRY_PI = 1
if (FOR_RASPBERRY_PI == 1):
# ============== control Raspberry Pi IO ===============
# sudo apt-get install rpi.gpio
#
    import RPi.GPIO as GPIO
 
# to use Raspberry Pi board pin numbers
    GPIO.setmode(GPIO.BOARD)
 
# set up the GPIO channels - one input and one output here
    GPIO.setup(11, GPIO.IN)
    GPIO.setup(12, GPIO.OUT)

#---------------------------------------------------------------------------

class fifo(object):
    def __init__(self):
        self.buf = []
    def write(self, data):
        self.buf += data
        return len(data)
    def read(self):
        return self.buf.pop(0)
        
# Create a wx.Frame object for the interface
class MAVFrame():

    RCV_COMMAND = mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE
    RPM2 = 0
    ACK_RESULT = 0
 
    # camera informations (default camera routines will retrieve this)
    time_boot_ms = 1213
    firmware_version = 12
    focal_length = 11
    sensor_size_h = 300
    sensor_size_v = 400
    flags = 4
    resolution_h = 300
    resolution_v = 400
    cam_definition_version = 2
    vendor_name = "sony"
    model_name = "alpha750"
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
    status = mavutil.mavlink.STORAGE_STATUS_READY 

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
    flags = 3                                                                 # Bitmap of stream status flags.
    resolution_h = 300                                                        # [pix] Horizontal resolution.
    resolution_v = 400                                                        # [pix] Vertical resolution.
    rotation = 90                                                             # [deg] Video image rotation clockwise.
    hfov = 45                                                                 # [deg] Horizontal Field of view.
    stream_id = 2                                                             # Video Stream ID (1 for first, 2 for second, etc.)
    count = 4                                                                 # Number of streams available.
    type = mavutil.mavlink.VIDEO_STREAM_TYPE_MPEG_TS_H264                     # Type of stream.
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
        
    ACK_ERROR = 0
    errRCV_COMMAND = 0
    errRPM2 = 0

    # task control flag
    task_control_1 = 0

    # global constants
    GOT_ERROR = 1
    GOT_SUCCESS = 2
    GOT_BAD = 3
    GOT_UNFORMAT = 4 
    
    # used to decide what is being requested from the calling (GCS) station
    type_of_msg = 0
    
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
            self.textOutput.AppendText("No Chans %u chan1 %u chan2 %u)\n" % (self.master.chancount, self.master.chan1_raw, self.master.chan2_raw))
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
        print("\033[33m %s %6.3f %6.3f %6.3f"%(text,value1,value2,value3))
        
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
            the_conection = mavutil.mavlink_connection('udpin:0.0.0.0:14550',autoreconnect=True, source_system=mavutil.mavlink.MAV_COMP_ID_AUTOPILOT1,source_component=mavutil.mavlink.MAV_COMP_ID_CAMERA)
            return the_conection,True
        except Exception as err_msg:
            print("Failed to connect : %s" % (err_msg))
            return the_conection,False
        
    # Send heartbeat from a GCS (types are define as enum in the dialect file). 
    #
    def mavlink_send_GCS_heartbeat(self, the_conection): 
        the_conection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_GENERIC, 0, 0, 0)

    # Send heartbeat from a MAVLink application.
    #
    def mavlink_send_OBC_heartbeat(self, the_connection):   
        the_conection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER, mavutil.mavlink.MAV_AUTOPILOT_GENERIC, 0, 0, 0)

    # Send heartbeat from a MAVLink application.
    #
    def mavlink_send_CAM_heartbeat(self, the_connection):   
        the_conection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_CAMERA, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavutil.mavlink.MAV_STATE_ACTIVE)

    # Receive heartbeat from a MAVLink application.
    #
    def mavlink_rcv_heartbeat(self, the_connection):   
        the_connection.wait_heartbeat()
        
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
        # target_system
        # target_component
        # RC channel list, in microseconds.
        the_connection.mav.rc_channels_override_send( the_connection.target_system, the_connection.target_component, *rc_channel_values )   

    # drives a gimbal axis controller to the pitch roll yaw specified
    #
    def gimbal_move_to( self, the_connection, tilt, roll=0, pan=0):
    #"""
    #Moves gimbal to given position
    #Args:
    #    tilt (float): tilt angle in centidegrees (0 is forward)
    #    roll (float, optional): pan angle in centidegrees (0 is forward)
    #    pan  (float, optional): pan angle in centidegrees (0 is forward)
    #"""
        the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component, mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL, 1, tilt, roll, pan, 0, 0, 0, mavutil.mavlink.MAV_MOUNT_MODE_MAVLINK_TARGETING)

    def mavlink10(self,connID):
     #   '''return True if using MAVLink 1.0 or later'''
        return float(connID.WIRE_PROTOCOL_VERSION) >= 1

    def mavlink20(self,connID):
     #  '''return True if using MAVLink 2.0 or later'''
        return float(connID.WIRE_PROTOCOL_VERSION) >= 2		        

    def mavlink_set_relay(self, the_connection, relay_pin=0, state=True):
     #   Set relay_pin to value of state
        #if self.mavlink10():
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
        #else:
        #    print("Setting relays not supported.")

    # ref:- https://mavlink.io/en/messages/common.html#MAV_CMD
    
    def mavlink_video_stop_capture(self, the_connection, streamNo):
        #if self.mavlink10():
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

    def mavlink_video_start_capture(self, the_connection, streamNo, freq):
        #if self.mavlink10():
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

    def mavlink_image_stop_capture(self, the_connection):
        #if self.mavlink10():
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

    def mavlink_image_start_capture(self, the_connection, interval, totalImages, seqNo):
        #if self.mavlink10():
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

    def mavlink_video_stop_streaming(self, the_connection, streamNo):
        #if self.mavlink10():
        the_connection.mav.command_long_send(
            the_connection.target_system,  # target_system
            the_connection.target_component, # target_component
            mavutil.mavlink.MAV_CMD_VIDEO_STOP_STREAMING, # command
            0, # Confirmation
            streamNo, # stream number
            0, # param2
            0, # param3 
            0, # param4
            0, # param5
            0, # param6
            0) # param7

    def mavlink_video_start_streaming(self, the_connection, streamNo):
        #if self.mavlink10():
        the_connection.mav.command_long_send(
            the_connection.target_system,  # target_system
            the_connection.target_component, # target_component
            mavutil.mavlink.MAV_CMD_VIDEO_START_STREAMING, # command
            0, # Confirmation
            streamNo, # stream number
            0, # param2
            0, # param3 
            0, # param4
            0, # param5
            0, # param6
            0) # param7

    # suitable variables to drive CamMode
    #
    MAV_CAMERA_MODE_IMAGE = 0
    MAV_CAMERA_MODE_VIDEO = 1
    MAV_CAMERA_MODE_IMAGE_SURVEY = 2
    
    def mavlink_video_set_camera_mode(self, the_connection, camMode):
        #if self.mavlink10():
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

    # suitable variables to drive CamZoomType
    #
    MAV_ZOOM_TYPE_STEP = 0	        # Zoom one step increment (-1 for wide, 1 for tele)
    MAV_ZOOM_TYPE_CONTINUOUS = 1	# Continuous zoom up/down until stopped (-1 for wide, 1 for tele, 0 to stop zooming)
    MAV_ZOOM_TYPE_RANGE = 2         # Zoom value as proportion of full camera range (a value between 0.0 and 100.0)
    MAV_ZOOM_TYPE_FOCAL_LENGTH = 3  # Zoom value/variable focal length in milimetres
    
    def mavlink_video_set_camera_zoom(self, the_connection, camZoomType, camZoomValue):
        #if self.mavlink10():
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

    MAV_FOCUS_TYPE_STEP = 0	       # Focus one step increment (-1 for focusing in, 1 for focusing out towards infinity).
    MAV_FOCUS_TYPE_CONTINUOUS = 1  # Continuous focus up/down until stopped (-1 for focusing in, 1 for focusing out towards infinity, 0 to stop focusing)
    MAV_FOCUS_TYPE_RANGE = 2	   # Focus value as proportion of full camera focus range (a value between 0.0 and 100.0)
    MAV_FOCUS_TYPE_METERS = 3	   # Focus value in metres

    def mavlink_video_set_camera_focus(self, the_connection, camFocusType, camFocusValue):
        #if self.mavlink10():
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

    def mavlink_do_digicam_configure(self, the_connection, camMode, camShutterSpeed, camAperture, camISO, camExposure, camCommandIdentity, camEngineCutOff):
        #if self.mavlink10():
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

    def mavlink_do_digicam_control(self, the_connection, camSessionControl, camZoomAbsolute, camZoomRelative, camFocus, camShootCommand, camCommandIdentity, camShotID):
        #if self.mavlink10():
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

    def mavlink_do_video_control(self, the_connection, camID, camTransmission, camInterval, camRecording):
        #if self.mavlink10():
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

    def mavlink_get_camera_settings(self, the_connection):
        #if self.mavlink10():
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

    def mavlink_get_storage_info(self, the_connection, StoId):
        #if self.mavlink10():
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

    def mavlink_get_capture_status(self, the_connection):
        #if self.mavlink10():
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

    def mavlink_get_stream_info(self, the_connection):
        #if self.mavlink10():
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

    def mavlink_reset_camera(self, the_connection):
        #if self.mavlink10():
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

    def mavlink_set_camera_trig_interval(self, the_connection, camTriggerCycle, camShutterIntegration):
        #if self.mavlink10():
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

    def mavlink_set_camera_to_quaternion(self, the_connection, q1, q2, q3, q4):
        #if self.mavlink10():
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

    def mavlink_send_camera_information(self, the_connection):
        #if self.mavlink10():
        the_connection.mav.camera_information_send(
            the_connection.target_system,                                      # target_system
            the_connection.target_component,                                   # target_component
            mavutil.mavlink.MAV_CMD_CAMERA_INFORMATION,                        # command
            self.time_boot_ms,
            self.firmware_version,
            self.focal_length,
            self.sensor_size_h,
            self.sensor_size_v,
            self.flags,
            self.resolution_h,
            self.resolution_v,
            self.cam_definition_version,
            self.vendor_name, 
            self.model_name, 
            self.lens_id,
            self.cam_definition_uri)

    def mavlink_send_camera_settings(self, the_connection):
        #if self.mavlink10():
        the_connection.mav.camera_settings_send(
            the_connection.target_system,                                       # target_system
            the_connection.target_component,                                    # target_component
            mavutil.mavlink.MAV_CMD_CAMERA_SETTINGS,                            # command
            self.time_boot_ms,
            self.mode_id,                                                       #  Camera mode
            self.zoomLevel,                                                     #  Current zoom level (0.0 to 100.0, NaN if not known)*/
            self.focusLevel)  

    def mavlink_send_storage_information(self, the_connection):
        #if self.mavlink10():
        the_connection.mav.storage_information_send(
            the_connection.target_system,                                      # target_system
            the_connection.target_component,                                   # target_component
            mavutil.mavlink.MAV_CMD_STORAGE_INFORMATION,                       # command
            self.time_boot_ms,
            self.total_capacity,                                               #  [MiB] Total capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.
            self.used_capacity,                                                #  [MiB] Used capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.
            self.available_capacity,                                           #  [MiB] Available storage capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.
            self.read_speed,                                                   #  [MiB/s] Read speed.
            self.write_speed,                                                  #  [MiB/s] Write speed.
            self.storage_id,                                                   #  Storage ID (1 for first, 2 for second, etc.)
            self.storage_count,                                                #  Number of storage devices
            self.status) 

    def mavlink_send_camera_capture_status(self, the_connection):
        #if self.mavlink10():
        the_connection.mav.camera_capture_status_send(
            the_connection.target_system,                                      # target_system
            the_connection.target_component,                                   # target_component
            mavutil.mavlink.MAV_CMD_CAMERA_CAPTURE_STATUS,                     # command
            self.time_boot_ms,                                                 # [ms] Timestamp (time since system boot).*/
            self.image_interval,                                               # [s] Image capture interval*/
            self.recording_time_ms,                                            # [ms] Time since recording started*/
            self.available_capacity,                                           # [MiB] Available storage capacity.*/
            self.image_status,                                                 # Current status of image capturing (0: idle, 1: capture in progress, 2: interval set but idle, 3: interval set and capture in progress)*/
            self.video_status,                                                 # Current status of video capturing (0: idle, 1: capture in progress)*/
            self.image_count) 
 
    def mavlink_send_video_stream_information(self, the_connection):
        #if self.mavlink10():
        the_connection.mav.video_stream_information_send(
            the_connection.target_system,                                      # target_system
            the_connection.target_component,                                   # target_component
            mavutil.mavlink.MAV_CMD_VIDEO_STREAM_INFORMATION,                  # command
            self.framerate,                                                    #/*< [Hz] Frame rate.
            self.bitrate,                                                      #/*< [bits/s] Bit rate.
            self.flags,                                                        #/*<  Bitmap of stream status flags.
            self.resolution_h,                                                 #/*< [pix] Horizontal resolution.
            self.resolution_v,                                                 #/*< [pix] Vertical resolution.
            self.rotation,                                                     #/*< [deg] Video image rotation clockwise.
            self.hfov,                                                         #/*< [deg] Horizontal Field of view.
            self.stream_id,                                                    #/*<  Video Stream ID (1 for first, 2 for second, etc.)
            self.count,                                                        #/*<  Number of streams available.
            self.type,                                                         #/*<  Type of stream.
            self.videoname,
            self.video_uri)

    def mavlink_send_camera_image_captured(self, the_connection):
        #if self.mavlink10():
        the_connection.mav.video_stream_information_send(
            the_connection.target_system,                                      # target_system
            the_connection.target_component,                                   # target_component
            mavutil.mavlink.MAV_CMD_CAMERA_IMAGE_CAPTURED,                     # command
            self.time_utc,                                                     # [us] Timestamp (time since UNIX epoch) in UTC. 0 for unknown.
            self.time_boot_ms,                                                 # [ms] Timestamp (time since system boot).
            self.lat,                                                          # [degE7] Latitude where image was taken
            self.lon,                                                          # [degE7] Longitude where capture was taken
            self.alt,                                                          # [mm] Altitude (MSL) where image was taken
            self.relative_alt,                                                 # [mm] Altitude above ground
            self.q[0],                                                         #  Quaternion of camera orientation (w, x, y, z order, zero-rotation is 0, 0, 0, 0)
            self.q[1],
            self.q[2],
            self.q[3],
            self.image_index,                                                  #  Zero based index of this image (image count since armed -1)
            self.camera_id,                                                    #  Camera ID (1 for first, 2 for second, etc.)
            self.capture_result,                                               #  Boolean indicating success (1) or failure (0) while capturing this image.
            self.file_url)

            
    # process the incoming messages received
    #
    def process_messages_from_connection(self, the_connection):
        #"""
        #This runs continuously. The mavutil.recv_match() function will call mavutil.post_message()
        #any time a new message is received, and will notify all functions in the master.message_hooks list.
        #"""
        while True:
            # wait heartbeat (only the GCS does this )
            # m = the_connection.recv_match(type="HEARTBEAT", blocking=True, timeout=5)
            #
            # you can also use type lists like this 
            # type=['COMMAND_LONG,RC_CHANNELS']
            #
            msg = the_connection.recv_match(blocking=True, timeout=5)
            if ( the_connection.target_system == msg.get_srcSystem() ):                             # check this and eliminate spurious messages if needed
                print(f"connection {the_connection.target_system} == {msg.get_srcSystem()}")
            last_timestamp = msg._timestamp
            if not msg:
                return
            if msg.get_type() == "BAD_DATA":
                self.ACK_ERROR = self.GOT_BAD
                self.errRCV_COMMAND = 0
                self.errRPM2 = 0
                if mavutil.all_printable(msg.data):
                    sys.stdout.write(msg.data)
                    sys.stdout.flush()
            elif msg.get_type() == 'RC_CHANNELS':
                print("RC Channel message (system %u component %u)\n" % (self.master.target_system, self.master.target_component))
                print("No Chans %u chan1 %u chan2 %u)\n" % (self.master.chancount, self.master.chan1_raw, self.master.chan2_raw))
            elif msg.get_type() == 'COMMAND_LONG':
                print("Long message received (system %u component %u)\n" % (self.master.target_system, self.master.target_component))
                print("Command %u p1 %u p2 %u p3 %u p4 %u \n" % (self.master.command, self.master.param1, self.master.param2, self.master.param3, self.master.param4))
                print("p5 %u p6 %u p7 %u \n" % (self.master.param5, self.master.param6, self.master.param7))  
                if (self.ACK_RESULT == 0):
                    self.RCV_COMMAND = self.master.command
                    if (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE):
                        self.RPM2 = self.master.param1 
                        if (self.RPM2 == mavutil.mavlink.CAMERA_INFORMATION):                       #camera_information
                            self.type_of_msg = 6500
                        elif (self.RPM2 == mavutil.mavlink.CAMERA_SETTINGS):                        #camera_settings
                            self.type_of_msg = 6501                        
                        elif (self.RPM2 == mavutil.mavlink.STORAGE_INFORMATION):                    #storage information
                            self.type_of_msg = 6502
                        elif (self.RPM2 == mavutil.mavlink.CAMERA_CAPTURE_STATUS):                  #camera capture status
                            self.type_of_msg = 6503  
                        elif (self.RPM2 == mavutil.mavlink.MAVLINK_MSG_ID_CAMERA_IMAGE_CAPTURED):   #retrieve lost images
                            self.type_of_msg = 6504   
                            self.Got_Param1 = self.master.param2
                        elif (self.RPM2 == 269):                                                    #video stream
                            self.type_of_msg = 6505                             
                        else:
                            self.type_of_msg = 0
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_SET_RELAY):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_SET_RELAY;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                    elif (self.RCV_COMMAND == mavutil.mavlink. MAV_CMD_VIDEO_START_CAPTURE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_VIDEO_START_CAPTURE;
                        self.Got_Param1 = self.master.param1 
                    elif (self.RCV_COMMAND == mavutil.mavlink. MAV_CMD_VIDEO_STOP_CAPTURE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_VIDEO_START_CAPTURE;
                        self.Got_Param1 = self.master.param1                           
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_IMAGE_START_CAPTURE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_IMAGE_START_CAPTURE;
                        self.Got_Param1 = self.master.param2
                        self.Got_Param2 = self.master.param3
                        self.Got_Param3 = self.master.param4
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_IMAGE_STOP_CAPTURE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_IMAGE_STOP_CAPTURE;
                        self.Got_Param1 = self.master.param3
                        self.Got_Param2 = self.master.param4
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_VIDEO_START_STREAMING):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_VIDEO_START_STREAMING;
                        self.Got_Param1 = self.master.param1
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_VIDEO_STOP_STREAMING):
                        self.type_of_msg = MAV_CMD_VIDEO_STOP_STREAMING;
                        self.Got_Param1 = self.master.param1
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_SET_CAMERA_MODE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_SET_CAMERA_MODE;
                        self.Got_Param1 = self.master.param2
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_SET_CAMERA_ZOOM):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_SET_CAMERA_ZOOM;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                        self.Got_Param3 = self.master.param3
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_SET_CAMERA_FOCUS):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_SET_CAMERA_FOCUS;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONFIGURE):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONFIGURE;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                        self.Got_Param3 = self.master.param3
                        self.Got_Param4 = self.master.param4
                        self.Got_Param5 = self.master.param5
                        self.Got_Param6 = self.master.param6
                        self.Got_Param7 = self.master.param7
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                        self.Got_Param3 = self.master.param3
                        self.Got_Param4 = self.master.param4
                        self.Got_Param5 = self.master.param5
                        self.Got_Param6 = self.master.param6
                        self.Got_Param7 = self.master.param7
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_CONTROL_VIDEO):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_CONTROL_VIDEO;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                        self.Got_Param3 = self.master.param3
                        self.Got_Param4 = self.master.param4
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_SET_CAM_TRIGG_INTERVAL):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_SET_CAM_TRIGG_INTERVAL;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_RESET_CAMERA_SETTINGS):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_RESET_CAMERA_SETTINGS;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL_QUAT):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL_QUAT;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                        self.Got_Param3 = self.master.param3
                        self.Got_Param4 = self.master.param4
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                        self.Got_Param3 = self.master.param3
                        self.Got_Param4 = self.master.param4
                        self.Got_Param5 = self.master.param5
                        self.Got_Param6 = self.master.param6
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_DO_TRIGGER_CONTROL):
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_DO_TRIGGER_CONTROL;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                        self.Got_Param3 = self.master.param3
                    elif (self.RCV_COMMAND == 2004):             # MAV_CMD_CAMERA_TRACK_POINT=2004
                        self.type_of_msg = 2004;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                        self.Got_Param3 = self.master.param3
                    elif (self.RCV_COMMAND == 2005):             # MAV_CMD_CAMERA_TRACK_RECTANGLE=2005
                        self.type_of_msg = 2005;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                        self.Got_Param3 = self.master.param3
                    elif (self.RCV_COMMAND == 2010):             # MAV_CMD_CAMERA_STOP_TRACKING=2010
                        self.type_of_msg = 2010;
                    elif (self.RCV_COMMAND == mavutil.mavlink.MAV_CMD_STORAGE_FORMAT):           
                        self.type_of_msg = mavutil.mavlink.MAV_CMD_STORAGE_FORMAT;
                        self.Got_Param1 = self.master.param1
                        self.Got_Param2 = self.master.param2
                    else:
                        self.RPM2 = 0
                        self.type_of_msg = self.RCV_COMMAND
                    self.ACK_RESULT = mavutil.mavlink.MAV_RESULT_ACCEPTED
                else:
                    self.ACK_ERROR = self.GOT_ERROR
                    self.errRCV_COMMAND = self.master.command
                    self.errRPM2 = self.master.param1
                    
            elif msg.get_type() == 'CAMERA_IMAGE_CAPTURED':
                print("Cam Cap message received (system %u component %u)\n" % (self.master.target_system, self.master.target_component)) 
                print("lat %u lon %u alt %u\n" % (self.master.lat, self.master.lon, self.master.alt)) 
                print("URL %u)\n" % (self.master.file_url))                    

    def mavlink_send_ack_command(self, the_connection, cmd, rpm2, pro, res):
        #if self.mavlink10():
        the_connection.mav.command_ack_send(
            the_connection.target_system,                       # target_system
            the_connection.target_component,                    # target_component
            cmd,                                                # command
            rpm2,                                               # result_param2
            pro,                                                # progress
            res)                                                # result

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
        
# ----------- micaSense RedEye Camera  -----------------------------------
#
# 
#
# 
# for http request
#
# if you have minimal you might need sudo apt install libpython2.7-stdlib
#pip install requests
import requests
import json

class redEye():

    HTTP_SUCCESS_RETURN = 200

# Functions
#
    #def print_myJson( self, cap_data ):
    #    if (cap_data.status_code == self.HTTP_SUCCESS_RETURN):
    #        print cap_data.json()
    #    else:
    #        print "http REST API error"
        
    # Post a message to the camera commanding a capture, block until complete
    #
    def redEyeCapture( self ):
        capture_params = { 'store_capture' : True, 'block' : True }
        capture_data = requests.post("http://192.168.10.254/capture", json=capture_params)
        #print_myJson( capture_data )
        return cap_data.status_code

#
# The heartbeat task
#
async def sendMavlinkHeartBeat(fm, cID, sleep):
    fm.mavlink_send_CAM_heartbeat(cID)
    while sleep > 0:
        await asyncio.sleep(1)
        print(f'{sleep} seconds')
        sleep -= 1    

#
# The continuos reading thread
#
async def readMavlinkIncomingData(fm, cID):
    fm.process_messages_from_connection(cID)

#
# The ACK send thread
#
async def sendMavlinkAckData(fm, cID, sleep, cmd, rpm2, pro, res):
    fm.mavlink_send_ack_command(cID, cmd, rpm2, pro, res)
    while sleep > 0:
        await asyncio.sleep(1)
        print(f'{sleep} seconds')
        sleep -= 1

#
# The handle with ACK an error during collection that might happen during the send, its told to come again later or its wrong
#
async def exceptionMavlinkErrorAckData(fm, cID):
    while fm.task_control_1 > 0:
        await asyncio.sleep(1)
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
async def processMavlinkMessageData(fm, cID, sleep, sonycam, caminst, redeyecam ):

    # define what is sent in param1
    myRedEyeCamera = 1
    mySonyCamera = 2
    mySonyCameraContShoot = 3 
    
    if (fm.type_of_msg == 65000):
        #
        ## TODO :: Add the cmera retrieval class cam_data_result = fm.getCameraInfomationFromCam()
        #
        cam_data_result = fm.GOT_SUCCESS
        if (cam_data_result == fm.GOT_SUCCESS):
            fm.mavlink_send_camera_information(cID)
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED        
    elif (fm.type_of_msg == 65001):
        #
        ## TODO :: Add the cmera retrieval class cam_data_result = fm.getCameraSettingsFromCam()
        #
        cam_data_result = fm.GOT_SUCCESS
        if (cam_data_result == fm.GOT_SUCCESS):
            fm.mavlink_send_camera_settings(cID)
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == 65002):
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
    elif (fm.type_of_msg == 65003):
        #
        ## TODO :: Add the cmera retrieval class cam_data_result = fm.getCameraCaptureStatusFromCam()
        #
        cam_data_result = fm.GOT_SUCCESS
        if (cam_data_result == fm.GOT_SUCCESS):
            fm.mavlink_send_camera_capture_status(cID)
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == 65004):
        #
        ## TODO :: Add the cmera retrieval class cam_data_result = fm.getCameraCaptureInformationFromCam(self.Got_Param1)
        #
        cam_data_result = fm.GOT_SUCCESS
        if (cam_data_result == fm.GOT_SUCCESS):
            fm.mavlink_send_camera_capture_information(cID)
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_IN_PROGRESS
        else:
            fm.ACK_RESULT = mavutil.mavlink.MAV_RESULT_FAILED
    elif (fm.type_of_msg == 65005):
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
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_SET_CAMERA_ZOOM):
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
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_SET_CAMERA_FOCUS):
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
    elif (fm.type_of_msg == mavutil.mavlink.MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW):
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
            
    while sleep > 0:
        await asyncio.sleep(1)
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

    # python sony class
    #
    # pysonyCam = pySony()  
    # camInst = pysonyCam.createCameraInstance()    
    
    print("connect %s"%(cID))  

    # micasense redEye class
    redEyeCam = redEye()
    
    
    frame.RCV_COMMAND = 0
    frame.RPM2 = 0
    frame.ACK_RESULT = 0

    read_task_1 = asyncio.create_task(readMavlinkIncomingData(frame, cID))
        
    while True: 
        print(f"Started: {time.strftime('%X')}")
        
        snd_task_1 = asyncio.create_task(sendMavlinkHeartBeat(frame, cID, 1))
        await snd_task_1

        #doesnt wait its continuos ---> await read_task_1
        
        if not (frame.ACK_RESULT == 0):
            snd_task_2 = asyncio.create_task(sendMavlinkAckData(frame, cID, 1, frame.RCV_COMMAND, frame.RPM2, 0, frame.ACK_RESULT ))      
            await snd_task_2
 
            fm.task_control_1 = 1 
            #snd_task_3 = asyncio.create_task(processMavlinkMessageData(frame, cID, 1, pysonyCam, camInst, redEyeCam))
            snd_task_3 = asyncio.create_task(processMavlinkMessageData(frame, cID, 2))
            exc_task_error_handler = asyncio.create_task(execptionMavlinkErrorAckData(frame, cID))           
            await snd_task_3 
            await exc_task_error_handler
            
            snd_task_2 = asyncio.create_task(sendMavlinkAckData(frame, cID, 1, frame.RCV_COMMAND, frame.RPM2, 100, frame.ACK_RESULT )) 
            await snd_task_2

            frame.RCV_COMMAND = 0  
            frame.ACK_RESULT = 0      
            
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
