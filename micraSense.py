# ------------------------------------------------------------------ micraSense Camera  Library ----------------------------------------------------------------------------------------------------------
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

class micraSenseCamera():

    # constants / definitions
    #
    HTTP_SUCCESS_RETURN = 200
    WIFI_CAM = "192.168.10.254"
    ETHER_CAM = "192.168.1.83"
    CAM_HOST_IP = WIFI_CAM                               # set this for the camera you want to use
    NTP_SYNC_THRESHOLD = 1000                            # frequency of ntp server syncronisation
    NTP_TIME_SYNC_ENABLE = 1                             # enable if 1 to use ntp timesync :: Internet conenction required (GPRS)
    
    # globals used by the class
    #
    ntp_sync_freq = 0 
    
# =================================================================================== Functions ==================================================================================================================
#
# General functions have prefix micraSense whereas specific camera actions shall have prefix by type e.g. redEye redEdge
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
    
    def print_myJson( self, cap_data ):
        try:
            if (cap_data.status_code == self.HTTP_SUCCESS_RETURN):
                print (cap_data.json())
            else:
                print ("http REST API error")
        except Exception:
            print("invalid json sent to function")
            
    # Post a message to the camera commanding an action
    #
    def micraSensePost( self, url, json_para={ 'block' : True } ):
            
        try:
            capture_data = requests.post( url, json=json_para, timeout=30)
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
            
        print_myJson( capture_data )
        return capture_data  

    # Get a message from the camera reading a status
    #
    def micraSenseGet( self, url, json_para={ 'block' : True } ):
           
        try:
            capture_data = requests.get( url, json=json_para, timeout=30)
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
        print_myJson( capture_data )
        return capture_data 

    def micraSensePrintId( self, capture_data ):
    
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
        
        capture_data = self.micraSensePost( url, capture_params )
        print_myJson( capture_data )
        return capture_data.status_code,status_code 

    # Post a message to the RedEdge camera commanding a capture, block until complete
    #        
    def redEdgeCapture( self ):

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

        capture_data = self.micraSensePost( url, capture_params )
        print_myJson( capture_data )
        return capture_data.status_code,capture_data         

    # Get the RedEye camera capture status, block until complete
    #
    def redEyeCaptureStatus( self, id ):
       
        url = HOST_IP + "/capture/" + id 
        
        capture_data = self.micraSenseGet( url )
        print_myJson( capture_data )
        return capture_data.status_code,status_code 

    # Post a message to the RedEdge camera commanding a capture, block until complete
    #        
    def redEdgeCaptureStatus( self, id ):

        url = HOST_IP + "/capture/" + id 

        capture_data = self.micraSenseGet( url )
        print_myJson( capture_data )
        return capture_data.status_code,capture_data 
        
        json_data_cap_resp = capture_data.json()
        id = str(json_data_cap_resp['id']) 
        
        json_data_cap_resp = capture_data.json()
        id = str(json_data_cap_resp['id']) 
        
    # Download KMZ File
    #
    def redEyeGetKMZ( self ):
           
        url = "http://" + self.CAM_HOST_IP + "/captures.kmz"
        
        capture_data = requests.post(url)
        print_myJson( capture_data )
        return capture_data.status_code,status_code 

    # Download KMZ File
    #
    def redEdgeGetKMZ( self ):
           
        url = "http://" + self.CAM_HOST_IP + "/captures.kmz"
        
        capture_data = requests.post(url)
        print_myJson( capture_data )
        return capture_data.status_code,status_code         

    # Parse the kmz file (xml stream) and print the placemark and co-ordinates
    #
    def micraSenseParseKmzData( self, capture_data ):
    
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
    def micraSenseParseKmzStream( self, capture_data ):
    
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
    def micraSenseSetExposure( self, e1, e2, e3, e4, e5, g1, g2, g3, g4, g5 ):
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
        capture_data = self.micraSensePost( url, exposure_params )
        return capture_data.status_code,status_code 

        
    # Detect Panel On
    #
    def micraSenseDetectPanelOn( self ):
        dt_params = { "detect_panel" : True } 
        url = "http://" + self.CAM_HOST_IP + "/detect_panel"
        capture_data = self.micraSensePost( url, dt_params )
        return capture_data.status_code,status_code         

    # Detect Panel On
    #
    def micraSenseDetectPanelOff( self ):
        dt_params = { 
        'abort_detect_panel' : False,	# When 'true', any actively running panel detection captures will be forced to complete.
        'detect_panel'	: True          # When 'true', a panel detection capture is active"detect_panel" : True } 
        }
        url = "http://" + self.CAM_HOST_IP + "/detect_panel"
        capture_data = self.micraSensePost( url, dt_params )
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
    def micraSenseSetGPS( self, lon, lat, alt, veln, vele, veld, pacc, vacc, fix3d=True ):
        ntp_sync_freq = ntp_sync_freq + 1
        if ((ntp_sync_freq >= self.NTP_SYNC_THRESHOLD) and ( self.NTP_TIME_SYNC_ENABLE >= 1)):
           self.ntp_time_sync()    
           time.sleep(1)
           ntp_sync_freq = 0
        dtime_utc = dt.datetime.now(pytz.utc)
        dt_params = { "latitude" : lat, "longitude" : lon, "altitude" : alt, "vel_n" : veln, "vel_e" : vele, "vel_d" : veld, "p_acc" : pacc, "v_acc" : vacc, "fix3d" : fix3d, utc_time : dtime_utc } 
        url = "http://" + self.CAM_HOST_IP + "/gps"
        capture_data = self.micraSensePost( url, dt_params )
        return capture_data.status_code,status_code 

    # get GPS
    #
    def micraSenseGetGPS( self ):

        url = "http://" + self.CAM_HOST_IP + "/gps"
        capture_data = self.micraSenseGet( url )
        return capture_data
        

    # set orientation
    #
    def micraSenseSetOrientation( self, Aphi, Atheta, Apsi, Cphi, Ctheta, Cpsi ):
    
        orintation_params = { "aircraft_phi" : Aphi, "aircraft_theta" : Atheta, "aircraft_psi" : Apsi, "camera_phi" : Cphi, "camera_theta"	: Ctheta, "camera_psi" : Cpsi }
        url = "http://" + self.CAM_HOST_IP + "/orientation"
        capture_data = self.micraSensePost( url, orintation_params )
        return capture_data.status_code,status_code 

    # get Orientation
    #
    def micraSenseSetGPS( self ):

        url = "http://" + self.CAM_HOST_IP + "/orientation"
        capture_data = self.micraSenseGet( url )
        return capture_data      

    # set picture state (redEdge Only)
    #
    def redEdgeSetState( self, Aphi, Atheta, Apsi, Cphi, Ctheta, Cpsi, lon, lat, alt, veln, vele, veld, pacc, vacc, fix3d=True ):
    
        pic_stat_params = { "aircraft_phi" : Aphi, "aircraft_theta" : Atheta, "aircraft_psi" : Apsi, "camera_phi" : Cphi, "camera_theta"	: Ctheta, "camera_psi" : Cpsi, "latitude" : lat, "longitude" : lon, "altitude" : alt, "vel_n" : veln, "vel_e" : vele, "vel_d" : veld, "p_acc" : pacc, "v_acc" : vacc, "fix3d" : fix3d, utc_time : dtime_utc }
        url = "http://" + self.CAM_HOST_IP + "/capture_state"
        capture_data = self.micraSensePost( url, pic_stat_params )
        return capture_data.status_code,status_code 
                
    # set configuration
    #
    def micraSenseSetConfig( self, streaming_enable=True, streaming_allowed = True, preview_band = "band1", operating_alt = 11, operating_alt_tolerance = 45, overlap_along_track = 11, overlap_cross_track = 5, auto_cap_mode = "overlap", timer_period = 1.2,ext_trigger_mode = "rising", pwm_trigger_threshold = 38.2,	enabled_bands_raw = 43,	enabled_bands_jpeg = 378,enable_man_exposure = True,gain_exposure_crossover = 87.65,	ip_address = "123.456.789.012", raw_format = "TIFF",network_mode = "main", ext_trigger_out_enable = False,	ext_trigger_out_pulse_high = False, agc_minimum_mean = 0.1,	audio_enable = True,audio_select_bitfield = 1,	injected_gps_delay = 9.1 ):
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
        capture_data = self.micraSensePost( url, orintation_params )
        return capture_data.status_code,status_code 
       
    # get pins
    #
    def micraSenseGetPinMux( self ):

        url = "http://" + self.CAM_HOST_IP + "/pin_mux"
        capture_data = self.micraSenseGet( url )
        return capture_data

    # get status
    #
    def micraSenseGetStatus( self ):

        url = "http://" + self.CAM_HOST_IP + "/status"
        capture_data = self.micraSenseGet( url )
        drive_gigaByte_Free = capture_data.json()['sd_gb_free']
        drive_gigaByte_Total = capture_data.json()['sd_gb_total']
        drive_WarningNearFull = capture_data.json()['sd_warn']
        return capture_data, drive_gigaByte_Free, drive_gigaByte_Total, drive_WarningNearFull

    # get status
    #
    def micraSenseGetStatus( self ):

        url = "http://" + self.CAM_HOST_IP + "/networkstatus"
        capture_data = self.micraSenseGet( url )
        drive_gigaByte_Free = capture_data.json()['sd_gb_free']
        drive_gigaByte_Total = capture_data.json()['sd_gb_total']
        drive_WarningNearFull = capture_data.json()['sd_warn']
        return capture_data, drive_gigaByte_Free, drive_gigaByte_Total, drive_WarningNearFull
        
    # get status
    #
    def micraSenseGetTimeSources( self ):

        url = "http://" + self.CAM_HOST_IP + "/timesources"
        capture_data = self.micraSenseGet( url )
        return capture_data
        
    # get time sources 
    #
    def micraSenseGetTimeSources( self ):

        url = "http://" + self.CAM_HOST_IP + "/version"
        capture_data = self.micraSenseGet( url )
        return capture_data
        
    # get files
    #
    def micraSenseGetFiles( self ):

        url = "http://" + self.CAM_HOST_IP + "/files/*"
        # could also be this url = HOST_IP + "/files/000SET/*"
        capture_data = self.micraSenseGet( url )
        return capture_data

    # delete files (uses GET method)
    #
    def micraSenseDelFiles( self ):

        url = "http://" + self.CAM_HOST_IP + "/deletefile/*"
        capture_data = self.micraSenseGet( url )
        return capture_data

    # delete files (uses GET method)
    #
    def micraSenseDelFile( self, fileDirs, fullFileNam ):

        url = "http://" + self.CAM_HOST_IP + "/deletefile/" + fileDirs + "/" + fullFileNam
        # or /deletefile/0000SET/000 or /deletefile/0001SET/000/IMG_1234_1.tif
        capture_data = self.micraSenseGet( url )
        return capture_data

    # set wifi
    #
    def micraSenseSetWiFi( self ):
    
        wifi_params = { "enable" : True }
        url = "http://" + self.CAM_HOST_IP + "/wifi"
        capture_data = self.micraSensePost( url, wifi_params )
        return capture_data.status_code,status_code 

    # reformat SD card 
    #
    def micraSenseReformatSDCard( self ):
    
        sd_params = { "erase_all_data" : True } 
        url = "http://" + self.CAM_HOST_IP + "/reformatsdcard"
        capture_data = self.micraSensePost( url, sd_params )
        return capture_data.status_code,status_code 

    # get information
    #
    def micraSenseGetInfo( self ):

        url = "http://" + self.CAM_HOST_IP + "/camera_info"
        capture_data = self.micraSenseGet( url )
        return capture_data       

    # get Calibration Distortion
    #
    def micraSenseGetCaliDistortion( self ):

        url = "http://" + self.CAM_HOST_IP + "/calibration/distortion"
        capture_data = self.micraSenseGet( url )
        return capture_data  
        
    # get Vignette Calibration 
    #
    def micraSenseGetVignetteCali( self ):

        url = "http://" + self.CAM_HOST_IP + "/calibration/vignette"
        capture_data = self.micraSenseGet( url )
        return capture_data 
        
    # get Rig Relatives Calibration 
    #
    def micraSenseGetVignetteCali( self ):

        url = "http://" + self.CAM_HOST_IP + "/calibration/rig_relatives"
        capture_data = self.micraSenseGet( url )
        return capture_data 

    # Prepare for Power Down 
    #
    def micraSensePreparePowerDwn( self ):
    
        po_params = { "ready_for_power_down" : True, "power_down" : False }  
        url = "http://" + self.CAM_HOST_IP + "/powerdownready"
        capture_data = self.micraSensePost( url, po_params )
        return capture_data.status_code,status_code 

    # Power Down Ready
    #
    def micraSensePowerDwnRdy( self ):
    
        po_params = { "ready_for_power_down" : False, "power_down" : True }   
        url = "http://" + self.CAM_HOST_IP + "/powerdownready"
        capture_data = self.micraSensePost( url, po_params )
        return capture_data.status_code,status_code 

    # get Power Down Status 
    #
    def micraSenseGetPowerDwnStatus( self ):

        url = "http://" + self.CAM_HOST_IP + "/powerdownready"
        capture_data = self.micraSenseGet( url )
        return capture_data 

    # Thermal NUC
    #
    def micraSenseThermalNUC( self ):
    
        nuc_params = { "nuc_now" : True, "elapsed_seconds_since_nuc" : 10, "delta_deg_K_since_nuc" : -0.2, "message" : "NUC request failed" }    
        url = "http://" + self.CAM_HOST_IP + "/thermal_nuc"
        capture_data = self.micraSensePost( url, nuc_params )
        return capture_data.status_code,status_code 
