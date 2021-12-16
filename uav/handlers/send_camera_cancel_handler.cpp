#include "send_camera_cancel_handler.hpp"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendCameraCancelHandler::SendCameraCancelHandler(MavLinkCommunicator* communicator,
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

void SendCameraCancelHandler::sendCmdCancelMAVLinkMessage( std::uint16_t cmd, std::uint8_t target_sys, std::uint8_t target_comp )
{
  std::uint16_t len=0u;

  mavlink_command_cancel_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = cmd;
  
  /* encode */
  len = mavlink_msg_command_cancel_encode(target_sys, target_comp, &message, &com);
  m_communicator->sendMessageOnLastReceivedLink(message);
}

/*
   This is the message the Camera will send as an ACK to the GCS if cancel was received
*/
void SendCameraCancelHandler::cameraCancelCameraInformationReqAccepted( std::uint8_t target_sys, std::uint8_t componentId )
{
    SendCameraCancelHandler::sendCmdCancelMAVLinkMessage( MAV_RESULT_CANCELLED, target_sys, std::uint8_t target_comp, std::uint8_t componentId)
}

/*
    This is the message the Camera Board shall send back to the GCS on receipt of the above message
*/
void SendCameraAckHandle::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)
    if (m_substate == DO_SEND_CANCEL)
    {
        SendCameraCancelHandler::cameraCancelCameraInformationReqAccepted( m_communicator->systemId(), m_communicator->componentId() );
        m_substate = GO_IDLE;
        m_sendState = GO_IDLE;
    }
}






