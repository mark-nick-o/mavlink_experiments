#include "send_cmd_req_handler.hpp"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "gcs_model.h"
#include "mavlink_communicator.h"
#include "camera_data.h"

using namespace domain;

SendCmdReqHandler::SendCmdReqHandler(MavLinkCommunicator* communicator,
                                         GcsModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40); // 25 Hz
}

void SendCmdReqHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

/*
   request a one-shot message cmd is the message you are wanting sent back e.g. cmd=STORAGE_INFORMATION or CAMERA_INFORMATION
*/
void SendCmdReqHandler::sendRequestCmdMAVLinkMessage( std::int8_t cmd, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_REQUEST_MESSAGE;
  com.confirmation     = conf;
  com.param1           = cmd;
  com.param2           = 0;
  com.param7           = target_comp;
  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, target_comp, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   request a one-shot message to recover images from the camera
*/
void SendCmdReqHandler::sendRequestCmdLostImagesMAVLinkMessage( std::uint8_t missing_img_idx, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_REQUEST_MESSAGE;
  com.confirmation     = conf;
  com.param1           = MAVLINK_MSG_ID_CAMERA_IMAGE_CAPTURED;
  com.param2           = missing_img_idx;
  com.param7           = target_comp;
  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, target_comp, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   set camera mode
*/
void SendCmdReqHandler::SetCamModeMAVLinkMessage( std:uint8_t cam_mode, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           

  // Disabled as Sony cam has more modes than 3!!!      if (cam_mode >= 3) std::cout << "invalid mode set options 0-2" << std::endl;
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_SET_CAMERA_MODE;
  com.confirmation     = conf;
  com.param1           = 0;
  com.param2           = cam_mode;                                    

  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, target_comp, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   control video stream
*/
void SendCmdReqHandler::SendVideoCaptureMAVLinkMessage( std::uint8_t stream, std::uint8_t start, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           

  com.target_system    = target_sys;
  com.target_component = target_comp;
  if ( start != 0 )
  {
      com.command      = MAV_CMD_VIDEO_STOP_CAPTURE;
  }
  else
  {
      com.command      = MAV_CMD_VIDEO_START_CAPTURE;	  
  }
  com.confirmation     = conf;
  com.param1           = stream;                                  

  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, target_comp, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   control image taking
*/
void SendCmdReqHandler::SendImageActionMAVLinkMessage( std::uint8_t start, std::uint8_t interVal, std::uint8_t image, std::uint8_t sequence, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
  // uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN];

  com.target_system    = target_sys;
  com.target_component = target_comp;
  if ( start != 0 )
  {	  
     com.command       = MAV_CMD_IMAGE_STOP_CAPTURE;
  }
  else
  {
     com.command       = MAV_CMD_IMAGE_START_CAPTURE;	  
  }
  com.confirmation     = conf;
  com.param1           = 0;
  com.param2           = interVal;                                    
  com.param3           = image; 
  com.param4           = sequence; 
	
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, target_comp, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   control stream
*/
void SendCmdReqHandler::SendStreamActionMAVLinkMessage( std::uint8_t stream, std::uint8_t start, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
  // uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN];

  com.target_system    = target_sys;
  com.target_component = target_comp;
  if ( start != 0 )
  {	  
     com.command       = MAV_CMD_VIDEO_STOP_STREAMING;
  }
  else
  {
     com.command       = MAV_CMD_VIDEO_START_STREAMING;	  
  }
  com.confirmation     = conf;
  com.param1           = stream;                                   

  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   set camera mode
*/
void SendCmdReqHandler::SetCamModeMAVLinkMessage( std:uint8_t cam_mode, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           

  // Disabled as Sony cam has more modes than 3!!!      if (cam_mode >= 3) std::cout << "invalid mode set options 0-2" << std::endl;
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_SET_CAMERA_MODE;
  com.confirmation     = conf;
  com.param1           = 0;
  com.param2           = cam_mode;                                    

  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   set camera zoom
*/
void SendCmdReqHandler::SetCamZoomMAVLinkMessage( std:uint8_t zoom_type, std::uint8_t zoom_value, std::uint8_t zoom_scale, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_SET_CAMERA_ZOOM;
  com.confirmation     = conf;
  com.param1           = zoom_type;
  com.param2           = zoom_value;                                    
  com.param3           = zoom_scale;  
  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   set camera focus
*/
void SendCmdReqHandler::SetCamFocusMAVLinkMessage( std:uint32_t focus_type, std::uint32_t focus_value, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_SET_CAMERA_FOCUS;
  com.confirmation     = conf;
  com.param1           = focus_type;
  com.param2           = focus_value;                                    

  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   do digicam config
*/
void SendCmdReqHandler::doDigiCamConfigMAVLinkMessage( const cam_config_t camConf, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_DO_DIGICAM_CONFIGURE;
  com.confirmation     = conf;
  com.param1           = camConf.mode;
  com.param2           = camConf.shutterSpeed;   
  com.param3           = camConf.aperture;
  com.param4           = camConf.iso;   
  com.param5           = camConf.exposure;
  com.param6           = camConf.identity;     
  com.param7           = camConf.engCutOff;
  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   do digicam control
*/
void SendCmdReqHandler::doDigiCamControlMAVLinkMessage( const cam_control_t camCont, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_DO_DIGICAM_CONTROL;
  com.confirmation     = conf;
  com.param1           = camCont.SessionControl;
  com.param2           = camCont.ZoomAbsolute;	
  com.param3           = camCont.ZoomRelative;
  com.param4           = camCont.Focus;
  com.param5           = camCont.Shoot;
  com.param6           = camCont.CommandId;
  com.param7           = camCont.ShotID;
  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   do control video
*/
void SendCmdReqHandler::doControlVideoMAVLinkMessage( vid_control_t vidCont, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_DO_CONTROL_VIDEO;
  com.confirmation     = conf;
  com.param1           = vidCont.ID;
  com.param2           = vidCont.Transmission;	
  com.param3           = vidCont.Interval;
  com.param4           = vidCont.Recording;
  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   format storage media
*/
void SendCmdReqHandler::formatMediaMAVLinkMessage( std::int8_t id, std::int8_t reset, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_STORAGE_FORMAT;
  com.confirmation     = conf;
  com.param1           = id;
  if (reset == 0)
  {
    com.param2           = 1;
    com.param3           = 0;
  }
  else
  {
    com.param2           = 0;
    com.param3           = reset;	  
  }	  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   set the camera trigger interval
*/
void SendCmdReqHandler::setCamTriggIntervalMAVLinkMessage( std::int8_t trig, std::int8_t si, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_DO_SET_CAM_TRIGG_INTERVAL;
  com.confirmation     = conf;
  com.param1           = trig;
  com.param2           = si;
  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   reset all settings
*/
void SendCmdReqHandler::resetCameraMAVLinkMessage( std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_RESET_CAMERA_SETTINGS;
  com.confirmation     = conf;
  com.param1           = 1;
  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   move gimbal to quaternion
*/
void SendCmdReqHandler::setRotation2QuatMAVLinkMessage( vector <std::int16_t> quat, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_DO_MOUNT_CONTROL_QUAT;
  com.confirmation     = conf;
  com.param1           = quat[0];
  com.param2           = quat[1];
  com.param3           = quat[2];
  com.param4           = quat[3];
  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   reset gimbal or camera mount rotation
*/
void SendCmdReqHandler::resetCamRotationMAVLinkMessage( std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_DO_MOUNT_CONTROL_QUAT;
  com.confirmation     = conf;
  com.param1           = 1;
  com.param2           = 0;
  com.param3           = 0;
  com.param4           = 0;
  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   move gimbal to quaternion mew command may not be ready
*/
void SendCmdReqHandler::moveGimbal2QuatMAVLinkMessage( vector <std::int16_t> vec, std::uint8_t flags, std::uint8_t id, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW;
  com.confirmation     = conf;
  com.param1           = vec[0];
  com.param2           = vec[1];
  com.param3           = vec[2];
  com.param4           = vec[3];
  com.param5           = flags;
  com.param6           = id;
  
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   set a relay on the Pi4
*/
void SendCmdReqHandler::SendRelayActionMAVLinkMessage( std:uint8_t r_num, std::uint8_t Action, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t conf, std::uint8_t componentId)
{
  std::uint16_t len=0u;

  mavlink_command_long_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           

  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_DO_SET_RELAY;
  com.confirmation     = conf;
  com.param1           = r_num;
  com.param2           = Action;                                    

  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
    This is the message the Camera Board shall send back to the GCS on receipt of the above message
*/
void SendCmdReqHandler::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)
    if (m_substate == DO_CMD_SEND_CAM_INFO)                                   /* --- 259 --- */
    {
        SendCmdReqHandler::sendRequestCmdMAVLinkMessage( CAMERA_INFORMATION, m_communicator->systemId(), m_communicator->componentId(), 0);
        m_substate == DO_CMD_SENT_CAM_INFO;
    }
    else if (m_substate == DO_CMD_SEND_CAM_SET)                               /* --- 260 --- */ 
    {
        SendCmdReqHandler::sendRequestCmdMAVLinkMessage( CAMERA_SETTINGS, m_communicator->systemId(), m_communicator->componentId(), 0);
        m_substate == DO_CMD_SENT_CAM_SET;
    }
    else if (m_substate == DO_CMD_SEND_STO_INFO)                              /* --- 261 --- */
    {
        SendCmdReqHandler::sendRequestCmdMAVLinkMessage( STORAGE_INFORMATION, m_communicator->systemId(), m_communicator->componentId(), 0);
        m_substate == DO_CMD_SENT_STO_INFO;
    }
    else if (m_substate == DO_CMD_SEND_CAP_STA)                                /* --- 262 --- */
    {
        SendCmdReqHandler::sendRequestCmdMAVLinkMessage( CAMERA_CAPTURE_STATUS, m_communicator->systemId(), m_communicator->componentId(), 0);
        m_substate == DO_CMD_SENT_CAP_STA;
    }
    else if (m_substate == DO_CMD_SEND_VIDEO_STREAM_REQ)                       /* --- 269 --- */
    {
        SendCmdReqHandler::sendRequestCmdMAVLinkMessage( 269, m_communicator->systemId(), m_communicator->componentId(), 0);
        m_substate == DO_CMD_SENT_VIDEO_STREAM_REQ;
    }
    else if (m_substate == DO_CAM_SEND_MODE_CHANGE)                       /* ---  --- */
    {
        SendCmdReqHandler::SetCamModeMAVLinkMessage( 3, m_communicator->systemId(), m_communicator->componentId(), 0);
        m_substate == DO_CAM_SENT_MODE_CHANGE;
    }
    else if (m_substate == DO_CAM_SEND_VC_START)                       /* ---  --- */
    {
        SendCmdReqHandler::SendVideoCaptureMAVLinkMessage( 1, 1, m_communicator->systemId(), m_communicator->componentId(), 0);
        m_substate == DO_CAM_SENT_VC_START;
    }
    else if (m_substate == DO_CAM_SEND_VC_STOP)                       /* ---  --- */
    {
        SendCmdReqHandler::SendVideoCaptureMAVLinkMessage( 1, 0, m_communicator->systemId(), m_communicator->componentId(), 0);
        m_substate == DO_CAM_SENT_VC_STOP;
    }
    else if (m_substate == DO_CAM_SEND_IM_START)                       /* ---  --- */
    {
        SendCmdReqHandler::SendImageActionMAVLinkMessage( 1, 3, 1, 1, m_communicator->systemId(), m_communicator->componentId(), 0);
        m_substate == DO_CAM_SENT_IM_START;
    }
    else if (m_substate == DO_CAM_SEND_IM_STOP)                       /* ---  --- */
    {
        SendCmdReqHandler::SendImageActionMAVLinkMessage( 0, 3, 1, 1, m_communicator->systemId(), m_communicator->componentId(), 0);
        m_substate == DO_CAM_SENT_IM_STOP;
    }
    else if (m_substate == DO_CAM_SEND_VIDEOST_START)                       /* ---  --- */
    {
	SendCmdReqHandler::SendStreamActionMAVLinkMessage( 1, 1, m_communicator->systemId(), m_communicator->componentId(), 0, m_communicator->componentId());
        m_substate == DO_CAM_SENT_VIDEOST_START;
    }
    else if (m_substate == DO_CAM_SEND_VIDEOST_STOP)                       /* ---  --- */
    {
	SendCmdReqHandler::SendStreamActionMAVLinkMessage( 1, 0, m_communicator->systemId(), m_communicator->componentId(), 0, m_communicator->componentId());
        m_substate == DO_CAM_SENT_VIDEOST_STOP;
    }
    else if (m_substate == DO_CAM_SEND_MODE)                       /* ---  --- */
    {
	SendCmdReqHandler::SetCamModeMAVLinkMessage( 2, m_communicator->systemId(), m_communicator->componentId(), 0, m_communicator->componentId());
        m_substate == DO_CAM_SENT_MODE;
    }
    else if (m_substate == DO_CAM_SEND_ZOOM)                       /* ---  --- */
    {
	SendCmdReqHandler::SetCamZoomMAVLinkMessage( 2, 36, 2, m_communicator->systemId(), m_communicator->componentId(), 0, m_communicator->componentId());
        m_substate == DO_CAM_SENT_ZOOM;
    }
    else if (m_substate == DO_CAM_SEND_FOCUS)                       /* ---  --- */
    {
	SendCmdReqHandler::SetCamFocusMAVLinkMessage( 1, 1111, m_communicator->systemId(), m_communicator->componentId(), std::uint8_t conf, m_communicator->componentId());
        m_substate == DO_CAM_SENT_FOCUS;
    }
    else if (m_substate == DO_CAM_SEND_CONFIG)                       /* ---  --- */
    {
	cam_config_t camConfigSettings;
        camConfigSettings.mode;
        camConfigSettings.shutterSpeed = 1;   
        camConfigSettings.aperture = 2;
        camConfigSettings.iso = 3;   
        camConfigSettings.exposure = 4;
        camConfigSettings.identity = 5;     
        camConfigSettings.engCutOff = 6;
	SendCmdReqHandler::doDigiCamConfigMAVLinkMessage( camConfigSettings, m_communicator->systemId(), m_communicator->componentId(), 0, m_communicator->componentId());
        m_substate == DO_CAM_SENT_CONFIG;
    }
    else if (m_substate == DO_CAM_SEND_CONTROL)                       /* ---  --- */
    {
	cam_control_t camControlObject;
        camControlObject.SessionControl = 9;
        camControlObject.ZoomAbsolute = 8;	
        camControlObject.ZoomRelative = 7;
        camControlObject.Focus = 6;
        camControlObject.Shoot = 5;
        camControlObject.CommandId = 4;
        camControlObject.ShotID = 3;
	SendCmdReqHandler::doDigiCamControlMAVLinkMessage( camControlObject, m_communicator->systemId(), m_communicator->componentId(), 0, m_communicator->componentId());
        m_substate == DO_CAM_SENT_CONTROL;
    }
    else if (m_substate == DO_VID_SEND_CONTROL) 
    {
	vid_control_t vidControlObject;
        vidControlObject.ID = 3;
        vidControlObject.Transmission = 4;	
        vidControlObject.Interval = 50;
        vidControlObject.Recording = 3;
        SendCmdReqHandler::doControlVideoMAVLinkMessage( vidControlObject, m_communicator->systemId(), m_communicator->componentId(), 0, m_communicator->componentId());
        m_substate == DO_VID_SENT_CONTROL;
    }	
    else if (m_substate == DO_MEDIA_SEND_FORMAT)                       /* ---  --- */
    {
	SendCmdReqHandler::formatMediaMAVLinkMessage( 0, 0, m_communicator->systemId(), m_communicator->componentId(), 0, m_communicator->componentId());
        m_substate == DO_MEDIA_SENT_FORMAT;
    }
    else if (m_substate == DO_CAM_SEND_TRIGI)                       /* ---  --- */
    {
        SendCmdReqHandler::setCamTriggIntervalMAVLinkMessage( 10, 20, m_communicator->systemId(), m_communicator->componentId(), 0,  m_communicator->componentId());
	m_substate == DO_CAM_SENT_TRIGI;
    }
    else if (m_substate == DO_CAM_SEND_RESET)                       /* ---  --- */
    {
	SendCmdReqHandler::resetCameraMAVLinkMessage( m_communicator->systemId(), m_communicator->componentId(), 0,  m_communicator->componentId());
	m_substate == DO_CAM_SENT_RESET;
    }
    else if (m_substate == DO_GIM_SEND_ROTAT)                       /* ---  --- */
    {
	vector <std::int16_t> quaternionSet;
	quaternionSet[0] = 30;
	quaternionSet[1] = 75;
	quaternionSet[2] = 56;
	quaternionSet[3] = 110;
	SendCmdReqHandler::setRotation2QuatMAVLinkMessage( quaternionSet, m_communicator->systemId(), m_communicator->componentId(), 0,  m_communicator->componentId());
	m_substate == DO_GIM_SENT_ROTAT;
    }
    else if (m_substate == DO_GIM_SEND_RESET)                       /* ---  --- */
    {
        SendCmdReqHandler::resetCamRotationMAVLinkMessage( m_communicator->systemId(), m_communicator->componentId(), 0,  m_communicator->componentId());
	m_substate == DO_GIM_SENT_RESET;
    }
    else if (m_substate == DO_GIM_SEND_QUAT)                       /* ---  --- */
    {
	vector <std::int16_t> quaternionSet;
	quaternionSet[0] = 30;
	quaternionSet[1] = 75;
	quaternionSet[2] = 56;
	quaternionSet[3] = 110;
        SendCmdReqHandler::moveGimbal2QuatMAVLinkMessage( quaternionSet, 3, 0, m_communicator->systemId(), m_communicator->componentId(), 0,  m_communicator->componentId());
	m_substate == DO_GIM_SENT_QUAT;
    }
    else if (m_substate == DO_PI_SEND_RELAY1_ON)                       /* ---  --- */
    {
	std:uint8_t relayNo = 1;
	std::uint8_t relayAction = 1;    
	SendCmdReqHandler::SendRelayActionMAVLinkMessage( relayNo, relayAction, m_communicator->systemId(), m_communicator->componentId(), 0,  m_communicator->componentId());
	m_substate == DO_PI_SENT_RELAY1_ON;
    }	
    else if (m_substate == DO_PI_SEND_RELAY1_OFF)                       /* ---  --- */
    {
	std:uint8_t relayNo = 1;
	std::uint8_t relayAction = 0;    
	SendCmdReqHandler::SendRelayActionMAVLinkMessage( relayNo, relayAction, m_communicator->systemId(), m_communicator->componentId(), 0,  m_communicator->componentId());
	m_substate == DO_PI_SENT_RELAY1_OFF;
    }
    else if (m_substate == DO_PI_SEND_RELAY2_ON)                       /* ---  --- */
    {
	std:uint8_t relayNo = 2;
	std::uint8_t relayAction = 1;    
	SendCmdReqHandler::SendRelayActionMAVLinkMessage( relayNo, relayAction, m_communicator->systemId(), m_communicator->componentId(), 0,  m_communicator->componentId());
	m_substate == DO_PI_SENT_RELAY2_ON;
    }	
    else if (m_substate == DO_PI_SEND_RELAY2_OFF)                       /* ---  --- */
    {
	std:uint8_t relayNo = 2;
	std::uint8_t relayAction = 0;    
	SendCmdReqHandler::SendRelayActionMAVLinkMessage( relayNo, relayAction, m_communicator->systemId(), m_communicator->componentId(), 0,  m_communicator->componentId());
	m_substate == DO_PI_SENT_RELAY2_OFF;
    }
    else if (m_substate == DO_CAM_SEND_IMAGE_MISS)                       /* ---  --- */
    {
        std::uint8_t missing_image_index = 4;
        SendCmdReqHandler::sendRequestCmdLostImagesMAVLinkMessage( missing_image_index,  m_communicator->systemId(), m_communicator->componentId(),  0);
	m_substate == DO_CAM_SENT_IMAGE_MISS;
    }
}
