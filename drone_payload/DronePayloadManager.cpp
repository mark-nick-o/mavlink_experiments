
// DronePayloadManager.cpp : Defines the entry point for the application.
//

#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <time.h>
#include <fstream>
#include<sys/sysinfo.h>
#if (defined __QNX__) | (defined __QNXNTO__)
/* QNX specific headers */
#include <unix.h>
#else
/* Linux / MacOS POSIX timer headers */
#include <sys/time.h>
#include <time.h>
#include <arpa/inet.h>
#include <stdbool.h> /* required for the definition of bool in C99 */
#endif

/* This assumes you have the mavlink headers on your include path
 or in the same folder as this source file */
#include "libs/mavlink2C/common/mavlink.h"
#include "libs/mavlink2C/checksum.h"                                            // cyclic redundancy for MAVLINK
#include "libs/mavlink2C/mavlink_types.h"                                       // structures for message types
#include "libs/mavlink2C/common/common.h"                                       // common enum and structs for command set
#include "libs/mavlink2C/protocol.h"                                            // protocol driver
#include "libs/mavlink2C/mavlink_sha256.h"                                      // sha256 implementation
#include "libs/mavlink2C/mavlink_get_info.h"                                    // get info request if 24bit set
#include "libs/mavlink2C/mavlink_helpers.h"                                     // general helper functions
#include "libs/mavlink2C/mavlink_conversions.h"
#include "libs/mavlink2C/common/mavlink_msg_file_transfer_protocol.h"           // for example mavftp if needed
#include "libs/mavlink2C/common/mavlink_msg_param_ext_ack.h"                    // this is the message it will use to send an ack to QGC
#include "libs/mavlink2C/common/mavlink_msg_param_ext_value.h"                  // this is the message it will use to confirm a value to QGC
#include "libs/mavlink2C/common/mavlink_msg_param_value.h"                      // this is the message it will use to confirm a value to Mission Planner
#include "libs/mavlink2C/common/mavlink_msg_camera_capture_status.h"
#include "libs/mavlink2C/common/mavlink_msg_camera_image_captured.h"
#include "libs/mavlink2C/common/mavlink_msg_camera_information.h"
#include "libs/mavlink2C/common/mavlink_msg_command_ack.h"
#include "libs/mavlink2C/common/mavlink_msg_storage_information.h"
#include "libs/mavlink2C/common/mavlink_msg_rc_channels.h"

#include "libs/mavlink2C/ardupilotmega/mavlink_msg_digicam_control.h"
#include "libs/mavlink2C/ardupilotmega/mavlink_msg_digicam_configure.h"

#include "libs/SonySDK/app/CameraDevice.h"

 // ==================== include enumeration library ====================
#include "libs/SonySDK/app/sony_a7_enumerate.cpp"
#include <endian.h>
#include <algorithm>

// ==================== logger using poco ================================
#include "Poco/Logger.h"
#include "Poco/ConsoleChannel.h"
#include "Poco/SimpleFileChannel.h"
#include "Poco/SplitterChannel.h"
#include "Poco/FormattingChannel.h"
#include "Poco/PatternFormatter.h"
#include "Poco/AutoPtr.h"
#include <Poco/Logger.h>
#include <Poco/ConsoleChannel.h>
#include <Poco/SimpleFileChannel.h>
#include <Poco/SplitterChannel.h>
#include <Poco/FormattingChannel.h>
#include <Poco/PatternFormatter.h>
#include <Poco/AutoPtr.h>

using Poco::Logger;
using Poco::ConsoleChannel;
using Poco::SimpleFileChannel;
using Poco::SplitterChannel;
using Poco::FormattingChannel;
using Poco::PatternFormatter;
using Poco::AutoPtr;

#define BUFFER_LENGTH 2041 // minimum buffer size that can be used with qnx (I don't know why)
#define UDP_PORT_NO 14550

namespace SDK = SCRSDK;

uint64_t microsSinceEpoch();
static volatile bool g_should_exit;
int sock = socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP);
struct sockaddr_in gcAddr;

// default sys id - we get a heartbeat from the master which locks our sys id at initialization
bool g_not_initialized = false;
int g_sys_id = 2;
int g_camId_photo = MAV_COMP_ID_CAMERA;                                     // default camera ID will be read from .ini file
std::uint16_t g_recording_state = 0;                                        // global containing the recording state

// flag which says we are not counting this picture
std::uint32_t g_total_pic_count = 0;

// make a union to convert types
//
union float_integer_u {
	std::uint32_t i;
	float f;
	std::uint64_t l;
	double d;
};

int g_status_txt_cnt = 0;

/*static int msg_send(mavlink_message_t *msg)
{
	uint8_t data[MAVLINK_MAX_PACKET_LEN];
	uint16_t len = mavlink_msg_to_send_buffer(data, msg);
	//return sendto(sock, data, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}*/

static int msg_send(mavlink_message_t* msg)
{
	uint8_t data[MAVLINK_MAX_PACKET_LEN];

	uint16_t len = mavlink_msg_to_send_buffer(data, msg);
	return sendto(sock, data, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
}

static void cam_param_request_list(uint8_t target_sys, uint8_t target_comp)
{
	mavlink_message_t msg;

	mavlink_param_request_list_t cprl;
	cprl.target_system = target_sys;
	cprl.target_component = target_comp;
	mavlink_msg_param_request_list_encode(target_sys, target_comp, &msg, &cprl);
	msg_send(&msg);
}

static void mav_send_cam_info_uri(uint8_t target_sys, uint8_t target_comp)
{
	mavlink_message_t message;
	mavlink_camera_information_t com;
	com.firmware_version = 10000;	  /*<  Version of the camera firmware (v << 24 & 0xff = Dev, v << 16 & 0xff = Patch, v << 8 & 0xff = Minor, v & 0xff = Major)*/
	com.focal_length = 1.4;			  /*< [mm] Focal length*/
	com.sensor_size_h = 600.0;		  /*< [mm] Image sensor size horizontal*/
	com.sensor_size_v = 300.0;		  /*< [mm] Image sensor size vertical*/
	com.flags = 123;				  /*<  Bitmap of camera capability flags.*/
	com.resolution_h = 100;			  /*< [pix] Horizontal image resolution*/
	com.resolution_v = 200;			  /*< [pix] Vertical image resolution*/
	com.cam_definition_version = 250; /*<  Camera definition version (iteration)*/
	com.vendor_name[0] = 12;		  /*<  Name of the camera vendor*/
	com.model_name[0] = 7;			  /*<  Name of the camera model*/
	com.lens_id = 1;				  /*<  Reserved for a lens ID*/
	strncpy(com.cam_definition_uri, "http://kerry-air.com/airobot/cam_defs.xml", strlen("http://kerry-air.com/airobot/cam_defs.xml"));
	// 100, MAV_COMP_ID_ALL
	//mavlink_msg_camera_information_encode(100, MAV_COMP_ID_ALL, &message, &com);
	mavlink_msg_camera_information_encode(target_sys, target_comp, &message, &com);
	printf("Camera Info : %s\n", com.cam_definition_uri);
	// msg_send(&message);
}

std::uint32_t get_uptime()
{
	struct sysinfo s_info;
	int error = sysinfo(&s_info);
	if (error != 0)
	{
		//printf("code error=%d\ n",error);
		std::cout << error << "\n";
	}
	return s_info.uptime;
}

int sendCamInfo(uint8_t target_sys, uint8_t target_comp) {
	std::chrono::milliseconds uptime(0u);
	double uptime_seconds;
	if (std::ifstream("/proc/uptime", std::ios::in) >> uptime_seconds)
	{
		uptime = std::chrono::milliseconds(
			static_cast<unsigned long long>(uptime_seconds * 1000.0)
		);
	}
	mavlink_camera_information_t f;
	std::cout << "\033[33m ---------CAM_INFO--------------- \033[0m " << std::endl;
	f.time_boot_ms = get_uptime();
	std::string sony = "Sony";
	memcpy((void*)&f.vendor_name[0], (const void*)&sony[0], 4);
	std::string model = "Alpha7";
	memcpy((void*)&f.model_name[0], (const void*)&model[0], 6);
	f.firmware_version = (5 << 8) | 1;
	f.focal_length = 400;
	f.sensor_size_h = 30;
	f.sensor_size_v = 30;
	f.resolution_h = 1080;
	f.resolution_v = 1080;
	f.lens_id = 1;
	f.flags = CAMERA_CAP_FLAGS_CAPTURE_VIDEO | CAMERA_CAP_FLAGS_CAPTURE_IMAGE | CAMERA_CAP_FLAGS_HAS_MODES | CAMERA_CAP_FLAGS_HAS_BASIC_FOCUS | CAMERA_CAP_FLAGS_HAS_VIDEO_STREAM;
	f.cam_definition_version = 1;
	strcpy(f.cam_definition_uri, "http://kerry-air.com/airobot/cam_defs.xml");

	std::cout << f.time_boot_ms << std::endl;
	std::cout << f.vendor_name << std::endl;
	std::cout << f.model_name << std::endl;
	std::cout << f.firmware_version << std::endl;
	std::cout << f.focal_length << std::endl;
	std::cout << f.sensor_size_h << std::endl;
	std::cout << f.sensor_size_v << std::endl;
	std::cout << f.resolution_h << std::endl;
	std::cout << f.resolution_v << std::endl;
	std::cout << f.lens_id << std::endl;
	std::cout << f.flags << std::endl;
	std::cout << f.cam_definition_version << std::endl;
	std::cout << f.cam_definition_uri << std::endl;

	mavlink_message_t message;
	std::uint8_t buf[MAVLINK_MSG_ID_CAMERA_INFORMATION_LEN];

	int len = mavlink_msg_camera_information_encode(target_sys, target_comp, &message, &f);  /* encode */
	len = mavlink_msg_to_send_buffer(buf, &message);
	// now send buf where you want to
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
	printf("Camera Info : %s\n", f.cam_definition_uri);
}

int sendParamExtValue(uint8_t target_sys, uint8_t target_comp, std::string param_id, std::uint32_t param_value, std::uint16_t param_index, std::uint16_t param_count)
{
	mavlink_param_ext_value_t setValue;
	strncpy(setValue.param_id, param_id.c_str(), sizeof(setValue.param_id));
	//strncpy(setValue.param_value, param_value.c_str(), sizeof(param_value));

	setValue.param_value[0] = (char)(param_value) & 0xff;
	setValue.param_value[1] = (char)(param_value >> 8) & 0xFF;
	setValue.param_value[2] = (char)(param_value >> 16) & 0xFF;
	setValue.param_value[3] = (char)(param_value >> 24) & 0xFF;


	//setValue.param_value[0] = param_value;
	setValue.param_type = MAV_PARAM_EXT_TYPE_UINT32;
	setValue.param_count = param_count;
	setValue.param_index = param_index;

	mavlink_message_t message;
	std::uint8_t buf[MAVLINK_MSG_ID_PARAM_VALUE_LEN];

	int len = mavlink_msg_param_ext_value_encode(target_sys, target_comp, &message, &setValue);  /* encode */
	len = mavlink_msg_to_send_buffer(buf, &message);
	printf("Param EXT Value : %s\n", setValue.param_value);
	printf("param ext value bytes sent %d\n", len);
	// now send buf where you want to
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
}

int sendParamValue(uint8_t target_sys, uint8_t target_comp, std::string param_id, std::float_t param_value, std::uint16_t param_index, std::uint16_t param_count)
{
	mavlink_param_value_t setValue;
	strncpy(setValue.param_id, param_id.c_str(), sizeof(setValue.param_id));
	//strncpy(setValue.param_value, param_value.c_str(), sizeof(param_value));

	setValue.param_value = param_value;
	setValue.param_type = MAV_PARAM_TYPE_UINT32;
	setValue.param_count = param_count;
	setValue.param_index = param_index;

	mavlink_message_t message;
	std::uint8_t buf[MAVLINK_MSG_ID_PARAM_VALUE_LEN];

	int len = mavlink_msg_param_value_encode(target_sys, target_comp, &message, &setValue);  /* encode */
	len = mavlink_msg_to_send_buffer(buf, &message);
	printf("Param Value : %.9g\n", setValue.param_value);
	printf("param info bytes sent %d\n", len);
	// now send buf where you want to
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
}

int sendCameraCaptureStatus(uint8_t target_sys, uint8_t target_comp)
{
	std::chrono::milliseconds uptime(0u);
	double uptime_seconds;
	if (std::ifstream("/proc/uptime", std::ios::in) >> uptime_seconds)
	{
		uptime = std::chrono::milliseconds(
			static_cast<unsigned long long>(uptime_seconds * 1000.0)
		);
	}
	mavlink_camera_capture_status_t setValue;
	printf("Uptime : %d\n", get_uptime());
	setValue.time_boot_ms = get_uptime();
	setValue.image_status = 0;
	setValue.video_status = g_recording_state;
	setValue.image_interval = 0;
	setValue.recording_time_ms = 0;
	setValue.available_capacity = 500;
	setValue.image_count = 5;

	mavlink_message_t message;
	std::uint8_t buf[MAVLINK_MSG_ID_CAMERA_CAPTURE_STATUS_LEN];

	int len = mavlink_msg_camera_capture_status_encode(target_sys, target_comp, &message, &setValue);  /* encode */
	len = mavlink_msg_to_send_buffer(buf, &message);

	printf("capture status bytes sent %d\n", len);
	// now send buf where you want to
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
}

int sendCameraStorageInfo(uint8_t target_sys, uint8_t target_comp)
{
	std::chrono::milliseconds uptime(0u);
	double uptime_seconds;
	if (std::ifstream("/proc/uptime", std::ios::in) >> uptime_seconds)
	{
		uptime = std::chrono::milliseconds(
			static_cast<unsigned long long>(uptime_seconds * 1000.0)
		);
	}
	mavlink_storage_information_t setValue;
	printf("Uptime : %d\n", get_uptime());
	setValue.time_boot_ms = get_uptime();
	setValue.storage_id = 1;
	setValue.storage_count = 2;
	setValue.status = STORAGE_STATUS_READY;
	setValue.total_capacity = 500;
	setValue.used_capacity = 100;
	setValue.available_capacity = 400;
	setValue.read_speed = 1;
	setValue.write_speed = 1;
	setValue.type = STORAGE_TYPE_SD;
	strncpy(&setValue.name[0], "AIRobot", 8);
	setValue.storage_usage = STORAGE_USAGE_FLAG_SET;

	mavlink_message_t message;
	std::uint8_t buf[MAVLINK_MSG_ID_STORAGE_INFORMATION_LEN];

	int len = mavlink_msg_storage_information_encode(target_sys, target_comp, &message, &setValue);  /* encode */
	len = mavlink_msg_to_send_buffer(buf, &message);

	printf("storage info bytes sent %d\n", len);
	// now send buf where you want to
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
}

int sendCameraSettings(uint8_t target_sys, uint8_t target_comp)
{
	std::chrono::milliseconds uptime(0u);
	double uptime_seconds;
	if (std::ifstream("/proc/uptime", std::ios::in) >> uptime_seconds)
	{
		uptime = std::chrono::milliseconds(
			static_cast<unsigned long long>(uptime_seconds * 1000.0)
		);
	}
	mavlink_camera_settings_t setValue;
	printf("Uptime : %d\n", get_uptime());
	setValue.time_boot_ms = get_uptime();
	setValue.mode_id = CAMERA_MODE_IMAGE;
	setValue.zoomLevel = 50.00;
	setValue.focusLevel = 50.00;

	mavlink_message_t message;
	std::uint8_t buf[MAVLINK_MSG_ID_CAMERA_SETTINGS_LEN];

	int len = mavlink_msg_camera_settings_encode(target_sys, target_comp, &message, &setValue);  /* encode */
	len = mavlink_msg_to_send_buffer(buf, &message);

	printf("camera settings bytes sent %d\n", len);
	// now send buf where you want to
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
}

/*
	vehicle->requestDataStream(MAV_DATA_STREAM_RAW_SENSORS,     2);
	vehicle->requestDataStream(MAV_DATA_STREAM_EXTENDED_STATUS, 2);
	vehicle->requestDataStream(MAV_DATA_STREAM_RC_CHANNELS,     2);
	vehicle->requestDataStream(MAV_DATA_STREAM_POSITION,        3);
	vehicle->requestDataStream(MAV_DATA_STREAM_EXTRA1,          20);
	vehicle->requestDataStream(MAV_DATA_STREAM_EXTRA2,          10);
	vehicle->requestDataStream(MAV_DATA_STREAM_EXTRA3,          3);
	https://github.com/mavlink/qgroundcontrol/blob/master/src/FirmwarePlugin/APM/ArduSubFirmwarePlugin.cc
*/

int requestDataStream(uint8_t target_sys, uint8_t target_comp, uint8_t stream_id, uint8_t state, uint16_t rate)
{

	/*
	* @brief Pack a on board off / on message
	*
	* @param OnBoardState float32_t <0.5f off >0.5f on
	* @param target_sys uint8_t target system
	* @param target_comp uint8_t target component
	* @param conf uint8_t confirmation
	* @param componentId uint8_t component id
	* @return length of the message in bytes (excluding serial stream start sign)
	*/
	mavlink_data_stream_t command = { 0u };                                          // Command Type
	mavlink_message_t msg;                                                        // encoder type
	command.message_rate = rate;
	command.stream_id = stream_id;
	command.on_off = state;

	/* encode */
	//mavlink_msg_data_stream_encode(target_sys, target_comp, &msg, &command);

	/* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
	//msg_send(&msg);
	std::cout << "> Data Stream Request Made" << static_cast<uint16_t>(stream_id) << std::endl;

	std::uint8_t buf[MAVLINK_MSG_ID_DATA_STREAM_LEN];

	int len = mavlink_msg_data_stream_encode(target_sys, target_comp, &msg, &command);  /* encode */
	len = mavlink_msg_to_send_buffer(buf, &msg);

	// now send buf where you want to
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
}

int sendLongCommandAck(uint8_t target_sys, uint8_t target_comp, std::uint16_t command)
{
	mavlink_command_ack_t setValue;
	setValue.command = command;
	setValue.result = MAV_RESULT_ACCEPTED;
	setValue.progress = 100;
	setValue.result_param2 = 0;
	setValue.target_system = target_sys;
	setValue.target_component = target_comp;

	mavlink_message_t message;
	std::uint8_t buf[MAVLINK_MSG_ID_COMMAND_ACK_LEN];

	int len = mavlink_msg_command_ack_encode(target_sys, target_comp, &message, &setValue); /* encode */
	len = mavlink_msg_to_send_buffer(buf, &message);
	printf("command long bytes sent %d\n", len);

	// now send buf where you want to
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
}

int sendSetParamExtAck(uint8_t target_sys, uint8_t target_comp, std::string param_id, std::string param_value, uint8_t type)
{
	mavlink_param_ext_ack_t setValue;
	strncpy(setValue.param_id, param_id.c_str(), sizeof(param_id));
	strncpy(setValue.param_value, param_value.c_str(), sizeof(param_value));
	/*setValue.param_value[0] = (char)(param_value) & 0xff;
	setValue.param_value[1] = (char)(param_value >> 8) & 0xFF;
	setValue.param_value[2] = (char)(param_value >> 16) & 0xFF;
	setValue.param_value[3] = (char)(param_value >> 24) & 0xFF;*/
	setValue.param_type = MAV_PARAM_TYPE_UINT32;
	setValue.param_result = type;

	mavlink_message_t message;
	std::uint8_t buf[MAVLINK_MSG_ID_PARAM_EXT_ACK_LEN];

	int len = mavlink_msg_param_ext_ack_encode(target_sys, target_comp, &message, &setValue);  /* encode */
	len = mavlink_msg_to_send_buffer(buf, &message);
	printf("Param Value : %s\n", setValue.param_value);
	printf("param ext ack bytes sent %d\n", len);
	// now send buf where you want to
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
}

int sendServoRawToSocket(uint8_t target_sys, uint8_t target_comp, std::uint16_t a1, std::uint16_t a2, std::uint16_t a3, std::uint16_t a4, std::uint8_t p)
{
	mavlink_servo_output_raw_t setValue;
	setValue.servo9_raw = a1;
	setValue.servo10_raw = a2;
	setValue.servo11_raw = a3;
	setValue.servo12_raw = a4;
	setValue.port = p;
	setValue.time_usec = get_uptime();

	mavlink_message_t message;
	std::uint8_t buf[MAVLINK_MSG_ID_SERVO_OUTPUT_RAW_LEN];

	int len = mavlink_msg_servo_output_raw_encode(target_sys, target_comp, &message, &setValue);  /* encode */
	len = mavlink_msg_to_send_buffer(buf, &message);
	printf("Servo Raw : %d %d %d %d %d\n", setValue.servo9_raw, setValue.servo10_raw, setValue.servo11_raw, setValue.servo12_raw, setValue.port);
	printf("servo raw to gimbal serial bytes sent %d\n", len);
	// now send buf where you want to
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
}

//#define LINUX_SERIAL
#if defined(LINUX_SERIAL)
int sendServoRawToSerial(std::uint16_t a1, std::uint16_t a2, std::uint16_t a3, std::uint16_t a4, std::uint8_t p, int fd)
#else
int sendServoRawToSerial(uint8_t target_sys, uint8_t target_comp, std::uint16_t a1, std::uint16_t a2, std::uint16_t a3, std::uint16_t a4, std::uint8_t p)
#endif
{
	mavlink_servo_output_raw_t setValue;
	setValue.servo9_raw = a1;
	setValue.servo10_raw = a2;
	setValue.servo11_raw = a3;
	setValue.servo12_raw = a4;
	setValue.port = p;
	setValue.time_usec = get_uptime();

	mavlink_message_t message;
	std::uint8_t buf[MAVLINK_MSG_ID_SERVO_OUTPUT_RAW_LEN];

	int len = mavlink_msg_servo_output_raw_encode(target_sys, target_comp, &message, &setValue);  /* encode */
	len = mavlink_msg_to_send_buffer(buf, &message);
	printf("Servo Raw : %d %d %d %d %d\n", setValue.servo9_raw, setValue.servo10_raw, setValue.servo11_raw, setValue.servo12_raw, setValue.port);
	printf("servo raw to gimbal serial bytes sent %d\n", len);

#if defined(LINUX_SERIAL)
	write(fd, buf, len);
#elif defined(BOOST_SERIAL)
	gimbal_cmd.write_byte_array(&buf[0]);
#else
	// now send buf where you want to
	sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
	// 
	// example :: gimbal_cmd.write_byte_array(&buf[0]); 
	//
#endif
	return 1;             // change to send to serial port for gimbal.......
}

int SendComRequestSERVO_OUTPUT_RAWInterval(uint8_t target_sys, uint8_t target_comp, float rate)
{

	/*
	* @brief Pack a on board off / on message
	*
	* @param OnBoardState float32_t <0.5f off >0.5f on
	* @param target_sys uint8_t target system
	* @param target_comp uint8_t target component
	* @param conf uint8_t confirmation
	* @param componentId uint8_t component id
	* @return length of the message in bytes (excluding serial stream start sign)
	*/
	std::cout << "> Requesting Servo Data at rate of 10Hz from FCU \n";
	mavlink_command_long_t command = { 0u };                                          // Command Type
	mavlink_message_t msg;                                                            // encoder type
	command.target_system = target_sys;
	command.target_component = target_comp;
	command.command = MAV_CMD_SET_MESSAGE_INTERVAL;
	command.confirmation = 0;
	command.param1 = MAVLINK_MSG_ID_SERVO_OUTPUT_RAW;
	// command.param2 = 1000000;                                                         10 Hz
	command.param2 = rate;
	std::uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN];
	/* encode */
	int len = mavlink_msg_command_long_encode(target_sys, target_comp, &msg, &command);

	/* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
	//msg_send(&msg);
	len = mavlink_msg_to_send_buffer(buf, &msg);
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));

}

#include "mavlink_status_msg.cpp"                                                // wrapper for sending status messages
#include "poco_script_runner.cpp"                                                // reset the usb power 

// =================== focus adjust algorythm ===========================
#include "focus_adjustment.h"
// =================== to get shutter speeds into vector ================
#include "poco_get_ss.cpp"

#if defined(LINUX_SERIAL)
#include "linux_serial.cpp"  
#elif defined(BOOST_SERIAL)
#include "boost_serial_class.cpp"
#endif

static void exit_socket_handler(int signum)
{
	// if(signum == SIGINT)
	//    {paus= true;}
//else
	{
		std::cout << std::endl << "Signum " << signum << " ";
		std::cout << "Exception handler closing socket" << std::endl;
		close(sock);
		g_should_exit = true;
		_exit(EXIT_FAILURE);
	}
}

void clean_and_destroy() {

	cli::tout << "Release SDK resources...\n";
	// cr_lib->Release();
	SDK::Release();
}

#if defined(LINUX_SERIAL)
int fd;                        // serial port file descriptor
#endif

void close_serial() {
#if defined(LINUX_SERIAL)
	serial_gimbal_close(fd);
#elif defined(BOOST_SERIAL)
	gimbal_cmd.close();
#endif
}

bool g_pause = false;
void exit_signal_handler(int signo) {

	switch (signo)
	{
	    case SIGUSR1:
		cli::tout << " --------- GOt the SIGUSR1 e.g. kill -12 Do your chosen exception here ------------------- " << "\n";
		break;

	    case SIGHUP:                                // disconnecting (hanging) the controlling terminal, terminating the virtual terminal
		clean_and_destroy();
		cli::tout << " --------- Got the SIGHUP clean-up & exit ------------------- " << "\n";
		exit_socket_handler(signo);
		close_serial();
		exit(-SIGHUP);
		break;

	    case SIGINT:                               // INTERRUPT SIGNAL FROM KEYBOARD (USUALLY [CTRL]+[C])
		clean_and_destroy();
		cli::tout << " --------- Got the SIGINT clean-up & exit ------------------- " << "\n";
		exit_socket_handler(signo);
		close_serial();
		exit(-SIGINT);
		break;

	    case SIGQUIT:                              // KEYBOARD ABORT SIGNAL (USUALLY [CTRL]+[\])
		clean_and_destroy();
		cli::tout << " --------- Got the SIGQUIT clean-up & exit ------------------- " << "\n";
		exit_socket_handler(signo);
		close_serial();
		exit(-SIGQUIT);
		break;

	    case SIGFPE:	                          // occurrence of illegal floating-point operations (such as division by zero or overflow)	
		clean_and_destroy();
		cli::tout << " --------- Got the SIGFPE clean-up & exit ------------------- " << "\n";
		exit_socket_handler(signo);
		close_serial();
		exit(-SIGFPE);
		break;

	    case SIGKILL:	                         // FORCE EXIT SIGNAL (KILL SIGNAL)	
		clean_and_destroy();
		cli::tout << " --------- Got the SIGKILL clean-up & exit ------------------- " << "\n";
		exit_socket_handler(signo);
		close_serial();
		exit(-SIGKILL);
		break;

	    case SIGSEGV:	                         // incorrect memory reference occurrence	
		clean_and_destroy();
		cli::tout << " --------- Got the SIGSEGV clean-up & exit ------------------- " << "\n";
		exit_socket_handler(signo);
		close_serial();
		exit(-SIGSEGV);
		break;

	    case SIGPIPE:	                         // 	writing to a pipe without a reader (usually terminating immediately upon receiving this signal)	
		clean_and_destroy();
		cli::tout << " --------- Got the SIGPIPE clean-up & exit ------------------- " << "\n";
		exit_socket_handler(signo);
		close_serial();
		exit(-SIGPIPE);
		break;

	    case SIGTERM:	                        // 	exit signal (default signal for the "kill" command)
		clean_and_destroy();
		cli::tout << " --------- Got the SIGTERM clean-up & exit ------------------- " << "\n";
		exit_socket_handler(signo);
		close_serial();
		exit(-SIGTERM);
		break;

	    case SIGCONT:	                        // 	resume signal to a paused job
		g_pause = false;
		break;

	    case SIGSTOP:	                        // 	start a paused job
		g_pause = true;
		break;

	    case SIGTSTP:	                        // 	PAUSE SIGNAL FROM THE TERMINAL (USUALLY [CTRL] + [Z])
		clean_and_destroy();
		cli::tout << " --------- Got the SIGTSTP clean-up & exit ------------------- " << "\n";
		exit_socket_handler(signo);
		close_serial();
		exit(-SIGTSTP);
		break;

	    default:
		cli::tout << " --------- Got the unknown signal = " << signo << " clean - up & exit------------------ - " << "\n";
		break;
	}
}

static void setup_signal_handlers()
{
	struct sigaction sa = { };
	std::cout << "> Setting up signal handlers" << std::endl;
	sa.sa_flags = SA_NOCLDSTOP;
	sa.sa_handler = exit_signal_handler;
#if defined(_MSC_VER)
	//Allow floating-point exceptions
	_control87(0, _MCW_EM);
#endif
	sigaction(SIGTERM, &sa, NULL);
	sigaction(SIGINT, &sa, NULL);
	sigaction(SIGQUIT, &sa, NULL);
	sigaction(SIGFPE, &sa, NULL);
	sigaction(SIGHUP, &sa, NULL);
	/* alarm handler is being used to periodically control stream messages so surpress it sigaction(SIGALRM, &sa, NULL); */
	sigaction(SIGSEGV, &sa, NULL);
	sigaction(SIGTSTP, &sa, NULL);

}

int SendComRequest_RC_CHANNELS(uint8_t target_sys, uint8_t target_comp, float rate)
{

	/*
	* @brief Pack a on board off / on message
	*
	* @param OnBoardState float32_t <0.5f off >0.5f on
	* @param target_sys uint8_t target system
	* @param target_comp uint8_t target component
	* @param conf uint8_t confirmation
	* @param componentId uint8_t component id
	* @return length of the message in bytes (excluding serial stream start sign)
	*/
	mavlink_command_long_t command = { 0u };                                          // Command Type
	mavlink_message_t msg;                                                        // encoder type
	command.target_system = target_sys;
	command.target_component = target_comp;
	command.command = MAV_CMD_SET_MESSAGE_INTERVAL;
	//command.confirmation     = target_comp;
	command.param1 = (float)(MAVLINK_MSG_ID_RC_CHANNELS);
	command.param2 = rate;                                                // 10 Hz
	command.param7 = 2.0f;
	/* encode */
	//mavlink_msg_command_long_encode(target_sys, target_comp, &msg, &command);
	int len = mavlink_msg_command_long_encode(g_sys_id, g_camId_photo, &msg, &command);
	/* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
	//msg_send(&msg);
	std::uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN];
	len = mavlink_msg_to_send_buffer(buf, &msg);
	return sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
	printf("Requesting MAVLINK_MSG_ID_RC_CHANNELS Data, Target_sys %u, Targer Component, %u \n", target_sys, target_comp);
}

// disable the raw Channel message periodically to prevent Mission Planner starting and resetting the update for the unwanted message
// the function polls every timer interval (15 secs)
//
void alrm(int signo)
{
	// set slow rate on servo output
	int st = clock();
	// slow down raw interval
	int sntbyte1 = SendComRequestSERVO_OUTPUT_RAWInterval(g_sys_id, 0, 1000000000000000.0f);
	// rc channel for control @ 10Hz from FCU
	int sntbyte2 = SendComRequest_RC_CHANNELS(g_sys_id, 1, 1000000.0f);
	int en = clock();
	std::cout << "action time from alarm handler : " << (en - st) / double(CLOCKS_PER_SEC) * 1000.0f << "sent " << sntbyte1 << " " << sntbyte2 << "\n";
	// this would stop the RC_CHAN message SendComRequest_RC_CHANNELS(system_ID, 0, 1000000000000000.0f); 
}

int main(int argc, char* argv[])
{
	// use console
	//AutoPtr<ConsoleChannel> pChannel(new ConsoleChannel);

	// use file
	//AutoPtr<SimpleFileChannel> pChannel2(new SimpleFileChannel);
	//pChannel2->setProperty("path", "/home/pi/cam_init/dpm_sample.log");
	//pChannel2->setProperty("rotation", "2 K");
	// use splitter if you want both
	//AutoPtr<SplitterChannel> pSC(new SplitterChannel);
	//AutoPtr<PatternFormatter> pPF(new PatternFormatter);
	// poco pattern
	//pPF->setProperty("pattern", "[%p] %Y-%m-%d %H:%M:%S: %t");
	//AutoPtr<FormattingChannel> pFC(new FormattingChannel(pPF, pSC));
	// add the console and file to the spliiter
	//pSC->addChannel(pChannel);
	//pSC->addChannel(pChannel2);
	// choose the splitter for example
	//Logger::root().setChannel(pFC);
	// choose file only
	//Logger::root().setChannel(pChannel2); 
	// choose console only
	//Logger::root().setChannel(pChannel);  
	//Logger& logger = Logger::root(); // inherits root channel
	// write some infomration to the logger
	//logger.information("Started the drone payload manager event");

	//run_script("python3", "/home/pi/uhubctl/reset_usb.py", 1);
	int code_ret = reset_usb_sony();

	// set up poll action timer to keep unwanted messages out
	// at present when Mission Planner is connected it resets the SErvo RAW frequency message
	// therefore we time an action every RAW_STOP_SECS to supress it
	//
	const uint16_t RAW_STOP_SECS = 15u;
	struct sigaction sa_alarm;
	struct itimerval itimer;
	memset(&sa_alarm, 0, sizeof(sa_alarm));
	sa_alarm.sa_handler = alrm;
	sa_alarm.sa_flags = SA_RESTART;
	if (sigaction(SIGALRM, &sa_alarm, NULL) < 0) {
		perror("sigaction");
		exit(1);
    }
	itimer.it_value.tv_sec = itimer.it_interval.tv_sec = RAW_STOP_SECS;
	itimer.it_value.tv_usec = itimer.it_interval.tv_usec = 0;
	if (setitimer(ITIMER_REAL, &itimer, NULL) < 0) {
		perror("set timer");
		exit(1);
	}

#if defined(LINUX_SERIAL)
	serial_gimbal_open(fd);
#elif defined(BOOST_SERIAL)
	boost::asio::io_service ios;
	serialport gimbal_cmd(ios);
	gimbal_cmd.setPort(GIMBAL_USB_CONNECTION);                                 // where you conencted your gimbal
	gimbal_cmd.setSpeed(GREMSY_GIMBAL_BAUD);                                   // gimbal BAUD RATE
	gimbal_cmd.setTimeout_sec(1);                                              // port timeout to 1 second
	if (gimbal_cmd.open() == false) {
		cli::tout << " gimbal serial port could not be opened please check and try again ....." << gimbal_cmd.getPort() << "\n";
	}
#endif

	std::tuple<std::string, CrInt8, std::uint32_t> GetStillCapMode("notset", 0, 0);
	std::tuple<std::string, CrInt8, std::uint32_t> GetAperture("notset", 0, 0);
	std::tuple<std::string, CrInt8, std::uint32_t> GetExposureMode("notset", 0, 0);
	std::tuple<std::string, CrInt8, std::uint32_t> GetIso("notset", 0, 0);
	std::tuple<std::string, CrInt8, std::uint32_t> GetShutterSpeed("notset", 0, 0);
	std::tuple<std::string, CrInt8, std::uint32_t> GetWhiteBalance("notset", 0, 0);
	std::tuple<std::string, CrInt8, std::uint32_t> GetFocusArea("notset", 0, 0);
	std::tuple<std::string, CrInt8, std::uint32_t> GetFocusMode("notset", 0, 0);
	union float_integer_u type_convert_union;

	//Sony SDK INIT --START---------------------------------------------------------------------------------------------------------------------------------------------------
	CrInt32u version = SDK::GetSDKVersion();
	int major = (version & 0xFF000000) >> 24;
	int minor = (version & 0x00FF0000) >> 16;
	int patch = (version & 0x0000FF00) >> 8;
	// int reserved = (version & 0x000000FF);

	cli::tout << "Remote SDK version: ";
	cli::tout << major << "." << minor << "." << std::setfill(TEXT('0')) << std::setw(2) << patch << "\n";

	// Load the library dynamically
	// cr_lib = cli::load_cr_lib();

	cli::tout << "Initialize Remote SDK...\n";

	auto init_success = SDK::Init();
	if (!init_success) {
		cli::tout << "Failed to initialize Remote SDK. Terminating.\n";
		// cr_lib->Release();
		SDK::Release();
		std::exit(EXIT_FAILURE);
	}
	cli::tout << "Remote SDK successfully initialized.\n\n";
	cli::tout << "Enumerate connected camera devices...\n";
	SDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
	// auto enum_status = cr_lib->EnumCameraObjects(&camera_list, 3);
	auto enum_status = SDK::EnumCameraObjects(&camera_list);
	if (CR_FAILED(enum_status) || camera_list == nullptr) {
		cli::tout << "No cameras detected. Connect a camera and retry.\n";
		// cr_lib->Release();
		SDK::Release();
		std::exit(EXIT_FAILURE);
	}
	auto ncams = camera_list->GetCount();
	cli::tout << "Camera enumeration successful. " << ncams << " detected.\n\n";

	/*for (CrInt32u i = 0; i < ncams; ++i) {
		auto camera_info = camera_list->GetCameraObjectInfo(i);
		cli::text conn_type(camera_info->GetConnectionTypeName());
		cli::text model(camera_info->GetModel());
		cli::text id = TEXT("");
		if (TEXT("IP") == conn_type) {
			cli::NetworkInfo ni = cli::parse_ip_info(camera_info->GetId(), camera_info->GetIdSize());
			id = ni.mac_address;
		}
		else id = ((TCHAR*)camera_info->GetId());
		cli::tout << '[' << i + 1 << "] " << model.data() << " (" << id.data() << ")\n";
	}*/

	CrInt32u no = 1;

	typedef std::shared_ptr<cli::CameraDevice> CameraDevicePtr;
	typedef std::vector<CameraDevicePtr> CameraDeviceList;
	CameraDeviceList cameraList; // all
	std::int32_t cameraNumUniq = 1;
	std::int32_t selectCamera = 1;

	cli::tout << "Connect to selected camera...\n";
	auto* camera_info = camera_list->GetCameraObjectInfo(0);

	cli::tout << "Create camera SDK camera callback object.\n";
	CameraDevicePtr camera = CameraDevicePtr(new cli::CameraDevice(cameraNumUniq, nullptr, camera_info));
	cameraList.push_back(camera); // add 1st

	cli::tout << "Release enumerated camera list.\n";
	camera_list->Release();

	if (camera->is_connected()) {
		cli::tout << "Please disconnect\n";
	}
	else {
		camera->connect(SDK::CrSdkControlMode_Remote);
	}
	camera->get_sdkmode();

	//Sony SDK INIT --END------------------------------------------------------------------------------------------------------------------------------------------------------
	
	// use this label to jump to if you dont have the camera if you want to
	//
    End_SDK_Init:

	char help[] = "--help";

	char target_ip[100];

	//struct sockaddr_in gcAddr;
	struct sockaddr_in locAddr;
	// struct sockaddr_in fromAddr;
	uint8_t buf[BUFFER_LENGTH];
	ssize_t recsize;
	socklen_t fromlen = sizeof(gcAddr);
	int bytes_sent;
	mavlink_message_t msg;
	uint16_t len;
	int i = 0;
	// int success = 0;
	unsigned int temp = 0;

	// Check if --help flag was used
	if ((argc == 2) && (strcmp(argv[1], help) == 0))
	{
		printf("\n");
		printf("\tUsage:\n\n");
		printf("\t");
		printf("%s", argv[0]);
		printf(" <ip address of QGroundControl>\n");
		printf("\tDefault for localhost: udp-server 127.0.0.1\n\n");
		exit(EXIT_FAILURE);
	}

	// Change the target ip if parameter was given
	strcpy(target_ip, "0.0.0.0");
	if (argc == 2)
	{
		strcpy(target_ip, argv[1]);
	}

	memset(&locAddr, 0, sizeof(locAddr));
	locAddr.sin_family = AF_INET;
	locAddr.sin_addr.s_addr = INADDR_ANY;
	locAddr.sin_port = htons(14551);

	/* Bind the socket to port 14551 - necessary to receive packets from qgroundcontrol */
	if (-1 == bind(sock, (struct sockaddr*)&locAddr, sizeof(struct sockaddr)))
	{
		perror("error bind failed");
		close(sock);
		exit(EXIT_FAILURE);
	}

	/* Attempt to make it non blocking */
#if (defined __QNX__) | (defined __QNXNTO__)
	if (fcntl(sock, F_SETFL, O_NONBLOCK | FASYNC) < 0)
#else
	if (fcntl(sock, F_SETFL, O_NONBLOCK | O_ASYNC) < 0)
#endif

	{
		fprintf(stderr, "error setting nonblocking: %s\n", strerror(errno));
		close(sock);
		exit(EXIT_FAILURE);
	}

	memset(&gcAddr, 0, sizeof(gcAddr));
	gcAddr.sin_family = AF_INET;
	gcAddr.sin_addr.s_addr = inet_addr(target_ip);
	gcAddr.sin_port = htons(UDP_PORT_NO);

	mavlink_message_t message;
	mavlink_camera_information_t com;
	com.firmware_version = 10000;	  /*<  Version of the camera firmware (v << 24 & 0xff = Dev, v << 16 & 0xff = Patch, v << 8 & 0xff = Minor, v & 0xff = Major)*/
	com.focal_length = 1.4;			  /*< [mm] Focal length*/
	com.sensor_size_h = 600.0;		  /*< [mm] Image sensor size horizontal*/
	com.sensor_size_v = 300.0;		  /*< [mm] Image sensor size vertical*/
	com.flags = 123;				  /*<  Bitmap of camera capability flags.*/
	com.resolution_h = 100;			  /*< [pix] Horizontal image resolution*/
	com.resolution_v = 200;			  /*< [pix] Vertical image resolution*/
	com.cam_definition_version = 250; /*<  Camera definition version (iteration)*/
	com.vendor_name[0] = 12;		  /*<  Name of the camera vendor*/
	com.model_name[0] = 7;			  /*<  Name of the camera model*/
	com.lens_id = 1;				  /*<  Reserved for a lens ID*/
	strcpy(com.cam_definition_uri, "http://kerry-air.com/airobot/cam_defs.xml");

	mavlink_msg_camera_information_encode(g_sys_id, g_camId_photo, &message, &com);

	uint8_t data[MAVLINK_MAX_PACKET_LEN];

	setup_signal_handlers();

	int timer = 0;

	std::string ssi = "DronePayloadManager :: Started-up successfully !! ";
	rfc5424_facility_e f = user_level;
	rfc5424_severity_e s = rfc5424_info;
	std::uint16_t is = 0;                                                                                  // this should read from a file..
	sendStatusTextMessage(ssi, f, s, is, g_sys_id);

	camera->get_aperture();
	sleep(2);

	// grab all data as a single shot and update the objects with the data
	//
	std::vector<std::tuple<std::string, std::uint8_t, std::uint32_t>> p;
	if (camera->LoadMavProperties(p) == 1) {
		SCRSDK::CrNearFarEnableStatus nf_stat = camera->get_near_far_from_cam_vector(p);
		SCRSDK::CrMovie_Recording_State rec_stat = camera->get_rec_state_from_cam_vector(p);
		CrInt8 rec_msg = camera->printCrMovie_Recording_State(rec_stat);
		g_recording_state = static_cast<std::uint16_t>(rec_msg);
		cli::tout << "loaded the camera props....... near-far is " << nf_stat << "\n";
	}
	for (auto tup : p) {
		cli::tout << " property name " << std::get<0>(tup) << " value = " << std::get<2>(tup) << "\n";
	}

	// ============================================ focus adjustment ====================================================== 
	sony_focus_settings_t camera_chan_obj;
	init_focus_mode(&camera_chan_obj);
	int snt1 = SendComRequestSERVO_OUTPUT_RAWInterval(g_sys_id, 0, 1000000000000000.0f);                       // request the SERVO RAW CHANNEL messages to be slow 
	int snt2 = SendComRequest_RC_CHANNELS(g_sys_id, 1, 1000000.0f);                                            // request the RADIO CONTROL CHANNEL messages at freq of 10Hz from FCU
	cli::tout << " set-up comm request messages for RC channels" << snt1 << " " << snt2 << "\n";
	std::vector<std::uint32_t> poss_shutter_speeds;                                                                                  // create a vector of allowable shutter sppeds read from the xml
	std::vector<std::uint32_t> poss_FNumbers;                                                                                        // create a vector of allowable aperture FNum settings read from the xml
	std::vector<std::uint32_t> poss_Iso;                                                                                             // create a vector of allowable iso values read from the xml
	try {
		    Poco::XML::DOMParser parser;
		    // -----> parse the xml and read into the vector the values for shutter speed in the xml order <-----
		    //
		    Poco::AutoPtr<Poco::XML::Document> doc = parser.parse("/home/pi/cam_init/sony_new_xml.xml");

		    std::string tag = "CAM_SHUTTERSPD";

			poss_shutter_speeds = read_xml_value_for_tag(doc, tag);
		    int ii = 0;
		    for (auto x : poss_shutter_speeds) {
			    ++ii;
			    std::cout << "read ss from XML : [" << ii << "]  " << x << std::endl;
		    }

			tag = "CAM_APERTURE";

			poss_FNumbers = read_xml_value_for_tag(doc, tag);
			ii = 0;
			for (auto x : poss_FNumbers) {
				++ii;
				std::cout << "read aper from XML : [" << ii << "]  " << x << std::endl;
			}

			tag = "CAM_ISO";

			poss_Iso = read_xml_value_for_tag(doc, tag);
			ii = 0;
			for (auto x : poss_Iso) {
				++ii;
				std::cout << "read iso from XML : [" << ii << "]  " << x << std::endl;
			}
	}
	catch (Exception& e) {
		    std::cerr << e.displayText() << std::endl;
	}

    // this bit is done in the mavlink code which is in the DronePayload project
	camera_chan_obj.use_sdk_shut = 7;
	// now get the actual value for it from the xml read
	std::uint32_t raw_ss_val = get_shutter_from_index_pl(poss_shutter_speeds, &camera_chan_obj);
	std::cout << " got the value for Shutter Speed as : " << raw_ss_val << std::endl;
	camera_chan_obj.use_sdk_fnum = 0;
	// now get the actual value for it from the xml read
	std::uint32_t raw_fnum_val = get_FNum_from_index_pl(poss_FNumbers, &camera_chan_obj);
	std::cout << " got the value for Aperture as : " << raw_fnum_val << std::endl;
	camera_chan_obj.use_sdk_iso = 0;
	// now get the actual value for it from the xml read
	std::uint32_t raw_iso_val = get_Iso_from_index_pl(poss_Iso, &camera_chan_obj);
	std::cout << " got the value for Iso as : " << raw_iso_val << std::endl;

	// start the rc channel data stream @ 1Hz initially
	requestDataStream(g_sys_id, g_camId_photo, MAV_DATA_STREAM_RC_CHANNELS, 1, 1);

	for (;;)
	{
		memset(buf, 0, BUFFER_LENGTH);
		memset(data, 0, MAVLINK_MAX_PACKET_LEN);


		if (timer == 600000) {
			/*Send Heartbeat */
			mavlink_msg_heartbeat_pack(g_sys_id, g_camId_photo, &msg, MAV_TYPE_CAMERA, MAV_AUTOPILOT_INVALID, 0, 0, MAV_STATE_ACTIVE);
			len = mavlink_msg_to_send_buffer(buf, &msg);
			bytes_sent = sendto(sock, buf, len, 0, (struct sockaddr*)&gcAddr, sizeof(struct sockaddr_in));
			timer = 0;
		}
		++timer;

		recsize = recvfrom(sock, (void*)buf, BUFFER_LENGTH, 0, (struct sockaddr*)&gcAddr, &fromlen);
		if (recsize > 0)
		{
			// Something received - print out all bytes and parse packet
			mavlink_message_t msg;
			mavlink_status_t status;

			// printf("Bytes Received: %d\nDatagram: ", (int)recsize);
			for (i = 0; i < recsize; ++i)
			{
				temp = buf[i];
				// printf("%02x ", (unsigned char)temp);

				// auto res = mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status);
				// std::cout<<std::endl<<"Result " <<res <<" ";

				if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status) > 0)
				{
					/*if (msg.sysid == 242)
					{
						printf("\nParsed Part : Received packets: SYS: %d, COMP: %d, LEN: %d, MSG ID: %d\n", msg.sysid, msg.compid, msg.len, msg.msgid);
					}*/

					switch (msg.msgid)
					{

					case MAVLINK_MSG_ID_HEARTBEAT:
					{
						if (g_not_initialized == true) {
							mavlink_heartbeat_t h;
							mavlink_msg_heartbeat_decode(&msg, &h);
							if (h.autopilot != MAV_AUTOPILOT_INVALID) {
								g_sys_id = msg.sysid;
								std::cout << "\033[31m New SysID Found as \033[0m" << g_sys_id << std::endl;
							}
							g_not_initialized = false;
						}
					}
					break;

					case MAVLINK_MSG_ID_COMMAND_LONG:
					{
						printf("***MAVLINK_MSG_ID_COMMAND_LONG***\n");
						printf("\nReceived packets: SYS: %d, COMP: %d, LEN: %d, MSG ID: %d\n", msg.sysid, msg.compid, msg.len, msg.msgid);
						mavlink_command_long_t cmdReq;
						mavlink_msg_command_long_decode(&msg, &cmdReq);
						printf("Printing command: %d\n", cmdReq.command);
						switch (cmdReq.command)
						{
						case MAV_CMD_REQUEST_CAMERA_INFORMATION:
						{
							uint16_t result = sendLongCommandAck(g_sys_id, g_camId_photo, MAV_CMD_REQUEST_CAMERA_INFORMATION);
							printf("\nLong command Ack sent for MAV_CMD_REQUEST_CAMERA_INFORMATION %u\n", result);
							printf("--MAV_CMD_REQUEST_CAMERA_INFORMATION--\n");
							uint16_t len = mavlink_msg_to_send_buffer(data, &message);
							bytes_sent = sendto(sock, data, len, 0, (struct sockaddr*)&gcAddr, sizeof(gcAddr));
							printf("camera info bytes sent %d\n", bytes_sent);
							break;
						}
						case MAV_CMD_REQUEST_STORAGE_INFORMATION:
						{
							uint16_t result = sendLongCommandAck(g_sys_id, g_camId_photo, MAV_CMD_REQUEST_STORAGE_INFORMATION);
							printf("\nLong command Ack sent for MAV_CMD_REQUEST_STORAGE_INFORMATION %u\n", result);
							printf("--MAV_CMD_REQUEST_STORAGE_INFORMATION--\n");
							int bytesrecinfo = sendCameraStorageInfo(g_sys_id, g_camId_photo);
							printf("sendCameraStorageInfo info bytes sent %u\n", bytesrecinfo);
							break;
						}
						case MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS:
						{
							uint16_t result = sendLongCommandAck(g_sys_id, g_camId_photo, MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS);
							printf("\nLong command Ack sent for MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS %u\n", result);
							printf("--MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS--\n");
							/*int bytesrecvack = sendCameraAck(MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS, MAV_RESULT_IN_PROGRESS);
							printf("sendCameraFirstAck info bytes sent %u\n", bytesrecvack);*/

							int bytesrecv = sendCameraCaptureStatus(g_sys_id, g_camId_photo);
							printf("sendCameraCaptureStatus info bytes sent %u\n", bytesrecv);

							/*bytesrecvack = sendCameraAck(MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS, MAV_RESULT_ACCEPTED);
							printf("sendCameraSecondAck info bytes sent %u\n", bytesrecvack);*/
							break;
						}
						case MAV_CMD_REQUEST_CAMERA_SETTINGS:
						{
							uint16_t result = sendLongCommandAck(g_sys_id, g_camId_photo, MAV_CMD_REQUEST_CAMERA_SETTINGS);
							printf("\nLong command Ack sent for MAV_CMD_REQUEST_CAMERA_SETTINGS %u\n", result);
							printf("--MAV_CMD_REQUEST_CAMERA_SETTINGS--\n");
							int bytesrecv = sendCameraSettings(g_sys_id, g_camId_photo);
							printf("sendCameraSettings info bytes sent %u\n", bytesrecv);
							break;
						}
						case MAV_CMD_IMAGE_START_CAPTURE:
						{
							camera->capture_image();
							uint16_t result = sendLongCommandAck(g_sys_id, g_camId_photo, MAV_CMD_IMAGE_START_CAPTURE);
							++g_total_pic_count;
							break;
						}

						case MAV_CMD_DO_DIGICAM_CONTROL:
						{
							printf("command Long DO_DIGICAM_CONTROL received shoot=%f shot=%f\n",cmdReq.param5,cmdReq.param7);
							uint16_t result = sendLongCommandAck(g_sys_id, g_camId_photo, MAV_CMD_DO_DIGICAM_CONTROL);
							if (cmdReq.param5 == 1.0f) {
								camera->capture_image();
								if (cmdReq.param7 != 1.0f) {
									++g_total_pic_count;
								}
							}
						}
						break;

					    case MAV_CMD_DO_DIGICAM_CONFIGURE:
						{
							uint16_t result = sendLongCommandAck(g_sys_id, g_camId_photo, MAV_CMD_DO_DIGICAM_CONFIGURE);
							int mode_req = static_cast<std::uint32_t>(cmdReq.param1);
							std::uint32_t ss_req = enumerate_still_cap_sony_a7( static_cast<std::uint32_t>(cmdReq.param2) );
							camera->SetStillCaptureModeArgsInt(ss_req);
							std::uint32_t ap_req = enumerate_aperture_sony_a7( static_cast<std::uint32_t>(cmdReq.param3));
							camera->SetApertureArgsInt(ss_req);
							std::uint32_t iso_req = enumerate_iso_sony_a7(static_cast<std::uint32_t>(cmdReq.param4));
							camera->SetIsoArgsInt(ss_req);
							float eng_cut_off = cmdReq.param7;
						}
						break;

						case MAV_CMD_VIDEO_START_CAPTURE:
						{
							//camera->execute_movie_rec();
							camera->execute_movie_rec_int(1);
							uint16_t result = sendLongCommandAck(g_sys_id, g_camId_photo, MAV_CMD_VIDEO_START_CAPTURE);
							g_recording_state = 1;
						}
						break;

						case MAV_CMD_VIDEO_STOP_CAPTURE:
						{
							//camera->change_live_view_enable();
							camera->execute_movie_rec_int(0);
							uint16_t result = sendLongCommandAck(g_sys_id, g_camId_photo, MAV_CMD_VIDEO_STOP_CAPTURE);
							g_recording_state = 0;
						}
						break;

						case MAV_CMD_SET_CAMERA_FOCUS:
						{
							uint16_t result = sendLongCommandAck(g_sys_id, g_camId_photo, MAV_CMD_SET_CAMERA_FOCUS);
							printf("command Long SET_CAMERA_FOCUS type=%f value=%f\n", cmdReq.param1, cmdReq.param2);
							// read and set the focus
							std::string focus_mode;
							std::stringstream ss_conv;
							ss_conv << enumerate_focus_sony_a7(static_cast<std::uint32_t>(cmdReq.param1));
							ss_conv >> focus_mode;
							if (camera->SetFocusModeArgs(focus_mode) == 1) {
								int bytesrecv = sendCameraSettings(g_sys_id, g_camId_photo);
								printf("sendCameraSettings info bytes sent %u\n", bytesrecv);
							}
						}
						break;

						default:
							break;
						}
						break;
					}

					case MAVLINK_MSG_ID_DIGICAM_CONTROL:
					{
						mavlink_digicam_control_t dc;
						mavlink_msg_digicam_control_decode(&msg, &dc);
						printf(" Shot : %u ID : %u Target Com : %u Target Sys : %u\n", dc.shot, dc.command_id, dc.target_component, dc.target_system);
						std::uint8_t num_of_pics = dc.command_id;
						while ((num_of_pics > 0) && (dc.shot == 1))  {
							camera->capture_image();
							--num_of_pics;
							++g_total_pic_count;
						}
					}
					break;

					case MAVLINK_MSG_ID_DIGICAM_CONFIGURE:
					{
						mavlink_digicam_configure_t dc;
						mavlink_msg_digicam_configure_decode(&msg, &dc);
						printf(" Shutter speed : %u mode : %u aperture : %u iso : %u\n", dc.shutter_speed, dc.mode, dc.aperture, dc.iso);
						printf(" exposure : %u cmd : %u eng cut-off : %u extra param : %u extra value : %f\n", dc.exposure_type, dc.command_id, dc.engine_cut_off, dc.extra_param, dc.extra_value);
						switch (static_cast<std::uint16_t>(dc.command_id)) {
						    case 1:
							{
								int mode_req = static_cast<std::uint32_t>(dc.mode);
							}
							break;

							case 2:
							{
								std::uint32_t ss_req = enumerate_still_cap_sony_a7(static_cast<std::uint32_t>(dc.shutter_speed));
								camera->SetStillCaptureModeArgsInt(ss_req);
							}
							break;

							case 3:
							{
								std::uint32_t ap_req = enumerate_aperture_sony_a7(static_cast<std::uint32_t>(dc.aperture));
								camera->SetApertureArgsInt(ap_req);
							}
							break;

							case 4:
							{
								std::uint32_t iso_req = enumerate_iso_sony_a7(static_cast<std::uint32_t>(dc.iso));
								camera->SetIsoArgsInt(iso_req);
							}
							break;

							case 5:
							{
								std::uint32_t expro_req = enumerate_ex_pro_sony_a7(static_cast<std::uint32_t>(dc.exposure_type));
								camera->SetExposureProgramModeArgsInt(expro_req);
							}
							break;

							case 7:
							{
								std::uint8_t eng_cut_off = dc.engine_cut_off;
							}
							break;

							default:
								break;
						}
					}
					break;

					case MAVLINK_MSG_ID_PARAM_EXT_REQUEST_LIST:
					{
						printf("***MAVLINK_MSG_ID_PARAM_EXT_REQUEST_LIST***\n");
						mavlink_param_ext_request_read_t d;
						mavlink_msg_param_ext_request_read_decode(&msg, &d);

						printf(" Param ID : %s Param Index : %u Target Com : %u Target Sys : %u\n", d.param_id, d.param_index, d.target_component, d.target_system);
						printf("\nReceived packets: SYS: %d, COMP: %d, LEN: %d, MSG ID: %d\n", msg.sysid, msg.compid, msg.len, msg.msgid);
						//S_STILL_CAP
						GetStillCapMode = camera->GetStillCapMode();
						sendParamExtValue(g_sys_id, g_camId_photo, "S_STILL_CAP", std::get<2>(GetStillCapMode), 6, 8);
						//CAM_APERTURE
						GetAperture = camera->GetAperture();
						sendParamExtValue(g_sys_id, g_camId_photo, "CAM_APERTURE", std::get<2>(GetAperture), 0, 8);
						//CAM_EXPMODE
						GetExposureMode = camera->GetExposureMode();
						sendParamExtValue(g_sys_id, g_camId_photo, "CAM_EXPMODE", std::get<2>(GetExposureMode), 3, 8);
						//CAM_ISO
						GetIso = camera->GetIso();
						sendParamExtValue(g_sys_id, g_camId_photo, "CAM_ISO", std::get<2>(GetIso), 2, 8);
						//CAM_SHUTTERSPD
						GetShutterSpeed = camera->GetShutterSpeed();
						sendParamExtValue(g_sys_id, g_camId_photo, "CAM_SHUTTERSPD", std::get<2>(GetShutterSpeed), 1, 8);
						//CAM_WBMODE
						GetWhiteBalance = camera->GetWhiteBalance();
						sendParamExtValue(g_sys_id, g_camId_photo, "CAM_WBMODE", std::get<2>(GetWhiteBalance), 4, 8);
						//S_FOCUS_AREA
						GetFocusArea = camera->GetFocusArea();
						sendParamExtValue(g_sys_id, g_camId_photo, "S_FOCUS_AREA", std::get<2>(GetFocusArea), 7, 8);
						//S_FOCUS_MODE
						GetFocusMode = camera->GetFocusMode();
						sendParamExtValue(g_sys_id, g_camId_photo, "S_FOCUS_MODE", std::get<2>(GetFocusMode), 5, 8);
						break;
					}

					case MAVLINK_MSG_ID_PARAM_EXT_REQUEST_READ:
					{
						printf("***MAVLINK_MSG_ID_PARAM_EXT_REQUEST_READ***\n");
						mavlink_param_ext_request_read_t d;
						mavlink_msg_param_ext_request_read_decode(&msg, &d);

						printf("\nReceived packets in param ext read : SYS: %d, COMP: %d, LEN: %d, MSG ID: %d\n", msg.sysid, msg.compid, msg.len, msg.msgid);

						printf(" Param ID : %s Param Index : %u Target Com : %u Target Sys : %u\n", d.param_id, d.param_index, d.target_component, d.target_system);

						if (strncmp(d.param_id, "S_STILL_CAP", strlen("S_STILL_CAP")) == 0) {
							GetStillCapMode = camera->GetStillCapMode();
							sendParamExtValue(g_sys_id, g_camId_photo, "S_STILL_CAP", std::get<2>(GetStillCapMode), -1, 8);
						}
						else if (strncmp(d.param_id, "CAM_APERTURE", strlen("CAM_APERTURE")) == 0) {
							GetAperture = camera->GetAperture();
							sendParamExtValue(g_sys_id, g_camId_photo, "CAM_APERTURE", std::get<2>(GetAperture), -1, 8);
						}
						else if (strncmp(d.param_id, "CAM_EXPMODE", strlen("CAM_EXPMODE")) == 0) {
							GetExposureMode = camera->GetExposureMode();
							sendParamExtValue(g_sys_id, g_camId_photo, "CAM_EXPMODE", std::get<2>(GetExposureMode), -1, 8);
						}
						else if (strncmp(d.param_id, "CAM_ISO", strlen("CAM_ISO")) == 0) {
							GetIso = camera->GetIso();
							sendParamExtValue(g_sys_id, g_camId_photo, "CAM_ISO", std::get<2>(GetIso), -1, 8);
						}
						else if (strncmp(d.param_id, "CAM_SHUTTERSPD", strlen("CAM_SHUTTERSPD")) == 0) {
							GetShutterSpeed = camera->GetShutterSpeed();
							sendParamExtValue(g_sys_id, g_camId_photo, "CAM_SHUTTERSPD", std::get<2>(GetShutterSpeed), -1, 8);
						}
						else if (strncmp(d.param_id, "CAM_WBMODE", strlen("CAM_WBMODE")) == 0) {
							GetWhiteBalance = camera->GetWhiteBalance();
							sendParamExtValue(g_sys_id, g_camId_photo, "CAM_WBMODE", std::get<2>(GetWhiteBalance), -1, 8);
						}
						else if (strncmp(d.param_id, "S_FOCUS_AREA", strlen("S_FOCUS_AREA")) == 0) {
							GetFocusArea = camera->GetFocusArea();
							sendParamExtValue(g_sys_id, g_camId_photo, "S_FOCUS_AREA", std::get<2>(GetFocusArea), -1, 8);
						}
						else if (strncmp(d.param_id, "S_FOCUS_MODE", strlen("S_FOCUS_MODE")) == 0) {
							GetFocusMode = camera->GetFocusMode();
							sendParamExtValue(g_sys_id, g_camId_photo, "S_FOCUS_MODE", std::get<2>(GetFocusMode), -1, 8);
						}
						break;
					}

					case MAVLINK_MSG_ID_PARAM_REQUEST_LIST:
					{
						printf("***MAVLINK_MSG_ID_PARAM_REQUEST_LIST***\n");
						mavlink_param_ext_request_read_t d;
						mavlink_msg_param_ext_request_read_decode(&msg, &d);

						printf(" Param ID : %s Param Index : %u Target Com : %u Target Sys : %u\n", d.param_id, d.param_index, d.target_component, d.target_system);
						printf("\nReceived packets: SYS: %d, COMP: %d, LEN: %d, MSG ID: %d\n", msg.sysid, msg.compid, msg.len, msg.msgid);

						//S_STILL_CAP
						GetStillCapMode = camera->GetStillCapMode();
						type_convert_union.i = std::get<2>(GetStillCapMode);
						sendParamValue(g_sys_id, g_camId_photo, "S_STILL_CAP", type_convert_union.f, 6, 8);
						//CAM_APERTURE
						GetAperture = camera->GetAperture();
						type_convert_union.i = std::get<2>(GetAperture);
						sendParamValue(g_sys_id, g_camId_photo, "CAM_APERTURE", type_convert_union.f, 0, 8);
						//CAM_EXPMODE
						GetExposureMode = camera->GetExposureMode();
						type_convert_union.i = std::get<2>(GetExposureMode);
						sendParamValue(g_sys_id, g_camId_photo, "CAM_EXPMODE", type_convert_union.f, 3, 8);
						//CAM_ISO
						GetIso = camera->GetIso();
						type_convert_union.i = std::get<2>(GetIso);
						sendParamValue(g_sys_id, g_camId_photo, "CAM_ISO", type_convert_union.f, 2, 8);
						//CAM_SHUTTERSPD
						GetShutterSpeed = camera->GetShutterSpeed();
						type_convert_union.i = std::get<2>(GetShutterSpeed);
						sendParamValue(g_sys_id, g_camId_photo, "CAM_SHUTTERSPD", type_convert_union.f, 1, 8);
						//CAM_WBMODE
						GetWhiteBalance = camera->GetWhiteBalance();
						type_convert_union.i = std::get<2>(GetWhiteBalance);
						sendParamValue(g_sys_id, g_camId_photo, "CAM_WBMODE", type_convert_union.f, 4, 8);
						//S_FOCUS_AREA
						GetFocusArea = camera->GetFocusArea();
						type_convert_union.i = std::get<2>(GetFocusArea);
						sendParamValue(g_sys_id, g_camId_photo, "S_FOCUS_AREA", type_convert_union.f, 7, 8);
						//S_FOCUS_MODE
						GetFocusMode = camera->GetFocusMode();
						type_convert_union.i = std::get<2>(GetFocusArea);
						sendParamValue(g_sys_id, g_camId_photo, "S_FOCUS_MODE", type_convert_union.f, 5, 8);
						break;
					}

					case MAVLINK_MSG_ID_PARAM_REQUEST_READ:
					{
						printf("***MAVLINK_MSG_ID_PARAM_REQUEST_READ***\n");
						mavlink_param_request_read_t d;
						mavlink_msg_param_request_read_decode(&msg, &d);

						printf("\nReceived packets in param read : SYS: %d, COMP: %d, LEN: %d, MSG ID: %d\n", msg.sysid, msg.compid, msg.len, msg.msgid);

						printf(" Param ID : %s Param Index : %u Target Com : %u Target Sys : %u\n", d.param_id, d.param_index, d.target_component, d.target_system);

						if (strncmp(d.param_id, "S_STILL_CAP", strlen("S_STILL_CAP")) == 0) {
							GetStillCapMode = camera->GetStillCapMode();
							type_convert_union.i = std::get<2>(GetStillCapMode);
							sendParamValue(g_sys_id, g_camId_photo, "S_STILL_CAP", type_convert_union.f, -1, 8);
						}
						else if (strncmp(d.param_id, "CAM_APERTURE", strlen("CAM_APERTURE")) == 0) {
							GetAperture = camera->GetAperture();
							type_convert_union.i = std::get<2>(GetAperture);
							sendParamValue(g_sys_id, g_camId_photo, "CAM_APERTURE", type_convert_union.f, -1, 8);
						}
						else if (strncmp(d.param_id, "CAM_EXPMODE", strlen("CAM_EXPMODE")) == 0) {
							GetExposureMode = camera->GetExposureMode();
							type_convert_union.i = std::get<2>(GetExposureMode);
							sendParamValue(g_sys_id, g_camId_photo, "CAM_EXPMODE", type_convert_union.f, -1, 8);
						}
						else if (strncmp(d.param_id, "CAM_ISO", strlen("CAM_ISO")) == 0) {
							GetIso = camera->GetIso();
							type_convert_union.i = std::get<2>(GetIso);
							sendParamValue(g_sys_id, g_camId_photo, "CAM_ISO", type_convert_union.f, -1, 8);
						}
						else if (strncmp(d.param_id, "CAM_SHUTTERSPD", strlen("CAM_SHUTTERSPD")) == 0) {
							GetShutterSpeed = camera->GetShutterSpeed();
							type_convert_union.i = std::get<2>(GetShutterSpeed);
							sendParamValue(g_sys_id, g_camId_photo, "CAM_SHUTTERSPD", type_convert_union.f, -1, 8);
						}
						else if (strncmp(d.param_id, "CAM_WBMODE", strlen("CAM_WBMODE")) == 0) {
							GetWhiteBalance = camera->GetWhiteBalance();
							type_convert_union.i = std::get<2>(GetWhiteBalance);
							sendParamValue(g_sys_id, g_camId_photo, "CAM_WBMODE", type_convert_union.f, -1, 8);
						}
						else if (strncmp(d.param_id, "S_FOCUS_AREA", strlen("S_FOCUS_AREA")) == 0) {
							GetFocusArea = camera->GetFocusArea();
							type_convert_union.i = std::get<2>(GetFocusArea);
							sendParamValue(g_sys_id, g_camId_photo, "S_FOCUS_AREA", type_convert_union.f, -1, 8);
						}
						else if (strncmp(d.param_id, "S_FOCUS_MODE", strlen("S_FOCUS_MODE")) == 0) {
							GetFocusMode = camera->GetFocusMode();
							type_convert_union.i = std::get<2>(GetFocusArea);
							sendParamValue(g_sys_id, g_camId_photo, "S_FOCUS_MODE", type_convert_union.f, -1, 8);
						}
						break;
					}

					case MAVLINK_MSG_ID_PARAM_EXT_SET:
					{
						printf("***MAVLINK_MSG_ID_PARAM_EXT_SET***\n");
						mavlink_param_ext_set_t d;
						mavlink_msg_param_ext_set_decode(&msg, &d);

						printf("\nReceived packets in param read : SYS: %d, COMP: %d, LEN: %d, MSG ID: %d\n", msg.sysid, msg.compid, msg.len, msg.msgid);

						printf(" Param ID : %s Param Value : [ %u ] [ %u ] [ %u ] [ %u ] Param Type : %u Target Com : %u Target Sys : %u\n", d.param_id, (d.param_value[3]&0xffu), (d.param_value[2]&0xffu), (d.param_value[1]&0xffu), (d.param_value[0]&0xffu), d.param_type, d.target_component, d.target_system);

#if __BYTE_ORDER == __LITTLE_ENDIAN
						std::uint32_t selected_cam_enum = (d.param_value[0]&0xffu) | ((d.param_value[1]&0xffu) << 8) | ((d.param_value[2]&0xffu) << 16) | ((d.param_value[3]&0xffu) << 24);
#elif __BYTE_ORDER == __BIG_ENDIAN
						std::uint32_t selected_cam_enum = (d.param_value[3]&0xffu) | ((d.param_value[2]&0xffu) << 8) | ((d.param_value[1]&0xffu) << 16) | ((d.param_value[0]&0xffu) << 24);
#endif
						std::stringstream ss_stream;
						std::string s_cam_enum;

						printf("received a PARAM_EXT_SET message with a value %u\n", selected_cam_enum);

						if (strncmp(d.param_id, "S_STILL_CAP", strlen("S_STILL_CAP")) == 0) {
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							int bytesfirst = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_IN_PROGRESS);
							ss_stream << enumerate_still_cap_sony_a7(selected_cam_enum);
							ss_stream >> s_cam_enum;
							CrInt8 result = camera->SetStillCaptureModeArgs(s_cam_enum);
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							if (result == -1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_FAILED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_FAILED %u\n", bytesrecinfo);
							}
							else if (result == -2)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_VALUE_UNSUPPORTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_VALUE_UNSUPPORTED %u\n", bytesrecinfo);
							}
							else if (result == 1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_ACCEPTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_ACCEPTED %u\n", bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "CAM_APERTURE", strlen("CAM_APERTURE")) == 0) {
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							int bytesfirst = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_IN_PROGRESS);
							ss_stream << enumerate_aperture_sony_a7(selected_cam_enum);
							ss_stream >> s_cam_enum;
							CrInt8 result = camera->SetApertureArgs(s_cam_enum);
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							if (result == -1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_FAILED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_FAILED %u\n", bytesrecinfo);
							}
							else if (result == -2)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_VALUE_UNSUPPORTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_VALUE_UNSUPPORTED %u\n", bytesrecinfo);
							}
							else if (result == 1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_ACCEPTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_ACCEPTED %u\n", bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "CAM_EXPMODE", strlen("CAM_EXPMODE")) == 0) {
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							int bytesfirst = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_IN_PROGRESS);
							ss_stream << enumerate_ex_pro_sony_a7(selected_cam_enum);
							ss_stream >> s_cam_enum;
							CrInt8 result = camera->SetExposureProgramModeArgs(s_cam_enum);
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							if (result == -1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_FAILED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_FAILED %u\n", bytesrecinfo);
							}
							else if (result == -2)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_VALUE_UNSUPPORTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_VALUE_UNSUPPORTED %u\n", bytesrecinfo);
							}
							else if (result == 1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_ACCEPTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_ACCEPTED %u\n", bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "CAM_ISO", strlen("CAM_ISO")) == 0) {
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							int bytesfirst = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_IN_PROGRESS);
							ss_stream << enumerate_iso_sony_a7(selected_cam_enum);
							ss_stream >> s_cam_enum;
							CrInt8 result = camera->SetIsoArgs(s_cam_enum);
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							if (result == -1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_FAILED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_FAILED %u\n", bytesrecinfo);
							}
							else if (result == -2)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_VALUE_UNSUPPORTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_VALUE_UNSUPPORTED %u\n", bytesrecinfo);
							}
							else if (result == 1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_ACCEPTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_ACCEPTED %u\n", bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "CAM_SHUTTERSPD", strlen("CAM_SHUTTERSPD")) == 0) {
						    ss_stream << selected_cam_enum;
						    ss_stream >> s_cam_enum;
						    int bytesfirst = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_IN_PROGRESS);
							ss_stream << enumerate_shutter_sony_a7(selected_cam_enum);
							ss_stream >> s_cam_enum;
							CrInt8 result = camera->SetShutterSpeedArgs(s_cam_enum);
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							if (result == -1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_FAILED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_FAILED %u\n", bytesrecinfo);
							}
							else if (result == -2)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_VALUE_UNSUPPORTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_VALUE_UNSUPPORTED %u\n", bytesrecinfo);
							}
							else if (result == 1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_ACCEPTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_ACCEPTED %u\n", bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "CAM_WBMODE", strlen("CAM_WBMODE")) == 0) {
					    	ss_stream << selected_cam_enum;
					    	ss_stream >> s_cam_enum;
				    		int bytesfirst = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_IN_PROGRESS);
							ss_stream << enumerate_white_bal_sony_a7(selected_cam_enum);
							ss_stream >> s_cam_enum;
							CrInt8 result = camera->SetWhiteBalanceArgs(s_cam_enum);
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							if (result == -1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_FAILED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_FAILED %u\n", bytesrecinfo);
							}
							else if (result == -2)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_VALUE_UNSUPPORTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_VALUE_UNSUPPORTED %u\n", bytesrecinfo);
							}
							else if (result == 1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_ACCEPTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_ACCEPTED %u\n", bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "S_FOCUS_AREA", strlen("S_FOCUS_AREA")) == 0) {
						    ss_stream << selected_cam_enum;
						    ss_stream >> s_cam_enum;
						    int bytesfirst = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_IN_PROGRESS);
							ss_stream << enumerate_focus_area_sony_a7(selected_cam_enum);
							ss_stream >> s_cam_enum;
							CrInt8 result = camera->SetFocusAreaArgs(s_cam_enum);
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							if (result == -1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_FAILED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_FAILED %u\n", bytesrecinfo);
							}
							else if (result == -2)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_VALUE_UNSUPPORTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_VALUE_UNSUPPORTED %u\n", bytesrecinfo);
							}
							else if (result == 1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_ACCEPTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_ACCEPTED %u\n", bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "S_FOCUS_MODE", strlen("S_FOCUS_MODE")) == 0) {
						    ss_stream << selected_cam_enum;
						    ss_stream >> s_cam_enum;
						    int bytesfirst = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_IN_PROGRESS);
							ss_stream << enumerate_focus_sony_a7(selected_cam_enum);
							ss_stream >> s_cam_enum;
							CrInt8 result = camera->SetFocusModeArgs(s_cam_enum);
							ss_stream << selected_cam_enum;
							ss_stream >> s_cam_enum;
							if (result == -1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_FAILED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_FAILED %u\n", bytesrecinfo);
							}
							else if (result == -2)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_VALUE_UNSUPPORTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_VALUE_UNSUPPORTED %u\n", bytesrecinfo);
							}
							else if (result == 1)
							{
								int bytesrecinfo = sendSetParamExtAck(g_sys_id, g_camId_photo, d.param_id, s_cam_enum, PARAM_ACK_ACCEPTED);
								printf("Set Parameter Ext Ack info bytes sent with result PARAM_ACK_ACCEPTED %u\n", bytesrecinfo);
							}
						}
						break;
					}

					case MAVLINK_MSG_ID_PARAM_SET:
					{
						printf("***MAVLINK_MSG_ID_PARAM_SET***\n");
						mavlink_param_set_t d;
						mavlink_msg_param_set_decode(&msg, &d);

						printf("\n Received packets in param set : SYS: %d, COMP: %d, LEN: %d, MSG ID: %d\n", msg.sysid, msg.compid, msg.len, msg.msgid);

						printf(" Param ID : %s Param Value : %f Param Type : %u Target Com : %u Target Sys : %u\n", d.param_id, d.param_value, d.param_type, d.target_component, d.target_system);

						type_convert_union.f = d.param_value;

#if __BYTE_ORDER == __LITTLE_ENDIAN
						std::uint32_t selected_cam_enum = type_convert_union.i;
#elif __BYTE_ORDER == __BIG_ENDIAN
						std::uint32_t selected_cam_enum = ((std::uint8_t)(type_convert_union.i & 0xf000)) | (((std::uint8_t)(type_convert_union.i & 0x0f00)) << 8) | (((std::uint8_t)(type_convert_union.i & 0x00f0)) << 16) | (((std::uint8_t)(type_convert_union.i & 0x000f)) << 24);
#endif
						std::stringstream ss_stream;
						std::string s_cam_enum;

						printf("received a PARAM_SET message with a value %u\n", selected_cam_enum);

						if (strncmp(d.param_id, "S_STILL_CAP", strlen("S_STILL_CAP")) == 0) {
							//selected_cam_enum = std::clamp(selected_cam_enum, SDK::CrDrive_Single, SDK::CrDrive_SelfPortrait_2);
							ss_stream << enumerate_still_cap_sony_a7(selected_cam_enum);
							int bytesrecinfo = sendParamValue(g_sys_id, g_camId_photo, d.param_id, d.param_value, 6, 8);
							ss_stream >> s_cam_enum;
							if (camera->SetStillCaptureModeArgs(s_cam_enum) == 1)
							{
								//int bytesrecinfo = sendParamValue(d.param_id, d.param_value, 6, 8);
								printf("Set PARAM_SET for %s info bytes sent %u\n", d.param_id, bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "CAM_APERTURE", strlen("CAM_APERTURE")) == 0) {
							//selected_cam_enum = std::clamp(selected_cam_enum, SDK::CrDrive_Single, SDK::CrDrive_SelfPortrait_2);
							ss_stream << enumerate_aperture_sony_a7(selected_cam_enum);
							int bytesrecinfo = sendParamValue(g_sys_id, g_camId_photo, d.param_id, d.param_value, 0, 8);
							ss_stream >> s_cam_enum;
							cli::tout << "set aperture with an index of " << s_cam_enum << "\n";
							if (camera->SetApertureArgs(s_cam_enum) == 1)
							{
								//int bytesrecinfo = sendParamValue(d.param_id, d.param_value, 0, 8);
								printf("Set PARAM_SET for %s info bytes sent %u\n", d.param_id, bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "CAM_EXPMODE", strlen("CAM_EXPMODE")) == 0) {
							//selected_cam_enum = std::clamp(selected_cam_enum, SDK::CrExposure_M_Manual, SDK::CrExposure_Movie_F_Mode);
							ss_stream << enumerate_ex_pro_sony_a7(selected_cam_enum);
							int bytesrecinfo = sendParamValue(g_sys_id, g_camId_photo, d.param_id, d.param_value, 3, 8);
							ss_stream >> s_cam_enum;
							if (camera->SetExposureProgramModeArgs(s_cam_enum) == 1)
							{
								//int bytesrecinfo = sendParamValue(d.param_id, d.param_value, 3, 8);
								printf("Set PARAM_SET for %s info bytes sent %u\n", d.param_id, bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "CAM_ISO", strlen("CAM_ISO")) == 0) {
							//selected_cam_enum = std::clamp(selected_cam_enum,  0, 102400);
							ss_stream << enumerate_iso_sony_a7(selected_cam_enum);
							int bytesrecinfo = sendParamValue(g_sys_id, g_camId_photo, d.param_id, d.param_value, 2, 8);
							ss_stream >> s_cam_enum;
							if (camera->SetIsoArgs(s_cam_enum) == 1)
							{
								//int bytesrecinfo = sendParamValue(d.param_id, d.param_value, 2, 8);
								printf("Set PARAM_SET for %s info bytes sent %u\n", d.param_id, bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "CAM_SHUTTERSPD", strlen("CAM_SHUTTERSPD")) == 0) {
							//selected_cam_enum = std::clamp(selected_cam_enum,  65539, 19660810);
							ss_stream << enumerate_shutter_sony_a7(selected_cam_enum);
							int bytesrecinfo = sendParamValue(g_sys_id, g_camId_photo, d.param_id, d.param_value, 1, 8);;
							ss_stream >> s_cam_enum;
							if (camera->SetShutterSpeedArgs(s_cam_enum) == 1)
							{
								//int bytesrecinfo = sendParamValue(d.param_id, d.param_value, 1, 8);;
								printf("Set PARAM_SET for %s info bytes sent %u\n", d.param_id, bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "CAM_WBMODE", strlen("CAM_WBMODE")) == 0) {
							//selected_cam_enum = std::clamp(selected_cam_enum,  SDK::CrWhiteBalance_AWB, SDK::CrWhiteBalance_Custom);
							ss_stream << enumerate_white_bal_sony_a7(selected_cam_enum);
							int bytesrecinfo = sendParamValue(g_sys_id, g_camId_photo, d.param_id, d.param_value, 4, 8);
							ss_stream >> s_cam_enum;
							if (camera->SetWhiteBalanceArgs(s_cam_enum) == 1)
							{
								//int bytesrecinfo = sendParamValue(d.param_id, d.param_value, 4, 8);
								printf("Set PARAM_SET for %s info bytes sent %u\n", d.param_id, bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "S_FOCUS_AREA", strlen("S_FOCUS_AREA")) == 0) {
							//selected_cam_enum = std::clamp(selected_cam_enum,  SDK::CrFocusArea_Unknown, SDK::CrFocusArea_Tracking_Flexible_Spot);
							ss_stream << enumerate_focus_area_sony_a7(selected_cam_enum);
							int bytesrecinfo = sendParamValue(g_sys_id, g_camId_photo, d.param_id, d.param_value, 7, 8);
							ss_stream >> s_cam_enum;
							if (camera->SetFocusAreaArgs(s_cam_enum) == 1)
							{
								//int bytesrecinfo = sendParamValue(d.param_id, d.param_value, 7, 8);
								printf("Set PARAM_SET for %s info bytes sent %u\n", d.param_id, bytesrecinfo);
							}
						}
						else if (strncmp(d.param_id, "S_FOCUS_MODE", strlen("S_FOCUS_MODE")) == 0) {
							//selected_cam_enum = std::clamp(selected_cam_enum,  SDK::CrFocus_MF, SDK::CrFocus_PF);
							ss_stream << enumerate_focus_sony_a7(selected_cam_enum);
							int bytesrecinfo = sendParamValue(g_sys_id, g_camId_photo, d.param_id, d.param_value, 5, 8);;
							ss_stream >> s_cam_enum;
							if (camera->SetFocusModeArgs(s_cam_enum) == 1)
							{
								//int bytesrecinfo = sendParamValue(d.param_id, d.param_value, 5, 8);;
								printf("Set PARAM_SET for %s info bytes sent %u\n", d.param_id, bytesrecinfo);
							}
						}
						break;
					}

					 case MAVLINK_MSG_ID_RC_CHANNELS:
					 {
						 mavlink_rc_channels_t RC_In2;
						 mavlink_msg_rc_channels_decode(&msg, &RC_In2);
						 printf("boot = %u", RC_In2.time_boot_ms);
						 printf("RC chancount %u:-\n", static_cast<uint16_t>(RC_In2.chancount));
						 printf("RC CH 9 IN %u:-\n", RC_In2.chan9_raw);
						 printf("RC CH 10 IN %u:-\n", RC_In2.chan10_raw);
						 printf("RC CH 11 IN %u:-\n", RC_In2.chan11_raw);
						 printf("RC CH 12 IN %u:-\n", RC_In2.chan12_raw);
						 printf("RC RSSI %u:-\n", static_cast<uint16_t>(RC_In2.rssi));
						 if (RC_In2.chan10_raw >= 1200)
						 {
							 printf("\t\t********* RC CH IN 10 > 1200********\n");
						 }
						 check_change_mode(&camera_chan_obj, RC_In2.chan12_raw);               // set the mode from the servo signal
						 check_focus_adjust(&camera_chan_obj, RC_In2.chan11_raw, RC_In2.chan10_raw, g_status_txt_cnt, g_sys_id); // now do the action
						 cli::tout << " mode " << camera_chan_obj.hw_def_mode << "\n";
#if defined(LINUX_SERIAL)
						 if (camera_chan_obj.hw_def_mode == modGimbal) sendServoRawToSerial(g_sys_id, MAV_COMP_ID_GIMBAL, 0, camera_chan_obj.rc10_gim_out, camera_chan_obj.rc11_gim_out, 0, 1, fd);
#elif defined(BOOST_SERIAL)
						 if (camera_chan_obj.hw_def_mode == modGimbal) sendServoRawToSerial(g_sys_id, MAV_COMP_ID_GIMBAL, 0, camera_chan_obj.rc10_gim_out, camera_chan_obj.rc11_gim_out, 0, 1);
#else
						 if (camera_chan_obj.hw_def_mode == modGimbal) sendServoRawToSocket(g_sys_id, MAV_COMP_ID_GIMBAL, 0, camera_chan_obj.rc10_gim_out, camera_chan_obj.rc11_gim_out, 0, 1);
#endif
						 if (camera_chan_obj.use_sdk_shut != camera_chan_obj.prev_sdk_shut) {
							 raw_ss_val = get_shutter_from_index_pl(poss_shutter_speeds, &camera_chan_obj);
							 std::uint32_t enum_ss = enumerate_shutter_sony_a7(raw_ss_val);
							 camera->SetShutterSpeedArgsInt(enum_ss);
						 }
						 if (camera_chan_obj.use_sdk_iso != camera_chan_obj.prev_sdk_iso) {
							 raw_iso_val = get_Iso_from_index_pl(poss_Iso, &camera_chan_obj);
							 std::uint32_t enum_iso = enumerate_iso_sony_a7(raw_iso_val);
							 camera->SetIsoArgsInt(enum_iso);
						 }
						 if (camera_chan_obj.use_sdk_fnum != camera_chan_obj.prev_sdk_fnum) {
							 raw_fnum_val = get_FNum_from_index_pl(poss_FNumbers, &camera_chan_obj);
							 std::uint32_t enum_fnum = enumerate_aperture_sony_a7(raw_fnum_val);
							 camera->SetApertureArgsInt(enum_fnum);
						 }

						 // =========== this is the code for enumerting the herelink for focus near far ==============
	                     //
						 if (camera_chan_obj.use_focus_setting != camera_chan_obj.prev_focus_setting) {
							 //camera->SetNearFarEnable(static_cast<SDK::CrCommandParam>(camera_chan_obj.use_focus_setting));
							 camera->set_focus_position(static_cast<SDK::CrCommandParam>(camera_chan_obj.use_focus_setting));
							 camera_chan_obj.prev_focus_setting = camera_chan_obj.use_focus_setting;
						 }
					}
					break;

					case MAVLINK_MSG_ID_SERVO_OUTPUT_RAW:
					{
						mavlink_servo_output_raw_t RC_Out;
						mavlink_msg_servo_output_raw_decode(&msg, &RC_Out);
						if (RC_Out.servo9_raw >= 1200)
						{
							printf("\t\t********* RC Trigger Camera********\n");
							camera->capture_image();
						}
						cli::tout << "channel 9 : " << RC_Out.servo9_raw << "\n";
						cli::tout << "channel 10 : " << RC_Out.servo10_raw << "\n";
						cli::tout << "channel 11 : " << RC_Out.servo11_raw << "\n";
					}
					break;

					default:
						if (msg.sysid == 242)
						{
							printf("\n$$$$Message ID $$$$ %u\n", msg.msgid);
						}
						break;
					}
				}
				else {
					//printf("\nElse Part: Received other packet: SYS: %d, COMP: %d, LEN: %d, MSG ID: %d\n", msg.sysid, msg.compid, msg.len, msg.msgid);
				}
			}
			// printf("\n");
		}
		memset(buf, 0, BUFFER_LENGTH);
		// sleep(1); // Sleep one second
	}
}

/* QNX timer version */
#if (defined __QNX__) | (defined __QNXNTO__)
uint64_t microsSinceEpoch()
{

	struct timespec time;

	uint64_t micros = 0;

	clock_gettime(CLOCK_REALTIME, &time);
	micros = (uint64_t)time.tv_sec * 1000000 + time.tv_nsec / 1000;

	return micros;
}
#else
uint64_t microsSinceEpoch()
{

	struct timeval tv;

	uint64_t micros = 0;

	gettimeofday(&tv, NULL);
	micros = ((uint64_t)tv.tv_sec) * 1000000 + tv.tv_usec;

	return micros;
}
#endif