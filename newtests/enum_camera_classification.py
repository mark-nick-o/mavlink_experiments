#
# Enumeration of various types of sony camera, options (maximum all mode, list of features in that model of camera) and cp_enumeration (number assigned to the feature in the API and GUI)  
#

import enum

# --------------- each camera has a set of enumerations for each functionality and its available options --------------------------------------
 
# =========================== White Balance ==============================================================

class sonyClassWhiteBalanceCpEnums(enum.IntEnum):

    CrWhiteBalance_AWB	= 0
    CrWhiteBalance_Underwater_Auto = 1
    CrWhiteBalance_Daylight	= 17
    CrWhiteBalance_Shadow = 18
    CrWhiteBalance_Cloudy = 19
    CrWhiteBalance_Tungsten = 20
    CrWhiteBalance_Fluorescent = 32
    CrWhiteBalance_Fluorescent_WarmWhite = 33
    CrWhiteBalance_Fluorescent_CoolWhite = 34
    CrWhiteBalance_Fluorescent_DayWhite = 35
    CrWhiteBalance_Fluorescent_Daylight = 36
    CrWhiteBalance_Flush = 48
    CrWhiteBalance_ColorTemp = 256
    CrWhiteBalance_Custom_1 = 257
    CrWhiteBalance_Custom_2 = 258
    CrWhiteBalance_Custom_3 = 259
    CrWhiteBalance_Custom = 260
    
#
#  consider grabbing all params from camera and writing these automatically (its what list is pulled out for each camera)
#  This is the capability of the model
#
class sonyClassAlpha7WhiteBalanceOptions(enum.IntEnum):

    CrWhiteBalance_AWB	= 0
    CrWhiteBalance_Underwater_Auto = 10
    CrWhiteBalance_Daylight	= 1
    CrWhiteBalance_Shadow = 2
    CrWhiteBalance_Cloudy = 3
    CrWhiteBalance_Tungsten = 4
    CrWhiteBalance_Fluorescent_WarmWhite = 5
    CrWhiteBalance_Fluorescent_CoolWhite = 6
    CrWhiteBalance_Fluorescent_DayWhite = 7
    CrWhiteBalance_Fluorescent_Daylight = 8
    CrWhiteBalance_Flush = 9
    CrWhiteBalance_ColorTemp = 11
    CrWhiteBalance_Custom_1 = 12
    CrWhiteBalance_Custom_2 = 13
    CrWhiteBalance_Custom_3 = 14

# =========================== Focus Mode ==============================================================

class sonyClassFocusModeCpEnums(enum.IntEnum):

    CrFocus_MF	= 1
    CrFocus_AF_S = 2
    CrFocus_AF_C = 3
    CrFocus_AF_A = 4
    CrFocus_AF_D = 5
    CrFocus_DMF = 6
    CrFocus_PF = 7

class sonyClassAlpha7FocusModeOptions(enum.IntEnum):

    CrFocus_MF	= 4
    CrFocus_AF_S = 0
    CrFocus_AF_C = 2
    CrFocus_AF_A = 1
    CrFocus_AF_D = 5
    CrFocus_DMF = 3

# =========================== Aperture ==============================================================

class sonyClassApertureCpEnums(enum.IntEnum):

    F2_8 = 280
    F3_2 = 320
    F3_5 = 350
    F4_0 = 400
    F4_5 = 450 
    F5_0 = 500   
    F5_6 = 560     
    F6_3 = 630    
    F7_1 = 710  
    F8_0 = 800   
    F9_0 = 900  
    F10 = 1000         
    F11 = 1100  
    F13 = 1300   
    F14 = 1400    
    F16 = 1600        
    F18 = 1800      
    F20 = 2000     
    F22 = 2200

class sonyClassAlpha7ApertureOptions(enum.IntEnum):

    F2_8 = 0
    F3_2 = 1
    F3_5 = 2
    F4_0 = 3
    F4_5 = 4 
    F5_0 = 5    
    F5_6 = 6     
    F6_3 = 7     
    F7_1 = 8   
    F8_0 = 9   
    F9_0 = 10  
    F10 = 11         
    F11 = 12   
    F13 = 13    
    F14 = 14     
    F16 = 15         
    F18 = 16       
    F20 = 17         
    F22 = 18

# =========================== Iso ==============================================================

class sonyClassIsoCpEnums(enum.IntEnum):

    ISO0 = 0
    ISO50 = 50
    ISO64 = 64
    ISO80 = 80
    ISO100 = 100
    ISO125 = 125
    ISO160 = 160
    ISO200 = 200
    ISO250 = 250
    ISO320 = 320
    ISO400 = 400
    ISO500 = 500
    ISO640 = 640
    ISO800 = 800
    ISO1000 = 1000
    ISO1250 = 1250
    ISO1600 = 1600
    ISO2000 = 2000
    ISO2500 = 2500
    ISO3200 = 3200
    ISO4000 = 4000
    ISO5000 = 5000
    ISO6400 = 6400
    ISO8000 = 8000
    ISO10000 = 10000 
    ISO12800 = 12800
    ISO16000 = 16000
    ISO20000 = 20000
    ISO25600 = 25600
    ISO32000 = 32000
    ISO40000 = 40000
    ISO51200 = 51200 
    ISO64000 = 64000
    ISO80000 = 80000     
    ISO102400 = 102400    

class sonyClassAlpha7IsoOptions(enum.IntEnum):

    ISO0 = 0
    ISO50 = 1
    ISO64 = 2
    ISO80 = 3
    ISO100 = 4
    ISO125 = 5
    ISO160 = 6
    ISO200 = 7
    ISO250 = 8
    ISO320 = 9
    ISO400 = 10
    ISO500 = 11
    ISO640 = 12
    ISO800 = 13
    ISO1000 = 14
    ISO1250 = 15
    ISO1600 = 16
    ISO2000 = 17
    ISO2500 = 18
    ISO3200 = 19
    ISO4000 = 20
    ISO5000 = 21
    ISO6400 = 22
    ISO8000 = 23 
    ISO10000 = 24  
    ISO12800 = 25 
    ISO16000 = 26   
    ISO20000 = 27 
    ISO25600 = 28  
    ISO32000 = 29 
    ISO40000 = 30
    ISO51200 = 31 
    ISO64000 = 32   
    ISO80000 = 33       
    ISO102400 = 34 

# =========================== Focus Area ==============================================================

class sonyClassFocusAreaCpEnums(enum.IntEnum):

    CrFocusArea_Unknown	= 0
    CrFocusArea_Wide = 1
    CrFocusArea_Zone = 2
    CrFocusArea_Center = 3
    CrFocusArea_Flexible_Spot_S = 4
    CrFocusArea_Flexible_Spot_M = 5
    CrFocusArea_Flexible_Spot_L = 6
    CrFocusArea_Expand_Flexible_Spot = 7
    CrFocusArea_Flexible_Spot = 8
    CrFocusArea_Tracking_Wide = 17
    CrFocusArea_Tracking_Zone = 18
    CrFocusArea_Tracking_Center = 19
    CrFocusArea_Tracking_Flexible_Spot_S = 20
    CrFocusArea_Tracking_Flexible_Spot_M = 21
    CrFocusArea_Tracking_Flexible_Spot_L = 22
    CrFocusArea_Tracking_Expand_Flexible_Spot = 23
    CrFocusArea_Tracking_Flexible_Spot = 24
    
class sonyClassAlpha7FocusAreaOptions(enum.IntEnum):

    CrFocusArea_Wide = 0
    CrFocusArea_Zone = 1
    CrFocusArea_Center = 2
    CrFocusArea_Flexible_Spot_S = 3
    CrFocusArea_Flexible_Spot_M = 4
    CrFocusArea_Flexible_Spot_L = 5
    CrFocusArea_Expand_Flexible_Spot = 6
    CrFocusArea_Flexible_Spot = 7

# =========================== Exposure Program ==============================================================  

class sonyClassExProCpEnums(enum.IntEnum):

    CrExposure_M_Manual	= 1
    CrExposure_P_Auto = 2
    CrExposure_A_AperturePriority = 3
    CrExposure_S_ShutterSpeedPriority = 4
    CrExposure_Program_Creative = 5
    CrExposure_Program_Action = 6
    CrExposure_Portrait = 7
    CrExposure_Auto	= 32768
    CrExposure_Auto_Plus = 32769
    CrExposure_P_A = 32770
    CrExposure_P_S = 32771
    CrExposure_Sports_Action = 32772
    CrExposure_Sprots_Action = 32773
    CrExposure_Sunset = 32774
    CrExposure_Night = 32775
    CrExposure_Landscape = 32776
    CrExposure_Macro = 32777
    CrExposure_HandheldTwilight = 32778
    CrExposure_NightPortrait = 32779
    CrExposure_AntiMotionBlur = 32780
    CrExposure_Pet = 32781
    CrExposure_Gourmet = 32782
    CrExposure_Fireworks = 32783
    CrExposure_HighSensitivity = 32784
    CrExposure_MemoryRecall	= 32800
    CrExposure_ContinuousPriority_AE_8pics = 32817
    CrExposure_ContinuousPriority_AE_10pics = 32818
    CrExposure_ContinuousPriority_AE_12pics = 32819
    CrExposure_3D_SweepPanorama	= 32832
    CrExposure_SweepPanorama = 32833
    CrExposure_Movie_P = 32848
    CrExposure_Movie_A = 32849
    CrExposure_Movie_S = 32850
    CrExposure_Movie_M = 32851
    CrExposure_Movie_Auto = 32852
    CrExposure_Movie_SQMotion_P	= 32857
    CrExposure_Movie_SQMotion_A = 32858
    CrExposure_Movie_SQMotion_S = 32859
    CrExposure_Movie_SQMotion_M = 32860
    CrExposure_Flash_Off = 32864
    CrExposure_PictureEffect = 32880
    CrExposure_HiFrameRate_P = 32896
    CrExposure_HiFrameRate_A = 32897
    CrExposure_HiFrameRate_S = 32898
    CrExposure_HiFrameRate_M = 32899
    CrExposure_SQMotion_P = 32900
    CrExposure_SQMotion_A = 32901
    CrExposure_SQMotion_S = 32902
    CrExposure_SQMotion_M = 32903
    CrExposure_MOVIE = 32904
    CrExposure_STILL = 32905

class sonyClassAlpha7ExProOptions(enum.IntEnum):

    CrExposure_Movie_S = 2
    CrExposure_Movie_P = 0
    CrExposure_Movie_A = 1
    CrExposure_Movie_M = 3

# =========================== Shutter Speed ==============================================================  

class sonyClassShutterSpeedCpEnums(enum.IntEnum):

    s0 = 0   
    s30 = 19660810
    s25 = 16384010
    s20 = 13107210
    s15 = 9830410
    s13 = 8519690
    s10 = 6553610
    s8 = 5242890
    s6 = 3932170
    s5 = 3276810
    s4 = 2621450
    s3_2 = 2097162
    s2_5 = 1638410
    s2 = 1310730
    s1_6 = 1048586
    s1_3 = 851978
    s1 = 655370
    s0_8 = 524298
    s0_6 = 393226
    s0_5 = 327690
    s0_4 = 262154
    s1d3 = 65539
    s1d4 = 65540
    s1d5 = 65541
    s1d6 = 65542
    s1d8 = 65544
    s1d10 = 65546
    s1d13 = 65549
    s1d15 = 65551
    s1d20 = 65556
    s1d25 = 65561
    s1d30 = 65566
    s1d40 = 65576
    s1d50 = 65586
    s1d60 = 65596
    s1d80 = 65616
    s1d100 = 65636
    s1d125 = 65661
    s1d160 = 65696
    s1d200 = 65736
    s1d250 = 65786
    s1d320 = 65856
    s1d400 = 65936
    s1d500 = 66036
    s1d640 = 66176 
    s1d800 = 66336
    s1d1000 = 66536  
    s1d1250 = 66786
    s1d1600 = 67136
    s1d2000 = 67536 
    s1d2500 = 68036  
    s1d3200 = 68736 
    s1d4000 = 69536 
    s1d5000 = 70536  
    s1d6400 = 71936
    s1d8000 = 73536

class sonyClassAlpha7ShutterSpeedOptions(enum.IntEnum):

    s0 = 0        
    s30 = 1
    s25 = 2
    s20 = 3
    s15 = 4
    s13 = 5
    s10 = 6
    s8 = 7
    s6 = 8
    s5 = 9
    s4 = 10
    s3_2 = 11
    s2_5 = 12
    s2 = 13
    s1_6 = 14
    s1_3 = 15
    s1 = 16
    s0_8 = 17
    s0_6 = 18
    s0_5 = 19
    s0_4 = 20
    s1d3 = 21
    s1d4 = 22
    s1d5 = 23
    s1d6 = 24
    s1d8 = 25
    s1d10 = 26
    s1d13 = 27
    s1d15 = 28
    s1d20 = 29
    s1d25 = 30
    s1d30 = 31
    s1d40 = 32
    s1d50 = 33
    s1d60 = 34
    s1d80 = 35
    s1d100 = 36
    s1d125 = 37
    s1d160 = 38 
    s1d200 = 39 
    s1d250 = 40
    s1d320 = 41 
    s1d400 = 42 
    s1d500 = 43 
    s1d640 = 44  
    s1d800 = 45  
    s1d1000 = 46  
    s1d1250 = 47
    s1d1600 = 48 
    s1d2000 = 49  
    s1d2500 = 50   
    s1d3200 = 51  
    s1d4000 = 52  
    s1d5000 = 53  
    s1d6400 = 54 
    s1d8000 = 55

# =========================== Still Capture mode ==============================================================  

class sonyClassStillCaptureCpEnums(enum.IntEnum):

    CrDrive_Single = 1
    CrDrive_Continuous_Hi = 65537
    CrDrive_Continuous_Hi_Plus = 65538
    CrDrive_Continuous_Hi_Live = 65539
    CrDrive_Continuous_Lo = 65540
    CrDrive_Continuous = 65541
    CrDrive_Continuous_SpeedPriority = 65542
    CrDrive_Continuous_Mid = 65543
    CrDrive_Continuous_Mid_Live = 65544
    CrDrive_Continuous_Lo_Live = 65545
    CrDrive_SingleBurstShooting_lo = 69633
    CrDrive_SingleBurstShooting_mid = 69644
    CrDrive_SingleBurstShooting_hi = 69645
    CrDrive_Timelapse = 131073
    CrDrive_Timer_2s = 196609
    CrDrive_Timer_5s = 196610
    CrDrive_Timer_10s = 196611
    CrDrive_Continuous_Bracket_03Ev_3pics = 262913
    CrDrive_Continuous_Bracket_03Ev_5pics = 262914
    CrDrive_Continuous_Bracket_03Ev_9pics = 262915
    CrDrive_Continuous_Bracket_05Ev_3pics = 262916
    CrDrive_Continuous_Bracket_05Ev_5pics = 262917
    CrDrive_Continuous_Bracket_05Ev_9pics = 262918
    CrDrive_Continuous_Bracket_07Ev_3pics = 262919
    CrDrive_Continuous_Bracket_07Ev_5pics = 262920
    CrDrive_Continuous_Bracket_07Ev_9pics = 262921
    CrDrive_Continuous_Bracket_10Ev_3pics = 262922
    CrDrive_Continuous_Bracket_10Ev_5pics = 262923
    CrDrive_Continuous_Bracket_10Ev_9pics = 262924
    CrDrive_Continuous_Bracket_20Ev_3pics = 262925
    CrDrive_Continuous_Bracket_20Ev_5pics = 262926
    CrDrive_Continuous_Bracket_30Ev_3pics = 262927
    CrDrive_Continuous_Bracket_30Ev_5pics = 262928
    CrDrive_Single_Bracket_03Ev_3pics = 327681
    CrDrive_Single_Bracket_03Ev_5pics = 327682
    CrDrive_Single_Bracket_03Ev_9pics = 327683
    CrDrive_Single_Bracket_05Ev_3pics = 327684
    CrDrive_Single_Bracket_05Ev_5pics = 327685
    CrDrive_Single_Bracket_05Ev_9pics = 327686
    CrDrive_Single_Bracket_07Ev_3pics = 327687
    CrDrive_Single_Bracket_07Ev_5pics = 327688
    CrDrive_Single_Bracket_07Ev_9pics = 327689
    CrDrive_Single_Bracket_10Ev_3pics = 327690
    CrDrive_Single_Bracket_10Ev_5pics = 327691
    CrDrive_Single_Bracket_10Ev_9pics = 327692
    CrDrive_Single_Bracket_20Ev_3pics = 327693
    CrDrive_Single_Bracket_20Ev_5pics = 327694
    CrDrive_Single_Bracket_30Ev_3pics = 327695
    CrDrive_Single_Bracket_30Ev_5pics = 327696
    CrDrive_WB_Bracket_Lo = 393217
    CrDrive_WB_Bracket_Hi = 393218
    CrDrive_DRO_Bracket_Lo = 458753
    CrDrive_DRO_Bracket_Hi = 458754
    CrDrive_Continuous_Timer_3pics = 524289
    CrDrive_Continuous_Timer_5pics = 524290
    CrDrive_Continuous_Timer_2s_3pics = 524291
    CrDrive_Continuous_Timer_2s_5pics = 524292
    CrDrive_Continuous_Timer_5s_3pics = 524293
    CrDrive_Continuous_Timer_5s_5pics = 524294
    CrDrive_LPF_Bracket	= 989681
    CrDrive_RemoteCommander	= 989682
    CrDrive_MirrorUp = 989683
    CrDrive_SelfPortrait_1	= 989684
    CrDrive_SelfPortrait_2	= 989685
    
class sonyClassAlpha7StillCaptureOptions(enum.IntEnum):
   
    CrDrive_Continuous_Mid = 2
    CrDrive_Single = 0
    CrDrive_Continuous_Lo = 1
    CrDrive_Continuous_Hi = 3
    CrDrive_Continuous_Hi_Plus = 4
    CrDrive_Timer_10s = 5
    CrDrive_Timer_5s = 6
    CrDrive_Timer_2s = 7
    CrDrive_Continuous_Timer_3pics = 8
    CrDrive_Continuous_Timer_5pics = 9
    CrDrive_Continuous_Timer_5s_3pics = 10
    CrDrive_Continuous_Timer_5s_5pics = 11
    CrDrive_Continuous_Timer_2s_3pics = 12
    CrDrive_Continuous_Timer_2s_5pics = 13
    CrDrive_Continuous_Bracket_03Ev_3pics = 14
    CrDrive_Continuous_Bracket_03Ev_5pics = 15
    CrDrive_Continuous_Bracket_03Ev_9pics = 16
    CrDrive_Continuous_Bracket_05Ev_3pics = 17
    CrDrive_Continuous_Bracket_05Ev_5pics = 18
    CrDrive_Continuous_Bracket_05Ev_9pics = 19
    CrDrive_Continuous_Bracket_07Ev_3pics = 20
    CrDrive_Continuous_Bracket_07Ev_5pics = 21
    CrDrive_Continuous_Bracket_07Ev_9pics = 22
    CrDrive_Continuous_Bracket_10Ev_3pics = 23
    CrDrive_Continuous_Bracket_10Ev_5pics = 24
    CrDrive_Continuous_Bracket_10Ev_9pics = 25
    CrDrive_Continuous_Bracket_20Ev_3pics = 26
    CrDrive_Continuous_Bracket_20Ev_5pics = 27
    CrDrive_Continuous_Bracket_30Ev_3pics = 28
    CrDrive_Continuous_Bracket_30Ev_5pics = 29
    CrDrive_Single_Bracket_03Ev_3pics = 30
    CrDrive_Single_Bracket_03Ev_5pics = 31
    CrDrive_Single_Bracket_03Ev_9pics = 32
    CrDrive_Single_Bracket_05Ev_3pics = 33
    CrDrive_Single_Bracket_05Ev_5pics = 34
    CrDrive_Single_Bracket_05Ev_9pics = 35
    CrDrive_Single_Bracket_07Ev_3pics = 36
    CrDrive_Single_Bracket_07Ev_5pics = 37
    CrDrive_Single_Bracket_07Ev_9pics = 38
    CrDrive_Single_Bracket_10Ev_3pics = 39
    CrDrive_Single_Bracket_10Ev_5pics = 40
    CrDrive_Single_Bracket_10Ev_9pics = 41
    CrDrive_Single_Bracket_20Ev_3pics = 42
    CrDrive_Single_Bracket_20Ev_5pics = 43
    CrDrive_Single_Bracket_30Ev_3pics = 44
    CrDrive_Single_Bracket_30Ev_5pics = 45          
    CrDrive_WB_Bracket_Hi = 46
    CrDrive_WB_Bracket_Lo = 47
    CrDrive_DRO_Bracket_Hi = 48
    CrDrive_DRO_Bracket_Lo = 49
            
#
#                       These are examples of other cameras at present set as dummy data
#
# ============================================== EClass Camera ==========================================================================
#

# ================================================ ISO =========================================================================================

#
#
#  consider creating automatically from the .hpp file (its name and enumeration that the API understands)
#  This is the manufacture capability of the camera
#
class eClassApertureCpEnums(enum.IntEnum):

    F1_6 = 60
    F3 = 18
    F4 = 389
    F6 = 4080
    F20 = 5080
    F600 = 999

#
#  consider grabbing all params from camera and writing these automatically (its what list is pulled out for each camera)
#  This is the capability of the model
#
class eClassModel1ApertureOptions(enum.IntEnum):

    F1_6 = 0
    F3 = 1
    F4 = 3
    F6 = 4
    F20 = 5

#
#  consider grabbing all params from camera and writing these automatically (its what list is pulled out for each camera)
#  This is the capability of the model
#
class eClassModel2ApertureOptions(enum.IntEnum):

    F1_6 = 0
    F3 = 1
    F4 = 3
    F6 = 4
    F20 = 5
    F600 = 6

# ================================================ ISO =========================================================================================

class eClassIsoCpEnums(enum.IntEnum):

    ISO1 = 80
    ISO2 = 100
    ISO3 = 300
    ISO4 = 400
    ISO5 = 500
    ISO6 = 600
    
#
#  consider grabbing all params from camera and writing these automatically (its what list is pulled out for each camera)
#  This is the capability of the model
#
class eClassModel1IsoOptions(enum.IntEnum):

    ISO2 = 0
    ISO3 = 1
    ISO5 = 2
    ISO6 = 3

#
#  consider grabbing all params from camera and writing these automatically (its what list is pulled out for each camera)
#  This is the capability of the model
#
class eClassModel2IsoOptions(enum.IntEnum):

    ISO1 = 0
    ISO2 = 1
    ISO3 = 3
    ISO4 = 4
    ISO5 = 5
    ISO6 = 6
    
# ============ FClass Camera ===============================
# 
#
class fClassApertureCpEnums(enum.IntEnum):

    F1_6 = 620
    F3 = 1438
    F4 = 3869
    F6 = 4080
    F20 = 504680
    F60 = 4680
    
class fClassApertureOptions(enum.IntEnum):

    F1_6 = 0
    F3 = 1
    F4 = 2
    F6 = 3
    F20 = 5

#
# each feature set is a list of class names which enumerate the class each way
#	
FEATURE_SET_1 = {
    'iso': [ sonyClassIsoCpEnums, sonyClassAlpha7IsoOptions ],
    'white_bal': [ sonyClassWhiteBalanceCpEnums, sonyClassAlpha7WhiteBalanceOptions ],
    'focus_mode': [ sonyClassFocusModeCpEnums, sonyClassAlpha7FocusModeOptions ],
    'focus_area': [ sonyClassFocusAreaCpEnums, sonyClassAlpha7FocusAreaOptions ],
    'shutter_speed': [ sonyClassShutterSpeedCpEnums, sonyClassAlpha7ShutterSpeedOptions ],
    'still_cap_mode': [ sonyClassStillCaptureCpEnums, sonyClassAlpha7StillCaptureOptions ],
    'aperture': [ sonyClassApertureCpEnums, sonyClassAlpha7ApertureOptions ],
    'exposure_prog': [ sonyClassExProCpEnums, sonyClassAlpha7ExProOptions ],
    }

#
# these are dummy classes for other camera models to be added the dict can store details associated with available each mode
# CpEnums : denotes what total features are in a type or which an (API) can perform
# Options : denotes list of maximum options available for camera model
#	
FEATURE_SET_5 = {
    'iso': [ eClassIsoCpEnums, eClassModel1IsoOptions ],
    'white_bal': [ eClassApertureCpEnums, eClassModel1ApertureOptions ],
    'focus_mode': [ eClassApertureCpEnums, eClassModel1ApertureOptions ],
    'focus_area': [ eClassApertureCpEnums, eClassModel1ApertureOptions ],
    'shutter_speed': [ eClassApertureCpEnums, eClassModel1ApertureOptions ],
    'still_cap_mode': [ eClassApertureCpEnums, eClassModel1ApertureOptions ],
    'aperture': [ eClassApertureCpEnums, eClassModel1ApertureOptions ],
    }

FEATURE_SET_2 = {
    'exposure': (4, 6),
    }

FEATURE_SET_3 = {
    'iso': [ fClassApertureCpEnums, fClassApertureOptions ],
    'white_bal': [ fClassApertureCpEnums, fClassApertureOptions ],
    'focus_mode': [ fClassApertureCpEnums, fClassApertureOptions ],
    'focus_area': [ fClassApertureCpEnums, fClassApertureOptions ],
    'shutter_speed': [ fClassApertureCpEnums, fClassApertureOptions ],
    'still_cap_mode': [ fClassApertureCpEnums, fClassApertureOptions ],
    'aperture': [ fClassApertureCpEnums, fClassApertureOptions ],
    }

FEATURE_SET_4 = {
    'iso': [ eClassIsoCpEnums, eClassModel2IsoOptions ],
    'white_bal': [ eClassApertureCpEnums, eClassModel2ApertureOptions ],
    'focus_mode': [ eClassApertureCpEnums, eClassModel2ApertureOptions ],
    'focus_area': [ eClassApertureCpEnums, eClassModel2ApertureOptions ],
    'shutter_speed': [ eClassApertureCpEnums, eClassModel2ApertureOptions ],
    'still_cap_mode': [ eClassApertureCpEnums, eClassModel2ApertureOptions ],
    'aperture': [ eClassApertureCpEnums, eClassModel2ApertureOptions ],
    }
    
# links the feature sets to the model this is what the camera can do and how it understands this data
#
CAMERA_FEATURE_DATA = {
    'Alpha7': FEATURE_SET_5,
    'RedEye': FEATURE_SET_2,
    'Alpha6': FEATURE_SET_5,
    'Alpha5': FEATURE_SET_3,
    'Alpha9': FEATURE_SET_4,
    'SonyAlfa7': FEATURE_SET_1,
    'SonyAlfa7LHS': FEATURE_SET_1,
    'SonyAlfa7RHS': FEATURE_SET_1,
    }

# lists the model names with a type id (which used to branch in the main code)
#
CAMERA_MODELS_DATA = {
    'SonyAlfa7': 1,
    'RedEye': 2,
    'Alpha6': 3,
    'Alpha5': 4,
    'Alpha9': 5,
    'Alpha7': 6,
    'SonyAlfa7LHS': 7,
    'SonyAlfa7RHS': 8,
    }

import re

class sonyAlphaNewCamera():
    # number from name
    #    
    def match_name_enum( self, nameS,eClass ):
        #pattern = re.compile(nameS)
        for s in sorted(eClass):
            if not s.name.find(nameS) == -1:
            #if (re.search(pattern, s.name.upper())==True):
                #print(f" value {s.value} {s.value}")
                return s.value
        return None

    # name from number
    #    
    def match_num_enum( self, nameV,eClass ):
        for s in sorted(eClass):
            if (s.value == nameV):
                #print(f" name {s.name} {s.value}")
                return s.name
        return None

    # option from enum
    #
    def classGetOptionFromCpEnum( self, cpEnumNum, camClassE, camClassO ):
        name=self.match_num_enum( cpEnumNum,camClassE )
        if name is not None:
            return(self.match_name_enum( name, camClassO ))
        
    # enum from option
    #
    def classGetCpEnumFromOption( self, oPtion,camClassE, camClassO ):
        name=self.match_num_enum( oPtion,camClassE )
        if name is not None:
            return(self.match_name_enum( name, camClassO ))
	
    # returns relevant data set and id number for a given camera name
    #
    #	
    def getDataForModel(self, my_model):

        # python2 : for model_name, model_id in CAMERA_MODELS_DATA.iteritems():
        #pattern = re.compile(my_model)
        for model_name, model_id in CAMERA_MODELS_DATA.items():
            if not model_name == None:
                if not model_name.find(my_model) == -1:
                #if (re.search(pattern, model_name.upper())==True):
                    my_data_set = CAMERA_FEATURE_DATA[model_name]
                    return my_data_set,model_id
        return None

    # returns the camera name selected from the GUI
    #
    #	
    def getModelForId(self, id):

        for model_name, model_id in CAMERA_MODELS_DATA.items():
            if not model_name == None:
                if (model_id == id):
                    my_data_set = CAMERA_FEATURE_DATA[model_name]
                    return my_data_set,model_name
        return None
        
    # gets option  
    #
    def getOptionFromEnum( self, enum, data_set, option ):

        list_of_enums = data_set[option]
        if len(list_of_enums) == 2:
            return( self.classGetOptionFromCpEnum( enum, list_of_enums[0], list_of_enums[1] ) )
        return None	

    # gets enum  
    #
    def getEnumFromOption( self, opt, data_set, option ):

        list_of_enums = data_set[option]
        if len(list_of_enums) == 2:
            return( self.classGetCpEnumFromOption( opt, list_of_enums[1], list_of_enums[0] ))
        return None

if __name__ == '__main__':	

    droneCam = sonyAlphaNewCamera()
    cam1_data, cam1_id = droneCam.getDataForModel('Alpha7')
    print(f" a7:: aperture option for 5080 is {droneCam.getOptionFromEnum( 5080, cam1_data, 'aperture' )}")
    print(f" a7:: aperture enum for 3 is {droneCam.getEnumFromOption( 3, cam1_data, 'aperture' )}")
    print(f" a7:: aperture option for 4680 is {droneCam.getOptionFromEnum( 4680, cam1_data, 'aperture' )}")
    print(f" a7:: aperture enum for 2 is {droneCam.getEnumFromOption( 2, cam1_data, 'aperture' )}")
    print(f" a7:: aperture option for 999 is {droneCam.getOptionFromEnum( 999, cam1_data, 'aperture' )}")

    print(f" a7:: iso enum for 2 is {droneCam.getEnumFromOption( 2, cam1_data, 'iso' )}")
    print(f" a7:: iso option for 600 is {droneCam.getOptionFromEnum( 600, cam1_data, 'iso' )}")
    
    cam1_data, cam1_id = droneCam.getDataForModel('Alpha9')
    print(f" a9:: aperture option for 999 is {droneCam.getOptionFromEnum( 999, cam1_data, 'aperture' )}")
    
    print(f" a9:: iso enum for 2 is {droneCam.getEnumFromOption( 2, cam1_data, 'iso' )}")
    print(f" a9:: iso option for 600 is {droneCam.getOptionFromEnum( 600, cam1_data, 'iso' )}")

    # ------------------------------- test every mode for alpha 7 sony camera ----------------------------------------
    #    
    cam1_data, cam1_id = droneCam.getDataForModel('SonyAlfa7')   
    print(f" sonyAlfa7:: whitebalance enum for 2 is {droneCam.getEnumFromOption( 2, cam1_data, 'white_bal' )}")
    print(f" sonyAlfa7:: whitebalance option for 256 is {droneCam.getOptionFromEnum( 256, cam1_data, 'white_bal' )}")
    
    print(f" sonyAlfa7:: iso enum for 2 is {droneCam.getEnumFromOption( 2, cam1_data, 'iso' )}")
    print(f" sonyAlfa7:: iso option for 800 is {droneCam.getOptionFromEnum( 800, cam1_data, 'iso' )}")
    
    print(f" sonyAlfa7:: focus mode enum for 2 is {droneCam.getEnumFromOption( 2, cam1_data, 'focus_mode' )}")
    print(f" sonyAlfa7:: focus mode option for 5 is {droneCam.getOptionFromEnum( 5, cam1_data, 'focus_mode' )}")
    
    print(f" sonyAlfa7:: focus_area enum for 2 is {droneCam.getEnumFromOption( 2, cam1_data, 'focus_area' )}")
    print(f" sonyAlfa7:: focus_area option for 6 is {droneCam.getOptionFromEnum( 6, cam1_data, 'focus_area' )}")
    
    print(f" sonyAlfa7:: shutter_speed enum for 2 is {droneCam.getEnumFromOption( 2, cam1_data, 'shutter_speed' )}")
    print(f" sonyAlfa7:: shutter_speed option for 66786 is {droneCam.getOptionFromEnum( 66786, cam1_data, 'shutter_speed' )}")
    
    print(f" sonyAlfa7:: still_cap_mode enum for 2 is {droneCam.getEnumFromOption( 2, cam1_data, 'still_cap_mode' )}")
    print(f" sonyAlfa7:: still_cap_mode option for 262921 is {droneCam.getOptionFromEnum( 262921, cam1_data, 'still_cap_mode' )}")
    
    print(f" sonyAlfa7:: aperture enum for 2 is {droneCam.getEnumFromOption( 2, cam1_data, 'aperture' )}")
    print(f" sonyAlfa7:: aperture option for 1300 is {droneCam.getOptionFromEnum( 1300, cam1_data, 'aperture' )}")
    
    
    
