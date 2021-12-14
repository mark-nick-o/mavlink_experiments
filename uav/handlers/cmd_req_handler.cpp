#include "cmd_req_handler.hpp"

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

           case CAMERA_CAPTURE_STATUS:
           /* send information regarding the capture status */
	   m_substate = DO_SEND_ACK;
	   m_sendState = SENS_CCS;
           break;

           case 269:
           /* send information regarding the video streaming status */
	   m_substate = DO_SEND_ACK;
	   m_sendState = SENS_VS;
           break;
			
           default:
           break;
       }
    }
    else if ((cmdReq.command == MAV_CMD_DO_SET_RELAY) && (cmdReq.target_system == MAV_CMP_ID_CAMERA))
    {
	   std::cout << " now set the relay number " << cmdReq.param1 << " to state : " << cmdReq..param2 << std::endl;
    }
}
