#include "send_cmd_req_handler.hpp"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendCmdReqHandler::SendCmdReqHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
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
}
