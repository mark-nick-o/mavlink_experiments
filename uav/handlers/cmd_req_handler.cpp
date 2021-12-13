#include "cmd_req_handler.hpp"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

using namespace domain;

CmdReqHandler::CmdReqHandler(MavLinkCommunicator* communicator):
    AbstractHandler(communicator)
{}

void CmdReqHandler::processMessage(const mavlink_message_t& message)
{
    if (message.msgid != MAV_CMD_REQUEST_MESSAGE || message.sysid == 0) return;

    mavlink_cmd_request_t cmdReq;
    mavlink_msg_cmd_request_decode(&message, &cmdReq);

    switch (cmdReq.param1)
    {
	   case CAMERA_INFORMATION:
           /* send information regarding the camera  */
	   m_substate = DO_SEND_ACK;
	   m_sendState = SENS_CI;
           break;

	   case CAMERA_SETTINGS:
	   m_substate = DO_SEND_ACK;
	   m_sendState = SENS_CS;
           break;
		    
           case STORAGE_INFORMATION:
           /* send information regarding the storage media */
	   m_substate = DO_SEND_ACK;
	   m_sendState = SENS_SI;
           break;					
    }
}
