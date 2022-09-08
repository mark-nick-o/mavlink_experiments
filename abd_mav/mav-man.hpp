#include "mav-com-defs.h"
#include "mavlink.h"
#include "ardupilotmega.h"

 bool print_heart = false;
 bool print_attitude = false;
 uint system_ID = 1;
 int heart_system_ID = 0;
 bool Mission_Planner_Detected =false;
 bool QGC_Detected = false;

static timespec auth_request_timeout;
static timespec heartbeat_timeout;
mavlink_heartbeat_t heartbeat{};
static uint8_t target_system;
static uint16_t mission_item_count;
static bool mission_valid;
static uint16_t first_mission_item_invalid;
mavlink_attitude_t attitude;
static void handle_new_message(const mavlink_message_t *msg, bool *heart);
void handle_heartbeat(const mavlink_message_t *msg, bool *heart);
int process_mavlink(int _socket_fd);

// contains the values returned from the camera
std::tuple<std::string, std::int8_t, std::uint32_t> GetStillCapMode("notset", 0, 0);
std::tuple<std::string, std::int8_t, std::uint32_t> GetAperture("notset", 0, 0);
std::tuple<std::string, std::int8_t, std::uint32_t> GetExposureMode("notset", 0, 0);
std::tuple<std::string, std::int8_t, std::uint32_t> GetIso("notset", 0, 0);
std::tuple<std::string, std::int8_t, std::uint32_t> GetShutterSpeed("notset", 0, 0);
std::tuple<std::string, std::int8_t, std::uint32_t> GetWhiteBalance("notset", 0, 0);
std::tuple<std::string, std::int8_t, std::uint32_t> GetFocusArea("notset", 0, 0);
std::tuple<std::string, std::int8_t, std::uint32_t> GetFocusMode("notset", 0, 0);
// make a union to convert types
//
union float_integer_u {
	std::uint32_t i;
	float f;
	std::uint64_t l;
	double d;
};
union float_integer_u type_convert_union;

int process_mavlink(int _socket_fd)
{    
    socklen_t addrlen = sizeof(sockaddr);
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    mavlink_message_t msg;
    mavlink_status_t status;
    ssize_t n = recvfrom(_socket_fd, buf, sizeof(buf), 0, (struct sockaddr *)&sockaddr, &addrlen);
    if(n == -1) 
    {
        if ((errno == EINTR) || (errno==EAGAIN)) {
            // This was commented out why ?? explantion is below continue;
            // When this event occurs, the calling code must check the EINTR return code and restart the call. One way to do this is to create a simple wrapper function () so that the application calls the appropriate wrapper.open_safe
            // EAGAIN = too many processes or there is a temporary memory shortage so do --->
            // If it occurs repeatedly after running again, stop unnecessary processes
        }
        else 
           fprintf(stderr, "Error reading socket (%m) %u\n",errno); 
        return 1;       
    }

    // Precess the messages
    for (int i = 0; i < n; ++i) 
    {
        if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status)) 
        {
            handle_new_message(&msg, &heart);
        }
    }    
        
        
}  

static int msg_send(mavlink_message_t *msg);

static int msg_send(mavlink_message_t *msg)
{
    uint8_t data[MAVLINK_MAX_PACKET_LEN];

    uint16_t len = mavlink_msg_to_send_buffer(data, msg);
    return sendto(server_socket_fd, data, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}

static void command_ack_send(mavlink_command_ack_t *ack);

static void command_ack_send(mavlink_command_ack_t *ack)
{
    mavlink_message_t msg;
    mavlink_msg_command_ack_encode(SYSTEM_ID, MAV_COMP_ID_ALL, &msg, ack);
    msg_send(&msg);
}


static void handle_command_long(const mavlink_message_t *msg, mavlink_command_long_t *cmd);

static void handle_command_long(const mavlink_message_t *msg, mavlink_command_long_t *cmd)
{

}

static void handle_new_message(const mavlink_message_t *msg, bool *heart)
{
   // printf("> MSG Received %u from System %u Component %u\n",msg->msgid,msg->sysid ,msg->compid);
    switch (msg->msgid) {
        
        case MAVLINK_MSG_ID_HEARTBEAT:
             handle_heartbeat(msg,heart);
        break;
    
        //break;
         case MAVLINK_MSG_ID_COMMAND_LONG:
           printf("********************MAV_CMD_REQUEST_MESSAGE**************");
           mavlink_command_long_t LN_IN;
           mavlink_msg_command_long_decode(msg, &LN_IN);
           printf("Command Long cmd=%u p1=%f",LN_IN.command, LN_IN.param1);
           break;     

        case MAVLINK_MSG_ID_SERVO_OUTPUT_RAW:
             mavlink_servo_output_raw_t RC_Out;
             mavlink_msg_servo_output_raw_decode(msg, &RC_Out);
             //printf("SERVO CH 9 OUT %u:-\n",RC_Out.servo9_raw);
             if(RC_Out.servo9_raw >= 1200)
             {
               printf( "\t\t********* RC Trigger Camera********\n");  
             }
            break;

        //  break; 
       //case MAVLINK_MSG_ID_RC_CHANNELS_RAW: 
       //                                                                =================== This was the old message =========================
       //      mavlink_rc_channels_raw_t RC_In;
       //      mavlink_msg_rc_channels_raw_decode(msg, &RC_In);
       //      printf("RC CH 10 IN %u:-\n",RC_In.chan10_raw);
       //      if(RC_In.chan10_raw>= 1200)
       //      {
       //        printf( "\t\t********* RC CH IN 10 > 1200********\n");  
       //      }
       //     break;

       case MAVLINK_MSG_ID_RC_CHANNELS:
             mavlink_rc_channels_t RC_In;
             mavlink_msg_rc_channels_decode(msg, &RC_In);
			 printf("boot = %u\n", RC_In.time_boot_ms);
			 printf("RC chancount %u:-\n", static_cast<uint16_t>(RC_In.chancount));
			 printf("RC CH 9 IN %u:-\n", RC_In.chan9_raw);
			 printf("RC CH 10 IN %u:-\n", RC_In.chan10_raw);
			 printf("RC CH 11 IN %u:-\n", RC_In.chan11_raw);
			 printf("RC CH 12 IN %u:-\n", RC_In.chan12_raw);
			 printf("RC RSSI %u:-\n", static_cast<uint16_t>(RC_In.rssi));
             if(RC_In.chan10_raw>= 1200)
             {
               printf( "\t\t********* RC CH IN 10 > 1200********\n");  
            }
            break;

//        case MAVLINK_MSG_ID_RC_CHANNELS:
//            mavlink_rc_channels_t RC_In2;
//             mavlink_msg_rc_channels_decode(msg, &RC_In2);
//            printf("boot = %u",RC_In2.time_boot_ms);
//             printf("RC chancount %u:-\n",static_cast<uint16_t>(RC_In2.chancount));
//             printf("RC CH 9 IN %u:-\n",RC_In2.chan9_raw);
//             printf("RC CH 10 IN %u:-\n",RC_In2.chan10_raw);
//             printf("RC CH 11 IN %u:-\n",RC_In2.chan11_raw);
//             printf("RC RSSI %u:-\n",static_cast<uint16_t>(RC_In2.rssi));
//             if(RC_In2.chan10_raw>= 1200)
//             {
//               printf( "\t\t********* RC CH IN 10 > 1200********\n");  
//             }
//             break;

        default:
            //printf("message unspecified seen %u\n",msg->msgid);
            break;
    }
        switch (msg->sysid) {
        // case 200:
        //      if(!Mission_Planner_Detected)
        //      {
        //         printf("Mission Planner\n");
        //         Mission_Planner_Detected = true;
        //      }
        // break;
        case 250 | 200:
             if(!QGC_Detected)
             {   
                printf("QGC %u:-\n"
                        "\tMessage ID %u\n"
                        ,
                        msg->sysid,msg->msgid);
                        QGC_Detected = true;
             }

            if(msg->msgid == 76) 
            {printf("*******COMMAND LONG*********\n");
            mavlink_command_long_t command;
           // uint param1 = command.param1;
            mavlink_msg_command_long_decode(msg, &command);
            printf( "\tPeram 1: - %f\n"
                    "\tPeram 2: -%f\n"
                    "\tPeram 3: -%f\n"
                    "\tPeram 4: -%f\n"
                    "\tPeram 5: -%f\n"
                    "\tPeram 6: -%f\n"
                    "\tPeram 7: -%f\n"
                    "\tCommand %u\n"
                    "\tTarget Component: -\n"
                    "\tTarget System: -: -\n"
                    ,command.param1,command.param2,command.param3,command.param4,command.param5,command.param5,command.param7,command.command);
             if (command.command == MAV_CMD_DO_DIGICAM_CONTROL)
             {
                 printf( "\t\t********* MAVLINK Trigger Camera********\n");
             }
             
            mavlink_message_t msg_out;
            mavlink_statustext_t status_msg;
            status_msg.text[0]='S';
            status_msg.text[1]='o';
            status_msg.text[2]='n';
            status_msg.text[3]='y';
            status_msg.text[4]=' ';
            status_msg.text[5]='T';
            status_msg.text[6]='r';
            status_msg.text[7]='i';
            status_msg.text[8]='g';
            status_msg.text[9]='g';
            status_msg.text[10]='e';
            status_msg.text[11]='r';
            mavlink_msg_statustext_encode(system_ID,COMPONENT_ID,&msg_out,&status_msg);
            msg_send(&msg_out);

             mavlink_command_ack_t command_ack;

            command_ack.command = command.command;
            command_ack.result = MAV_RESULT_ACCEPTED;
            mavlink_msg_command_ack_encode(system_ID, COMPONENT_ID,&msg_out,&command_ack);
            msg_send(&msg_out);

            }
            

        break;
       
        if(msg->sysid == system_ID)
        {
           printf( "\t***********FMU**********\n" );


        }
    }
}

/* return > 0 if t1 is greater, return < 0 if t2 is greater or 0 otherwise */
static long int timespec_compare(timespec *t1, timespec *t2);

static long int timespec_compare(timespec *t1, timespec *t2)
{
    long int r = t1->tv_sec - t2->tv_sec;
    if (r) {
        return r;
    }

    return t1->tv_nsec - t2->tv_nsec;

    
}

void handle_heartbeat(const mavlink_message_t *msg, bool *heart)
{
            if(!*heart || print_heart)
           {
            
            mavlink_msg_heartbeat_decode(msg, &heartbeat);
            printf("HEARTBEAT:\n"
                  "\tmavlink_version: %u\n"
                  "\ttype: %u\n"
                  "\tfrom system %u\n"
                  "\tcomponent %u \n"
                  ,
                heartbeat.mavlink_version,
                heartbeat.type,msg->sysid,msg->compid);
                heart_system_ID = msg->sysid;
                *heart = true;
           }
}

static void SendComRequestSERVO_OUTPUT_RAWInterval (uint8_t target_sys, uint8_t target_comp, float rate);

static void SendComRequestSERVO_OUTPUT_RAWInterval (uint8_t target_sys, uint8_t target_comp, float rate)
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
  command.target_system    = target_sys;
  command.target_component = target_comp;
  command.command          = MAV_CMD_SET_MESSAGE_INTERVAL;
  //command.confirmation     = target_comp;
  command.param1           = (float)(MAVLINK_MSG_ID_SERVO_OUTPUT_RAW);                       
  command.param2           = rate;                                                // 10 Hz
  /* encode */
  mavlink_msg_command_long_encode(target_sys, target_comp, &msg, &command);

  /* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
  msg_send(&msg);
  std::cout<<"> Requesting Servo Data\n";
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
static void requestDataStream(uint8_t target_sys, uint8_t target_comp, uint8_t stream_id, uint8_t state, uint16_t rate);

static void requestDataStream(uint8_t target_sys, uint8_t target_comp, uint8_t stream_id, uint8_t state, uint16_t rate)
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
  command.message_rate    = rate;
  command.stream_id = stream_id;
  command.on_off = state;

  /* encode */
  mavlink_msg_data_stream_encode(target_sys, target_comp, &msg, &command);

  /* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
  msg_send(&msg);
  std::cout<< "> Data Stream Request Made" << static_cast<uint16_t>(stream_id) << std::endl;
}

static void Set_msg_Interval(uint8_t target_sys, uint8_t target_comp, float rate, int16_t cmd);

static void Set_msg_Interval(uint8_t target_sys, uint8_t target_comp, float rate, int16_t cmd)
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
  command.target_system    = target_sys;
  command.target_component = target_comp;
  command.command          = MAV_CMD_SET_MESSAGE_INTERVAL;
  //command.confirmation     = target_comp;
  command.param1           = static_cast<float>(cmd);                       
  command.param2           = rate;                                                // 10 Hz
  //command.param7           = 2.0f;                                                // broadcast
  command.param7           = 0.0f;                                                // broadcast
  /* encode */
  mavlink_msg_command_long_encode(target_sys, target_comp, &msg, &command);

  /* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
  msg_send(&msg);
  std::cout<<"> set interval for msg " << cmd << std::endl;
}

static void SendComRequest_RC_CHANNELS_RAW (uint8_t target_sys, uint8_t target_comp, float rate);

static void SendComRequest_RC_CHANNELS_RAW (uint8_t target_sys, uint8_t target_comp, float rate)
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
  command.target_system    = target_sys;
  command.target_component = target_comp;
  command.command          = MAV_CMD_SET_MESSAGE_INTERVAL;
  //command.confirmation     = target_comp;
  command.param1           = (float)(MAVLINK_MSG_ID_RC_CHANNELS_RAW);                       
  command.param2           = rate;                                                // 10 Hz
  command.param7           = 2.0f;  
  /* encode */
  //mavlink_msg_command_long_encode(target_sys, target_comp, &msg, &command);
  mavlink_msg_command_long_encode(target_sys, 100, &msg, &command);
  /* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
  msg_send(&msg);
  printf( "Requesting MAVLINK_MSG_ID_RC_CHANNELS_RAW Data, Target_sys %u, Targer Component, %u \n",target_sys,target_comp ) ;
}

static void SendComRequest_RC_CHANNELS(uint8_t target_sys, uint8_t target_comp, float rate)
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
  command.target_system    = target_sys;
  command.target_component = target_comp;
  command.command          = MAV_CMD_SET_MESSAGE_INTERVAL;
  //command.confirmation     = target_comp;
  command.param1           = (float)(MAVLINK_MSG_ID_RC_CHANNELS);                       
  command.param2           = rate;                                                // 10 Hz
  command.param7           = 2.0f;  
  /* encode */
  //mavlink_msg_command_long_encode(target_sys, target_comp, &msg, &command);
  mavlink_msg_command_long_encode(target_sys, 100, &msg, &command);
  /* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
  msg_send(&msg);
  printf( "Requesting MAVLINK_MSG_ID_RC_CHANNELS Data, Target_sys %u, Targer Component, %u \n",target_sys,target_comp ) ;
}

static void GetOneShot_Long(uint8_t target_sys, uint8_t target_comp, std::uint16_t cmd);

static void GetOneShot_Long(uint8_t target_sys, uint8_t target_comp, std::uint16_t cmd)
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
  command.target_system    = target_sys;
  command.target_component = target_comp;
  command.command          = MAV_CMD_REQUEST_MESSAGE;
  //command.confirmation     = target_comp;
  command.param1           = static_cast<float>(cmd);                       
  command.param2           = 0.0f; 
  command.param3           = 0.0f; 
  command.param4           = 0.0f; 
  command.param5           = 0.0f;              
  command.param7           = 2.0f;                                   
  /* encode */
  //mavlink_msg_command_long_encode(target_sys, target_comp, &msg, &command);
  mavlink_msg_command_long_encode(target_sys, 100, &msg, &command);
  /* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
  msg_send(&msg);
  printf( "One Shot........ %f, Target_sys %u, Target Component, %u \n",command.param1, target_sys, target_comp ) ;
}

static void SendComRequestAtitideInterval (uint8_t target_sys, uint8_t target_comp, float rate);

static void SendComRequestAtitideInterval (uint8_t target_sys, uint8_t target_comp, float rate)
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
  uint16_t len=0u;


  mavlink_command_long_t com = { 0u };                                          // Command Type
  mavlink_message_t message;                                                    // encoder type
  uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN];

  com.target_system    = target_sys;
  com.target_component = target_comp;
  com.command          = MAV_CMD_SET_MESSAGE_INTERVAL;
  com.confirmation     = 0;
  com.param1           = 30.0f;                                                 // mavlink_attitude_t
  com.param2           = rate;                                                // 10 Hz
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, target_comp, &message, &com);

  /* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
  msg_send(&message);
  std::cout<<"> Requesting Attitude Data\n";
}

void send_sony_connected();

void send_sony_connected()
{
            std::cout<<"Setup Complete\n\n";  
            mavlink_message_t msg_out;
            mavlink_statustext_t status_msg;
            status_msg.text[0]='S';
            status_msg.text[1]='o';
            status_msg.text[2]='n';
            status_msg.text[3]='y';
            status_msg.text[4]=' ';
            status_msg.text[5]='C';
            status_msg.text[6]='o';
            status_msg.text[7]='n';
            status_msg.text[8]='e';
            status_msg.text[9]='c';
            status_msg.text[10]='t';
            status_msg.text[11]='e';
            status_msg.text[11]='d';
            mavlink_msg_statustext_encode(system_ID,COMPONENT_ID,&msg_out,&status_msg);
            msg_send(&msg_out);
}
#include "mav_cmd_lib_1.hpp"