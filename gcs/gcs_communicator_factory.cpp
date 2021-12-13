#include "gcs_communicator_factory.h"

// MAVLink
#include <mavlink.h>

// Internal
#include "mavlink_communicator.h"

#include "heartbeat_handler.h"
#include "attitude_handler.h"
#include "get_camera_info_handler.hpp"
#include "send_cmd_req_handler.hpp"
#include "battery_status.hpp"

using namespace domain;

GcsCommunicatorFactory::GcsCommunicatorFactory()
{}

MavLinkCommunicator* GcsCommunicatorFactory::create()
{
    MavLinkCommunicator* communicator = new MavLinkCommunicator(255, 0);

    new domain::HeartHandler(communicator, m_model);
    new domain::AttitudeHandler(communicator);
    new domain::SendCmdReqHandler(communicator, m_model);
    new domain::getCamInfoHandler(communicator, m_model);
    new domain::BattStatHandler(communicator, m_model);
    
    return communicator;
}
