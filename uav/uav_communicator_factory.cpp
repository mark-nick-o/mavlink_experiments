#include "uav_communicator_factory.h"

// MAVLink
#include <mavlink.h>

// Internal
#include "mavlink_communicator.h"

#include "send_heartbeat_handler.hpp"
//#include "send_system_status_handler.h"
#include "send_position_handler.h"
#include "send_attitude_handler.h"
#include "send_vfr_hud_handler.h"
#include "send_home_position_handler.h"
#include "send_gps_raw_handler.h"
#include "send_camera_info_handler.hpp"
#include "send_camera_settings_handler.hpp"
#include "send_camera_ack_handler.hpp"
//#include "send_camera_cancel_handler.hpp"
//#include "cmd_req_handler.hpp"
//#include "send_video_stream_handler.hpp"
//#include "send_battery_status.hpp"
//#include "send_camera_storage_info_handler.hpp"
//#include "send_camera_capture_status_handler.hpp"
//#include "send_camera_image_captured_handler.hpp"

using namespace domain;

UavCommunicatorFactory::UavCommunicatorFactory(domain::UavModel* model):
    m_model(model)
{}

MavLinkCommunicator* UavCommunicatorFactory::create()
{
    MavLinkCommunicator* communicator = new MavLinkCommunicator(1, 0);
   
    new domain::HeartbeatHandler(MAV_TYPE_FIXED_WING, communicator);
    //new domain::CmdReqHandler(communicator, m_model); 
    
    new domain::SendSystemStatusHandler(communicator, m_model);
    new domain::SendPositionHandler(communicator, m_model);
    new domain::SendAttitudeHandler(communicator, m_model);
    new domain::SendVfrHudHandler(communicator, m_model);
    new domain::SendHomePositionHandler(communicator, m_model);
    new domain::SendGpsRawHandler(communicator, m_model);
    new domain::SendCameraInfoHandler(communicator, m_model);
    //new domain::SendCameraAckHandler(communicator, m_model);
    //new domain::SendCameraCancelHandler(communicator, m_model);
    new domain::SendCameraSettingsHandler(communicator, m_model);
    //new domain::SendVideoStreamInfoHandler(communicator, m_model);
    //new domain::SendBatterStatusHandler(communicator, m_model);
    //new domain::SendCameraStorageInfoHandler(communicator, m_model);
    //new domain::SendCameraCaptureStatusHandler(communicator, m_model);
    //new domain::SendCameraImageCapturedHandler(communicator, m_model);
    
    return communicator;
}
