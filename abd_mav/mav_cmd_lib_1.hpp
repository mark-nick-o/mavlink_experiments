/* new commands library for mavlink */
#ifndef __mav_cmd_lib_1
#define __mav_cmd_lib_1

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

// default sys id - we get a heartbeat from the master which locks our sys id at initialization
int g_camId_photo = MAV_COMP_ID_CAMERA;                                     // default camera ID will be read from .ini file
std::uint16_t g_recording_state = 0;                                        // global containing the recording state

// flag which says we are not counting this picture
std::uint32_t g_total_pic_count = 0;

MAVPACKED(
typedef struct {
    union {
        float       param_float;
        double      param_double;
        int64_t     param_int64;
        uint64_t    param_uint64;
        int32_t     param_int32;
        uint32_t    param_uint32;
        int16_t     param_int16;
        uint16_t    param_uint16;
        int8_t      param_int8;
        uint8_t     param_uint8;
        uint8_t     bytes[MAVLINK_MSG_PARAM_EXT_SET_FIELD_PARAM_VALUE_LEN];
    };
    uint8_t type;
}) param_ext_union_t;


int g_status_txt_cnt = 0;

static void cam_param_request_list(uint8_t target_sys, uint8_t target_comp);

static void cam_param_request_list(uint8_t target_sys, uint8_t target_comp)
{
	mavlink_message_t msg;

	mavlink_param_request_list_t cprl;
	cprl.target_system = target_sys;
	cprl.target_component = target_comp;
	mavlink_msg_param_request_list_encode(target_sys, target_comp, &msg, &cprl);
	msg_send(&msg);
}


static void mav_send_cam_info_uri(uint8_t target_sys, uint8_t target_comp);

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
	msg_send(&message);
}

std::uint32_t get_uptime();

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

int sendCamInfo(uint8_t target_sys, uint8_t target_comp) ;

int sendCamInfo(uint8_t target_sys, uint8_t target_comp) 
{
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
    printf("Camera Info : %s\n", f.cam_definition_uri);
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));

}

int sendParamExtValue(uint8_t target_sys, uint8_t target_comp, std::string param_id, std::uint32_t param_value, std::uint16_t param_index, std::uint16_t param_count);

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
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}

int sendParamValue(uint8_t target_sys, uint8_t target_comp, std::string param_id, std::float_t param_value, std::uint16_t param_index, std::uint16_t param_count);

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
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}

int sendCameraCaptureStatus(uint8_t target_sys, uint8_t target_comp);

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
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}

int sendCameraStorageInfo(uint8_t target_sys, uint8_t target_comp);

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
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}

int sendCameraSettings(uint8_t target_sys, uint8_t target_comp);

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
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
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

int requestDataStream2(uint8_t target_sys, uint8_t target_comp, uint8_t stream_id, uint8_t state, uint16_t rate);

int requestDataStream2(uint8_t target_sys, uint8_t target_comp, uint8_t stream_id, uint8_t state, uint16_t rate)
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
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}

int sendLongCommandAck(uint8_t target_sys, uint8_t target_comp, std::uint16_t command);

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
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}

int sendSetParamExtAck(uint8_t target_sys, uint8_t target_comp, std::string param_id, std::string param_value, uint8_t type);

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
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}

int sendServoRawToSocket(uint8_t target_sys, uint8_t target_comp, std::uint16_t a1, std::uint16_t a2, std::uint16_t a3, std::uint16_t a4, std::uint8_t p);

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
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}

//#define LINUX_SERIAL
#if defined(LINUX_SERIAL)
int sendServoRawToSerial(std::uint16_t a1, std::uint16_t a2, std::uint16_t a3, std::uint16_t a4, std::uint8_t p, int fd);
int sendServoRawToSerial(std::uint16_t a1, std::uint16_t a2, std::uint16_t a3, std::uint16_t a4, std::uint8_t p, int fd)
#else
int sendServoRawToSerial(uint8_t target_sys, uint8_t target_comp, std::uint16_t a1, std::uint16_t a2, std::uint16_t a3, std::uint16_t a4, std::uint8_t p);
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
	sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
	// 
	// example :: gimbal_cmd.write_byte_array(&buf[0]); 
	//
#endif
	return 1;             // change to send to serial port for gimbal.......
}

int SendComRequestSERVO_OUTPUT_RAWInterval2(uint8_t target_sys, uint8_t target_comp, float rate);

int SendComRequestSERVO_OUTPUT_RAWInterval2(uint8_t target_sys, uint8_t target_comp, float rate)
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
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));

}

int SendComRequest_RC_CHANNELS2(uint8_t target_sys, uint8_t target_comp, float rate);

int SendComRequest_RC_CHANNELS2(uint8_t target_sys, uint8_t target_comp, float rate)
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
	int len = mavlink_msg_command_long_encode(target_sys, target_comp, &msg, &command);
	/* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
	//msg_send(&msg);
	std::uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN];
	len = mavlink_msg_to_send_buffer(buf, &msg);
	printf("Requesting MAVLINK_MSG_ID_RC_CHANNELS Data, Target_sys %u, Targer Component, %u \n", target_sys, target_comp);
	return sendto(server_socket_fd, buf, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}

#endif