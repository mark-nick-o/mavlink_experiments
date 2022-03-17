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

if __name__ == '__main__':

    myRedEdgeCamNo1 = micaSenseCamera()

    #
    # show the disk free 
    #
    diskFreePercent = myRedEdgeCamNo1.getDiskFree()

    #
    # command it to calibrating using the panel
    #
    #if (myRedEdgeCamNo1.redEdgeCaptureFivePictures(myRedEdgeCamNo1.CALIBRATE_USING_PANEL) == 2):
    #    print("success @ calibration")
    #else:
    #    print("failure in calibration")
        
    #
    # command it to take a picture
    #
    if (myRedEdgeCamNo1.redEdgeCaptureFivePictures() == 1):
        print("saved the pictures")
    else:
        print("error saving the pictures")

    a,b = myRedEdgeCamNo1.redEdgeGetKMZ()
    print(f" ret {a} KMZ {b}")

    #
    # get vasrious status about the camera
    #
    print(">>>>>>>>>>>>>>>> Status >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetStatus()

    print(">>>>>>>>>>>>>>>> Time >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetTimeSources()

    print(">>>>>>>>>>>>>>>> Files >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetFiles()

    print(">>>>>>>>>>>>>>>> Info >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetInfo()

    print(">>>>>>>>>>>>>>>> Network >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetNetworkStatus()

    print(">>>>>>>>>>>>>>>> Version >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetVersion()

    print(">>>>>>>>>>>>>>>> Get Information >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetInfo()

    print(">>>>>>>>>>>>>>>> Cali Dist >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetCaliDistortion()

    print(">>>>>>>>>>>>>>>> Vignette Cali  >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetVignetteCali()

    print(">>>>>>>>>>>>>>>> Rig Relatives Cali  >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetRigRelCali()

    print(">>>>>>>>>>>>>>>> Get Pin Mux  >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetPinMux()

    print(">>>>>>>>>>>>>>>> Get GPS  >>>>>>>>>>>>>>>>>>>>>>>>>")
    a = myRedEdgeCamNo1.micaSenseGetGPS()

    print(">>>>>>>>>>>>>>>> Get Exposure Call  >>>>>>>>>>>>>>>>>>>>>>>>>")
    print(micaSenseGetExposure())
    
    #print(">>>>>>>>>>>>>>>> Reformat SD Card >>>>>>>>>>>>>>>>>")
    #a,b = myRedEdgeCamNo1.micaSenseReformatSDCard()
    #if (a == 200):
    #    stateOfFormat = b.json()
    #    if not (stateOfFormat['reformat_status'].find("success") == -1):
    #        print(">>>>>>>>>>>>>> Re-Format OK >>>>>>>>>>>")

    #myRedEdgeCamNo1.micaSenseSetConfig()
    #myRedEdgeCamNo1.micaSensePreparePowerDwn()
    #myRedEdgeCamNo1.micaSensePowerDwnRdy()
