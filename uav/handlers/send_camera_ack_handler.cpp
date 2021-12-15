#include "send_camera_ack_handler.hpp"
#include "camera_status_data.h"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendCameraAckHandler::SendCameraAckHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40); // 25 Hz
}

void SendCameraAckHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

void SendCameraAckHandler::sendCmdACKMAVLinkMessage( std::uint8_t res, std::uint8_t progrez, std::uint16_t cmd, std::uint8_t target_sys, std::uint8_t target_comp, std::int32_t rpm2 )
{
  std::uint16_t len=0u;

  mavlink_command_ack_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = cmd;
  com.result_param2    = rpm2;
  com.progress         = progrez;
  com.result           = res;
  
  /* encode */
  len = mavlink_msg_command_ack_encode(target_sys, target_comp, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, 0 );
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraInformationReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_INFORMATION );
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraSettingsReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_SETTINGS);
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraStorageInfoReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez  )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, STORAGE_INFORMATION);  
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraImageCapturedReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_IMAGE_CAPTURED);      
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKVideoStreamReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, VIDEO_STREAM_STATUS);      
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKVideoStreamReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, VIDEO_STREAM_STATUS);      
}

// --- Command is valid, but cannot be executed at this time. This is used to indicate a problem that should be fixed just by waiting (e.g. a state machine is busy, can't arm because have not got GPS lock, etc.). Retrying later should work.

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraInformationReqTempRejected( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_TEMPORARILY_REJECTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_INFORMATION );
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraSettingsTempRejected( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_TEMPORARILY_REJECTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_SETTINGS);
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraStorageInfoTempRejected( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez  )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_TEMPORARILY_REJECTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, STORAGE_INFORMATION);  
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraImageCapturedTempRejected( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_TEMPORARILY_REJECTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_IMAGE_CAPTURED);      
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKVideoStreamTempRejected( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_TEMPORARILY_REJECTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, VIDEO_STREAM_STATUS);      
}

/*
   This is next the message the Camera will send to the GCS to reject any communication
*/
void SendCameraAckHandler::cameraACKTotalRejection( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_UNSUPPORTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, 0);      
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraInformationReqAlready( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_IN_PROGRESS, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_INFORMATION);
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraSettingsReqAlready( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_IN_PROGRESS, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_SETTINGS);
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraStorageInfoReqAlready( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_IN_PROGRESS, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, STORAGE_INFORMATION);
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKCameraImageCapturedReqAlready( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_IN_PROGRESS, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_IMAGE_CAPTURED);
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void SendCameraAckHandler::cameraACKVideoStreamReqAlready( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_IN_PROGRESS, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, VIDEO_STREAM_STATUS);
}

/*
   This is next the message the Camera will send to the GCS if the camera action requested fails to work
*/
void SendCameraAckHandler::cameraACKCameraInformationReqFailed( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_FAILED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_INFORMATION);
}

/*
   This is next the message the Camera will send to the GCS if the camera action requested fails to work
*/
void SendCameraAckHandler::cameraACKCameraSettingsReqFailed( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_FAILED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_SETTINGS);
}

/*
   This is next the message the Camera will send to the GCS if the camera action requested fails to work
*/
void SendCameraAckHandler::cameraACKCameraStorageInfoReqFailed( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_FAILED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, STORAGE_INFORMATION);
}

/*
   This is next the message the Camera will send to the GCS if the camera action requested fails to work
*/
void SendCameraAckHandler::cameraACKCameraImageCapturedReqFailed( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_FAILED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_IMAGE_CAPTURED);
}

/*
   This is next the message the Camera will send to the GCS if the camera action requested fails to work
*/
void SendCameraAckHandler::cameraACKVideoStreamReqFailed( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_FAILED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, VIDEO_STREAM_STATUS);
}

/*
    This is the message the Camera Board shall send back to the GCS on receipt of the above message
*/
void SendCameraAckHandler::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)
    if ((m_substate == DO_SENDING_ACK) && ((m_sendState == SENS_CI) || (m_sendState == SEND_CI)))
    {
        SendCameraAckHandler::cameraACKCameraInformationReqAlready( m_communicator->systemId(), m_communicator->componentId(), 50 );
        //m_substate == DO_SENDING_ACK;
    }
    else if ((m_substate == DO_SEND_ACK) && (m_sendState == SENS_CI))
    {
        SendCameraAckHandler::cameraACKCameraInformationReqAccepted( m_communicator->systemId(), m_communicator->componentId(), 0 );
        m_substate == DO_SENDING_ACK;
    }
    else if ((m_substate == DO_SENDING_ACK) && (m_sendState == SENT_CI))
    {
        SendCameraAckHandler::cameraACKCameraInformationReqAccepted( m_communicator->systemId(), m_communicator->componentId(), 100 );
        m_substate == GO_IDLE;
        m_sendState == GO_IDLE;
    }
    if ((m_substate == DO_SENDING_ACK) && ((m_sendState == SENS_CS) || (m_sendState == SEND_CS)))
    {
        SendCameraAckHandler::cameraACKCameraSettingsReqAlready( m_communicator->systemId(), m_communicator->componentId(), 50 );
        //m_substate == DO_SENDING_ACK;
    }
    else if ((m_substate == DO_SEND_ACK) && (m_sendState == SENS_CS))
    {
        SendCameraAckHandler::cameraACKCameraSettingsReqAccepted( m_communicator->systemId(), m_communicator->componentId(), 0 );
        m_substate == DO_SENDING_ACK;
    }
    else if ((m_substate == DO_SENDING_ACK) && (m_sendState == SENT_CS))
    {
        SendCameraAckHandler::cameraACKCameraSettingsReqAccepted( m_communicator->systemId(), m_communicator->componentId(), 100 );
        m_substate == GO_IDLE;
        m_sendState == GO_IDLE;
    }
    if ((m_substate == DO_SENDING_ACK) && ((m_sendState == SENS_SI) || (m_sendState == SEND_SI)))
    {
        SendCameraAckHandler::cameraACKCameraStorageInfoReqAlready( m_communicator->systemId(), m_communicator->componentId(), 50 );
        //m_substate == DO_SENDING_ACK;
    }
    else if ((m_substate == DO_SEND_ACK) && (m_sendState == SENS_SI))
    {
        SendCameraAckHandler::cameraACKCameraStorageInfoReqAccepted( m_communicator->systemId(), m_communicator->componentId(), 0 );
        m_substate == DO_SENDING_ACK;
    }
    else if ((m_substate == DO_SENDING_ACK) && (m_sendState == SENT_SI))
    {
        SendCameraAckHandler::cameraACKCameraStorageInfoReqAccepted( m_communicator->systemId(), m_communicator->componentId(), 100 );
        m_substate == GO_IDLE;
        m_sendState == GO_IDLE;
    }
    if ((m_substate == DO_SENDING_ACK) && ((m_sendState == SENS_CCS) || (m_sendState == SEND_CCS)))
    {
        SendCameraAckHandler::cameraACKCameraImageCapturedReqAlready( m_communicator->systemId(), m_communicator->componentId(), 50 );
        //m_substate == DO_SENDING_ACK;
    }
    else if ((m_substate == DO_SEND_ACK) && (m_sendState == SENS_CCS))
    {
        SendCameraAckHandler::cameraACKCameraImageCapturedReqAccepted( m_communicator->systemId(), m_communicator->componentId(), 0 );
        m_substate == DO_SENDING_ACK;
    }
    else if ((m_substate == DO_SENDING_ACK) && (m_sendState == SENT_CCS))
    {
        SendCameraAckHandler::cameraACKCameraImageCapturedReqAccepted( m_communicator->systemId(), m_communicator->componentId(), 100 );
        m_substate == GO_IDLE;
        m_sendState == GO_IDLE;
    }
    if ((m_substate == DO_SENDING_ACK) && ((m_sendState == SENS_VS) || (m_sendState == SEND_VS)))
    {
        SendCameraAckHandler::cameraACKVideoStreamReqAlready( m_communicator->systemId(), m_communicator->componentId(), 50 );
        //m_substate == DO_SENDING_ACK;
    }
    else if ((m_substate == DO_SEND_ACK) && (m_sendState == SENS_VS))
    {
        SendCameraAckHandler::cameraACKVideoStreamReqAccepted( m_communicator->systemId(), m_communicator->componentId(), 0 );
        m_substate == DO_SENDING_ACK;
    }
    else if ((m_substate == DO_SENDING_ACK) && (m_sendState == SENT_VS))
    {
        SendCameraAckHandler::cameraACKVideoStreamReqAccepted( m_communicator->systemId(), m_communicator->componentId(), 100 );
        m_substate == GO_IDLE;
        m_sendState == GO_IDLE;
    }
    else (m_substate == GO_IDLE)
    {
         SendCameraAckHandler::cameraACKCameraInformationReqAccepted( m_communicator->systemId(), m_communicator->componentId(), 0 );
    }
 
    /* if not listed above general ack sent */
    if (m_substate == DO_SEND_ACK) 
    {
        SendCameraAckHandler::cameraACKReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )( m_communicator->systemId(), m_communicator->componentId(), 0 );
        m_substate == DO_SENDING_ACK;
    }

    /* reject as already busy messages or failed action messages back to GCS */
    if (m_reject & CI_BIT)
    {
	SendCameraAckHandler::cameraACKCameraInformationReqTempRejected( m_communicator->systemId(), m_communicator->componentId(), 0  );
	std::uint16_t mask = CI_BIT;
	m_reject &= ~mask;
    }

    if (m_reject & CS_BIT)
    {
	SendCameraAckHandler::cameraACKCameraSettingsTempRejected( m_communicator->systemId(), m_communicator->componentId(), 0  );  
	std::uint16_t mask = CS_BIT;
	m_reject &= ~mask;
    }
	
    if (m_reject & SI_BIT)
    {
	SendCameraAckHandler::cameraACKCameraStorageInfoTempRejected( m_communicator->systemId(), m_communicator->componentId(), 0  );  
	std::uint16_t mask = SI_BIT;
	m_reject &= ~mask;
    }
	
    if (m_reject & CCS_BIT)
    {
	SendCameraAckHandler::cameraACKCameraImageCapturedTempRejected( m_communicator->systemId(), m_communicator->componentId(), 0  );  
	std::uint16_t mask = CCS_BIT;
	m_reject &= ~mask;
    }
	
    if (m_reject & VS_BIT)
    {
	SendCameraAckHandler::cameraACKVideoStreamTempRejected( m_communicator->systemId(), m_communicator->componentId(), 0  );  
	std::uint16_t mask = VS_BIT;
	m_reject &= ~mask;	    
    }
	
    if (m_reject & US_BIT)
    {
	SendCameraAckHandler::cameraACKTotalRejection( m_communicator->systemId(), m_communicator->componentId(), 0  );  
	std::uint16_t mask = US_BIT;
	m_reject &= ~mask;	    
    }

    if (m_reject & CI_FAIL_BIT)
    {
	SendCameraAckHandler::cameraACKCameraInformationReqFailed( m_communicator->systemId(), m_communicator->componentId(), 0  );
	std::uint16_t mask = CI_FAIL_BIT;
	m_reject &= ~mask;
    }

    if (m_reject & CS_FAIL_BIT)
    {
	SendCameraAckHandler::cameraACKCameraSettingsReqFailed( m_communicator->systemId(), m_communicator->componentId(), 0  );  
	std::uint16_t mask = CS_FAIL_BIT;
	m_reject &= ~mask;
    }
	
    if (m_reject & SI_FAIL_BIT)
    {
	SendCameraAckHandler::cameraACKCameraStorageInfoReqFailed( m_communicator->systemId(), m_communicator->componentId(), 0  );  
	std::uint16_t mask = SI_FAIL_BIT;
	m_reject &= ~mask;
    }
	
    if (m_reject & CCS_FAIL_BIT)
    {
	SendCameraAckHandler::cameraACKCameraImageCapturedReqFailed( m_communicator->systemId(), m_communicator->componentId(), 0  );  
	std::uint16_t mask = CCS_FAIL_BIT;
	m_reject &= ~mask;
    }
	
    if (m_reject & VS_FAIL_BIT)
    {
	SendCameraAckHandler::cameraACKVideoStreamReqFailed( m_communicator->systemId(), m_communicator->componentId(), 0  );  
	std::uint16_t mask = VS_FAIL_BIT;
	m_reject &= ~mask;	    
    }
	
}
