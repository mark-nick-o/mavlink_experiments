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
void SendCameraAckHandler::cameraACKCameraInformationReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_INFORMATION );
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void MavlinkCommunicator::cameraACKCameraSettingsReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_SETTINGS);
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void MavlinkCommunicator::cameraACKCameraStorageInfoReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez  )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, STORAGE_INFORMATION);  
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void MavlinkCommunicator::cameraACKCameraImageCapturedReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, CAMERA_IMAGE_CAPTURED);      
}

/*
   This is next the message the Camera will send to the GCS to accept this communication
*/
void MavlinkCommunicator::cameraACKVideoStreamReqAccepted( std::uint8_t target_sys, std::uint8_t componentId, std::uint8_t progrez )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, progrez, MAV_CMD_REQUEST_MESSAGE, target_sys, componentId, VIDEO_STREAM_STATUS);      
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
}
