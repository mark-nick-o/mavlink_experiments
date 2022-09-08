#ifndef DEFS_H
#define DEFS_H 



#define SYSTEM_ID 1
#define COMPONENT_ID 100
#define AUTH_TIMEOUT_SEC 10
#define HEARTBEAT_TIMEOUT_SEC 1
#define FC_TARGET 1
#define FC_TARGET_COMPONENT 0

#define MAX_VALID_ALTITUDE 300.0f
// 1 minute of authorization
#define AUTHORIZATION_TIMEOUT_SEC 60

// https://mavlink.io/en/messages/common.html#VISION_POSITION_ESTIMATE
#define enable_msg_vision_position_estimate = True
#define vision_position_estimate_msg_hz_default  30.0

// https://mavlink.io/en/messages/ardupilotmega.html#VISION_POSITION_DELTA
#define enable_msg_vision_position_delta = False
#define vision_position_delta_msg_hz_default  30.0

// https://mavlink.io/en/messages/common.html#VISION_SPEED_ESTIMATE
#define enable_msg_vision_speed_estimate = True
#define vision_speed_estimate_msg_hz_default  30.0

// https://mavlink.io/en/messages/common.html#STATUSTEXT
#define enable_update_tracking_confidence_to_gcs = True
#define update_tracking_confidence_to_gcs_hz_default = 1.0

// Default global position for EKF home/ origin
#define enable_auto_set_ekf_home = False
#define home_lat  151269321    // Somewhere random
#define home_lon  16624301     // Somewhere random
#define home_alt  163000       // Somewhere random

// TODO: Taken care of by ArduPilot, so can be removed (once the handling on AP side is confirmed stable)
// In NED frame, offset from the IMU or the center of gravity to the camera's origin point
#define body_offset_enabled = 0
#define body_offset_x = 0  # In meters (m)
#define body_offset_y = 0  # In meters (m)
#define body_offset_z = 0  # In meters (m)

// Global scale factor, position x y z will be scaled up/down by this factor
#define scale_factor_ = 1.0

// Enable using yaw from compass to align north (zero degree is facing north)
#define compass_enabled  0
#define TARGET_SYSTEM_ID 1
#define BASIC_INFO_HEARTBEAT_BIT (1 << 0)
#define BASIC_INFO_LOCAL_POSITION_NED_BIT (1 << 1)
#define BASIC_INFO_EXTENDED_SYS_STATE_BIT (1 << 2)
#define BASIC_INFO_HOME_POSITION (1 << 3)
#define BASIC_INFO_ALL_BITS (BASIC_INFO_HEARTBEAT_BIT | BASIC_INFO_LOCAL_POSITION_NED_BIT | BASIC_INFO_EXTENDED_SYS_STATE_BIT | BASIC_INFO_HOME_POSITION)
#define FC_MAIN_MODE_CUSTOM 1
#define FC_CUSTOM_MODE_OFFBOARD 6
#define ATTITUDE_FREQUENCY 30







#endif