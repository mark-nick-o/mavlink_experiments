#include "cmd_req_handler.hpp"
#inlcude "camera_status_data.h"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

using namespace domain;

CmdReqHandler::CmdReqHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    //this->startTimer(40); // 25 Hz
    //if (m_ccs_update_trigger != 0)
    //{
    //   this->startTimer(static_cast<std::uint16_t>(m_ccs_update_trigger*1.6f));                              // m_ccs_update_trigger Hz
    //}
    this->startTimer(40);                            // @ 25 Hz	    
}

void CmdReqHandler::processMessage(const mavlink_message_t& message)
{
    if (message.msgid != MAV_CMD_LONG_MESSAGE || message.sysid == 0) return;

    mavlink_command_long_t cmdReq;
    mavlink_msg_command_long_decode(&message, &cmdReq);
    
    if ((cmdReq.command == MAV_CMD_REQUEST_MESSAGE) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
        switch (cmdReq.param1)
        {
	   case CAMERA_INFORMATION:
           /* send information regarding the camera  */
	   if ((m_substate == GO_IDLE) && (m_sendState == GO_IDLE))
	   {
	       m_substate = DO_SEND_ACK;
	       m_sendState = SENS_CI;
	   }
	   else if (m_substate > SENT_CI)
	   {
		m_reject |= CI_BIT;
	   }
           break;

	   case CAMERA_SETTINGS:
	   if ((m_substate == GO_IDLE) && (m_sendState == GO_IDLE))
	   {
	       m_substate = DO_SEND_ACK;
	       m_sendState = SENS_CS;
	   }
	   else if (((m_substate < SENS_CS) && (m_substate != GO_IDLE)) || (m_substate > SENT_CS)) 
	   {
		m_reject |= CS_BIT;		   
	   }
           break;
		    
           case STORAGE_INFORMATION:
           /* send information regarding the storage media */
	   if ((m_substate == GO_IDLE) && (m_sendState == GO_IDLE))
	   {
	       m_substate = DO_SEND_ACK;
	       m_sendState = SENS_SI;
	   }
	   else if (((m_substate < SENS_SI) && (m_substate != GO_IDLE)) || (m_substate > SENT_SI)) 
	   {
		m_reject |= SI_BIT;		   
	   }
           break;

           case CAMERA_CAPTURE_STATUS:
           /* send information regarding the capture status */
	   if ((m_substate == GO_IDLE) && (m_sendState == GO_IDLE))
	   {
	      m_substate = DO_SEND_ACK;
	      m_sendState = SENS_CCS;
	   }
	   else if (((m_substate < SENS_CCS) && (m_substate != GO_IDLE)) || (m_substate > SENT_CCS))
	   {
		m_reject |= CCS_BIT;		   
	   }			
           break;

           case 269:
           /* send information regarding the video streaming status */
	   if ((m_substate == GO_IDLE) && (m_sendState == GO_IDLE))
	   {			
	      m_substate = DO_SEND_ACK;
	      m_sendState = SENS_VS;
	   }
	   else if (((m_substate < SENS_VS) && (m_substate != GO_IDLE)) || (m_substate > SENT_VS))
	   {
		m_reject |= VS_BIT;		   
	   }		
           break;

           case MAVLINK_MSG_ID_CAMERA_IMAGE_CAPTURED:
           /* send information regarding the missing images */
	   if ((m_substate == GO_IDLE) && (m_sendState == GO_IDLE))
	   {			
	      m_substate = DO_SEND_ACK;
	      m_sendState = SENS_CIC;
	      m_missing_image_index = cmdReq.param2;
	   }
	   else if (((m_substate < SENS_CIC) && (m_substate != GO_IDLE)) || (m_substate > SENT_CIC))
	   {
		m_reject |= CIC_BIT;		   
	   }			
	   break;
			
           default:
	   m_reject |= US_BIT;
           break;
       }
    }
    else if ((cmdReq.command == MAV_CMD_DO_SET_RELAY) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " now set the relay number " << cmdReq.param1 << " to state : " << cmdReq..param2 << std::endl;
           m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_VIDEO_STOP_CAPTURE) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " stop video capture on channel " << cmdReq.param1  << std::endl;
	   m_ccs_update_trigger = 0;
           m_substate = DO_SEND_ACK;	
    }
    else if ((cmdReq.command == MAV_CMD_VIDEO_START_CAPTURE) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " start video capture on channel " << cmdReq.param1  << std::endl;
	   qDebug() << " send update CAMERA_CAPTURE_MESSAGE @ timer Hz " << cmdReq.param2  << std::endl;
	   m_ccs_update_trigger = cmdReq.param2;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_IMAGE_START_CAPTURE) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " interval : " << cmdReq.param2 << " start image capture on image " << cmdReq.param3 << " sequence : " << cmdReq..param4 << std::endl;
	   if ((m_substate == GO_IDLE) && (m_sendState == GO_IDLE))
	   {			
	      m_substate = DO_SEND_ACK;
	      m_sendState = SENS_CIC;
	      m_cic_interval = cmdReq.param2;
	   }
	   else if (((m_substate < SENS_CIC) && (m_substate != GO_IDLE)) || (m_substate > SENT_CIC))
	   {
		m_reject |= CIC_BIT;		   
	   }
    }
    else if ((cmdReq.command == MAV_CMD_IMAGE_STOP_CAPTURE) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " stop image capture on image " << cmdReq.param3 << " sequence : " << cmdReq..param4 << std::endl;
	   m_substate = DO_SEND_ACK;
	   m_cic_interval = 0;
    }
    else if ((cmdReq.command == MAV_CMD_VIDEO_STOP_STREAMING) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " stop video stream on stream No. " << cmdReq.param1 << std::endl;
	   m_ack_cmd = MAV_CMD_VIDEO_STOP_STREAMING;
	   m_sendState == GO_IDLE;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_VIDEO_START_STREAMING) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " start video stream on stream No. " << cmdReq.param1 << std::endl;
	   m_ack_cmd = MAV_CMD_VIDEO_START_STREAMING;
	   if ((m_substate == GO_IDLE) && (m_sendState == GO_IDLE))
	   {			
	      m_substate = DO_SEND_ACK;
	      m_sendState = SENS_VS;
	   }
	   else if (((m_substate < SENS_VS) && (m_substate != GO_IDLE)) || (m_substate > SENT_VS))
	   {
		m_reject |= VS_BIT;		   
	   }
    }
    else if ((cmdReq.command == MAV_CMD_SET_CAMERA_MODE) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " set camera mode to. " << cmdReq.param2 << std::endl;
	   m_ack_cmd = MAV_CMD_SET_CAMERA_MODE;	    
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_SET_CAMERA_ZOOM) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " type : " << cmdReq.param1 << " value : " << cmdReq.param2 << " scale : " << cmdReq.param3 << std::endl;
	   m_ack_cmd = MAV_CMD_SET_CAMERA_ZOOM;	  	    
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_SET_CAMERA_FOCUS) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " type : " << cmdReq.param1 << " value : " << cmdReq.param2 << std::endl;
	   m_ack_cmd = MAV_CMD_SET_CAMERA_FOCUS;	  	    
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_DIGICAM_CONFIGURE) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " mode : " << cmdReq.param1 << " shutter speed : " << cmdReq.param2 << " aperture : " << cmdReq.param3 << std::endl;
	   qDebug() << " iso : " << cmdReq.param4 << " exposure : " << cmdReq.param5 << " identity : " << cmdReq.param6 << std::endl;
	   qDebug() << " engine cut off : " << cmdReq.param7 << std::endl;
	   m_ack_cmd = MAV_CMD_DO_DIGICAM_CONFIGURE;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_DIGICAM_CONTROL) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " SessionControl : " << cmdReq.param1 << " ZoomAbsolute : " << cmdReq.param2 << " ZoomRelative : " << cmdReq.param3 << std::endl;
	   qDebug() << " Focus : " << cmdReq.param4 << " Shoot : " << cmdReq.param5 << " CommandId : " << cmdReq.param6 << std::endl;
	   qDebug() << " ShotID : " << cmdReq.param7 << std::endl;
	   m_ack_cmd = MAV_CMD_DO_DIGICAM_CONTROL;	    
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_CONTROL_VIDEO) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " ID : " << cmdReq.param1 << " Transmission : " << cmdReq.param2 << " Interval : " << cmdReq.param3 << std::endl;
	   qDebug() << " Recording : " << cmdReq.param4 << std::endl;
	   m_ack_cmd = MAV_CMD_DO_CONTROL_VIDEO;		    
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_SET_CAM_TRIGG_INTERVAL) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " Trigger Cycle : " << cmdReq.param1 << " Shutter Integration : " << cmdReq.param2 << std::endl;
	   m_ack_cmd = MAV_CMD_DO_SET_CAM_TRIGG_INTERVAL;		    
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_RESET_CAMERA_SETTINGS) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " State Param : " << cmdReq.param1 << std::endl;
	   m_ack_cmd = MAV_CMD_RESET_CAMERA_SETTINGS;	    
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_MOUNT_CONTROL_QUAT) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " quaternion : [ " << cmdReq.param1 << " , " << cmdReq.param2 << " , " << cmdReq.param3 << " , " << cmdReq.param4 <<  " ] "  << std::endl;
	   m_ack_cmd = MAV_CMD_DO_MOUNT_CONTROL_QUAT;	
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " quaternion : [ " << cmdReq.param1 << " , " << cmdReq.param2 << " , " << cmdReq.param3 << " , " << cmdReq.param4 <<  " ] "  << std::endl;
	   qDebug() << " Flags : " << cmdReq.param5 << " Id : " << cmdReq.param6 << std::endl;
	   m_ack_cmd = MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW;	
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_TRIGGER_CONTROL) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " enable : [ " << cmdReq.param1 << " reset : " << cmdReq.param2 << " pause : " << cmdReq.param3 << std::endl;
	   m_ack_cmd = MAV_CMD_DO_TRIGGER_CONTROL;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == 2004) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))  // MAV_CMD_CAMERA_TRACK_POINT=2004
    {
	   qDebug() << " x : " << cmdReq.param1 << " y : " << cmdReq.param2 << " radius : " << cmdReq.param3 << std::endl;
	   m_ack_cmd = 2004;	    
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == 2005) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))  // MAV_CMD_CAMERA_TRACK_RECTANGLE=2005
    {
	   qDebug() << " x1 " << cmdReq.param1 << " y1 " << cmdReq.param2 << " x2 " << cmdReq.param3 << " y2 " << cmdReq.param4 << std::endl;
	   m_ack_cmd = 2005;	
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == 2010) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))  // MAV_CMD_CAMERA_STOP_TRACKING=2010
    {
	   qDebug() << " camera tracking stop request recieved " << std::endl;
	   m_ack_cmd = 2010;	    
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_STORAGE_FORMAT) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " ID : " << cmdReq.param1 << " Format " << cmdReq.param2 << "  Reset Image Log " << cmdReq.param3 << std::endl;
	   std::uint8_t stausOfFormat = 0;
	   /*
	       if format is on then format the drive
	       if (cmdReq.param2 == 1) stausOfFormat = formatDrive(cmdReq.param1);
	       if (cmdReq.param3 == 1)  retCmd = resetCamCaptureStausImageCount(cmdReq.param1);
	   */
	   if (stausOfFormat == 0)
	   {
	       m_substate = DO_SEND_ACK;
	   }
	   else
	   {
		if (cmdReq.param1 == 1)
		{
		   m_disk1_count_of_images = 0;
		}
		else if (cmdReq.param1 == 2)
		{
		   m_disk2_count_of_images = 0;
		}
	   }
    }
	
}

void CmdReqHandler::::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)
	    
    /* send information regarding the capture status after we sent a MAV_CMD_VIDEO_START_CAPTURE @ the rate specified by m_ccs_update_trigger */
    if (m_ccs_update_trigger > 0)
    {
        if (((m_substate == GO_IDLE) && (m_sendState == GO_IDLE)) && (m_ccs_time_cycle == 0)) 
        {
	    m_substate = DO_SEND_ACK;
	    m_sendState = SENS_CCS;
	    ++m_ccs_time_cycle;
         }
         m_ccs_time_cycle %= m_ccs_update_trigger;     // modulate cycle counter by the set-point which has been sent in multiples od 25Hz rests at value to zero
    }	
	
    /* send information regarding the capture status after we sent a MAV_CMD_VIDEO_START_CAPTURE @ the rate specified by m_ccs_update_trigger */
    if (m_cic_interval > 0)
    {
        if (((m_substate == GO_IDLE) && (m_sendState == GO_IDLE)) && (m_cic_time_cycle == 0)) 
        {
	    m_substate = DO_SEND_ACK;
	    m_sendState = SENS_CIC;
	    ++m_cic_time_cycle;
         }
         m_ccs_time_cycle %= m_cic_interval;     // modulate cycle counter by the set-point which has been sent in multiples od 25Hz rests at value to zero
    }
	
}

