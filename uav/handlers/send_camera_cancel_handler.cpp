#include "send_camera_cancel_handler.h"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendCameraAckHandler::SendCameraCancelHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40); // 25 Hz
}

void SendCameraCancelHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

void SendCameraAckHandler::sendCmdCancelMAVLinkMessage( std::uint16_t cmd, std::uint8_t target_sys, std::uint8_t target_comp, std::uint8_t componentId )
{
  std::uint16_t len=0u;

  mavlink_command_cancel_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = cmd;
  
  /* encode */
  len = mavlink_msg_command_cancel_encode(target_sys, componentId, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   This is the message the Camera will send as an ACK to the GCS if cancel was received
*/
void SendCameraAckHandler::cameraCancelCameraInformationReqAccepted( std::uint8_t componentId )
{
	//const std::int8_t CAMERA_INFORMATION = 259;
	SendCameraAckHandler::sendCmdCancelMAVLinkMessage( MAV_RESULT_CANCELLED,  MAV_TYPE_GCS, std::uint8_t target_comp, std::uint8_t componentId)
}







