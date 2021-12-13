#include "send_camera_ack_handler.h"

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
void SendCameraAckHandler::cameraACKCameraInformationReqAccepted( std::uint8_t target_sys, std::uint8_t componentId )
{
   //const std::int8_t CAMERA_INFORMATION = 259;
   //target_sys = MAV_TYPE_GCS;
   SendCameraAckHandler::sendCmdACKMAVLinkMessage( MAV_RESULT_ACCEPTED, 100, MAV_CMD_REQUEST_MESSAGE, target_sys, CAMERA_INFORMATION, std::uint8_t componentId);
}

/*
    This is the message the Camera Board shall send back to the GCS on receipt of the above message
*/
void SendCameraAckHandle::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)
    SendCameraAckHandler::cameraACKCameraInformationReqAccepted( m_communicator->systemId(), m_communicator->componentId() );
}
