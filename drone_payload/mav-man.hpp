#include "mav-com-defs.h"
//#include "mavlink.h"
#include "libs/mavlink2C/common/mavlink.h"
#include "libs/mavlink2C/ardupilotmega/ardupilotmega.h"

 bool print_heart = false;
 bool print_attitude = false;


static timespec auth_request_timeout;
static timespec heartbeat_timeout;

static uint8_t target_system;
static uint16_t mission_item_count;
static bool mission_valid;
static uint16_t first_mission_item_invalid;
mavlink_attitude_t attitude;
static void handle_new_message(const mavlink_message_t *msg, bool *heart);
int read_mav(int _socket_fd)
        {    
            socklen_t addrlen = sizeof(sockaddr);
            uint8_t buf[MAVLINK_MAX_PACKET_LEN];
            mavlink_message_t msg;
            mavlink_status_t status;
            ssize_t n = recvfrom(_socket_fd, buf, sizeof(buf), 0, (struct sockaddr *)&sockaddr, &addrlen);
            if(n == -1) 
                {
                    if ((errno == EINTR) || (errno==EAGAIN)) {
                    //    continue;
                    }
                    else
                    fprintf(stderr, "Error reading socket (%m)\n");        
                }

                    // Precess the messages
                    for (int i = 0; i < n; i++) 
                    {
                        if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status)) 
                        {
                            handle_new_message(&msg,&heart);
                        }
                    }    
        
        
        }  


static int msg_send(mavlink_message_t *msg)
{
    uint8_t data[MAVLINK_MAX_PACKET_LEN];

    uint16_t len = mavlink_msg_to_send_buffer(data, msg);
    return sendto(server_socket_fd, data, len, 0, (struct sockaddr *)&sockaddr, sizeof(sockaddr));
}

static void command_ack_send(mavlink_command_ack_t *ack)
{
    mavlink_message_t msg;
    mavlink_msg_command_ack_encode(SYSTEM_ID, MAV_COMP_ID_ALL, &msg, ack);
    msg_send(&msg);
}



static void handle_command_long(const mavlink_message_t *msg, mavlink_command_long_t *cmd)
{

}





static void handle_new_message(const mavlink_message_t *msg, bool *heart)
{
    printf("> MSG Received %u \n",msg->msgid);
    switch (msg->msgid) {
        
        case MAVLINK_MSG_ID_HEARTBEAT:
        if(!*heart || print_heart)
           {
            mavlink_heartbeat_t heartbeat{};
            mavlink_msg_heartbeat_decode(msg, &heartbeat);
                    printf("HEARTBEAT:\n"
                "\tmavlink_version: %u\n"
                "\ttype: %u\n",
                heartbeat.mavlink_version,
                heartbeat.type);
                *heart = true;
           }
        break;

        case MAVLINK_MSG_ID_ATTITUDE:
             mavlink_msg_attitude_decode(msg,&attitude);
             if(print_attitude)
             printf("Attitude:\n"
                    "\tPitch: %f Pitch Speed: %f\n"
                    "\tRoll : %f Roll Speed : %f\n"
                    "\tYaw  : %f Yaw Speed  : %f\n",
                    attitude.pitch,
                    attitude.pitchspeed,
                    attitude.roll,
                    attitude.rollspeed,
                    attitude.yaw,
                    attitude.yawspeed
                    );     
        break;
    //default:
        break;
    }
}

/* return > 0 if t1 is greater, return < 0 if t2 is greater or 0 otherwise */
static long int timespec_compare(timespec *t1, timespec *t2)
{
    long int r = t1->tv_sec - t2->tv_sec;
    if (r) {
        return r;
    }

    return t1->tv_nsec - t2->tv_nsec;

    
}

static void SendComRequestAtitideInterval (uint8_t target_sys, uint8_t target_comp)
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
  com.param2           = 100000;                                                // 10 Hz
  /* encode */
  len = mavlink_msg_command_long_encode(target_sys, target_comp, &message, &com);

  /* Copy the message to send buffer when buf is uint8_t buf[MAVLINK_MSG_ID_COMMAND_LONG_LEN]; */
  msg_send(&message);
  std::cout<<"> Requesting Attitude Data\n";
}