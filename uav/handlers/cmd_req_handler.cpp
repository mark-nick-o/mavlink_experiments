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
           m_substate = DO_SEND_ACK;	
    }
    else if ((cmdReq.command == MAV_CMD_VIDEO_START_CAPTURE) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " start video capture on channel " << cmdReq.param1  << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_IMAGE_STOP_CAPTURE) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " stop image capture on image " << cmdReq.param3 << " sequence : " << cmdReq..param4 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_VIDEO_STOP_STREAMING) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " stop video stream on stream No. " << cmdReq.param1 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_VIDEO_START_STREAMING) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " start video stream on stream No. " << cmdReq.param1 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_SET_CAMERA_MODE) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " set camera mode to. " << cmdReq.param2 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_SET_CAMERA_ZOOM) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " type : " << cmdReq.param1 << " value : " << cmdReq.param2 << " scale : " << cmdReq.param3 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_SET_CAMERA_FOCUS) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " type : " << cmdReq.param1 << " value : " << cmdReq.param2 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_DIGICAM_CONFIGURE) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " mode : " << cmdReq.param1 << " shutter speed : " << cmdReq.param2 << " aperture : " << cmdReq.param3 << std::endl;
	   qDebug() << " iso : " << cmdReq.param4 << " exposure : " << cmdReq.param5 << " identity : " << cmdReq.param6 << std::endl;
	   qDebug() << " engine cut off : " << cmdReq.param7 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_DIGICAM_CONTROL) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " SessionControl : " << cmdReq.param1 << " ZoomAbsolute : " << cmdReq.param2 << " ZoomRelative : " << cmdReq.param3 << std::endl;
	   qDebug() << " Focus : " << cmdReq.param4 << " Shoot : " << cmdReq.param5 << " CommandId : " << cmdReq.param6 << std::endl;
	   qDebug() << " ShotID : " << cmdReq.param7 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_CONTROL_VIDEO) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " ID : " << cmdReq.param1 << " Transmission : " << cmdReq.param2 << " Interval : " << cmdReq.param3 << std::endl;
	   qDebug() << " Recording : " << cmdReq.param4 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_SET_CAM_TRIGG_INTERVAL) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " Trigger Cycle : " << cmdReq.param1 << " Shutter Integration : " << cmdReq.param2 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_RESET_CAMERA_SETTINGS) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " State Param : " << cmdReq.param1 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_MOUNT_CONTROL_QUAT) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " quaternion : [ " << cmdReq.param1 << " , " << cmdReq.param2 << " , " << cmdReq.param3 << " , " << cmdReq.param4 <<  " ] "  << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " quaternion : [ " << cmdReq.param1 << " , " << cmdReq.param2 << " , " << cmdReq.param3 << " , " << cmdReq.param4 <<  " ] "  << std::endl;
	   qDebug() << " Flags : " << cmdReq.param5 << " Id : " << cmdReq.param6 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
    else if ((cmdReq.command == MAV_CMD_STORAGE_FORMAT) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   qDebug() << " ID : " << cmdReq.param1 << " Format " << cmdReq.param2 << "  Reset Image Log " << cmdReq.param3 << std::endl;
	   m_substate = DO_SEND_ACK;
    }
	
}
