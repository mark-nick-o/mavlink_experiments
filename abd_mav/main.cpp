//Branch
#define VER ">>    Socker-Class-Working > on to mavheart    <<"

#define AUTHORIZATION_TIMEOUT_SEC 60
/* INCLUDES */
#include "defs.hpp"
#include <iostream>
#include <map>
#include <vector>
#include <unistd.h>
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/socket.h>
#include <time.h>
#include "mavlink.h"
#include "/usr/include/libexplain/socket.h" // Socket error description
#include <stdlib.h>
#include "mav.hpp"
#include <sys/types.h> 
#include <netinet/in.h>
#include "arg-man.hpp"

#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <sys/time.h>

// for memset_s if we have it.
#define __STDC_WANT_LIB_EXT1__ 1
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static int server_socket_fd;
static int local_socket_fd;
static struct sockaddr_in sockaddr;
bool heart = false;
static volatile bool g_should_exit;
int g_en = 0;
int g_st = 0;

#include "mav-man.hpp"

void error(const char *msg)
{
    perror(msg);
    exit(1);
}

static void exit_signal_handler(int signum)
{
    // if(signum == SIGINT)
    //    {paus= true;}
//else
    {
        std::cout<<std::endl<<"Signum " <<signum <<" "; 
        std::cout<<"Exception handler closing socket"<<std::endl;        
        close(server_socket_fd);
        g_should_exit = true;
        _exit(EXIT_FAILURE);
    }
}

static void setup_signal_handlers()
{
    struct sigaction sa = { };
    std::cout<<"> Setting up signal handlers"<<std::endl;
    sa.sa_flags = SA_NOCLDSTOP;
    sa.sa_handler = exit_signal_handler;
    #if defined(_MSC_VER)
         //Allow floating-point exceptions
        _control87( 0, _MCW_EM );
    #endif
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT, &sa, NULL); 
    sigaction(SIGQUIT,&sa, NULL);
    sigaction(SIGFPE,&sa,NULL);
    sigaction(SIGHUP,&sa,NULL);
    /* we are using alarm for timer so surpress it here sigaction(SIGALRM,&sa,NULL ); */
    sigaction(SIGSEGV,&sa,NULL); 
    sigaction(SIGTSTP,&sa,NULL);   
}

static void heartbeat_time()
{
        mavlink_heartbeat_t heartbeat;
        mavlink_message_t msg;
        timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);

        /* send heartbeat at 0.333 hz */
        if (timespec_compare(&now, &heartbeat_timeout) > 0) {
            g_st = clock();
            std::cout << "send Heart-beat : " << (g_st-g_en)/double(CLOCKS_PER_SEC)*1000.0f << std::endl;
            heartbeat.type = MAV_TYPE_CAMERA;
            heartbeat.autopilot = MAV_AUTOPILOT_INVALID;
            heartbeat.base_mode = 0;
            heartbeat.custom_mode = 0;
            heartbeat.system_status = MAV_STATE_ACTIVE;
            heartbeat.mavlink_version = 2;
            mavlink_msg_heartbeat_encode(system_ID, COMPONENT_ID, &msg, &heartbeat);
            msg_send(&msg);

            heartbeat_timeout.tv_sec = now.tv_sec + HEARTBEAT_TIMEOUT_SEC;
            heartbeat_timeout.tv_nsec = now.tv_nsec;
            g_en = clock();
            std::cout << "heartbeat took : " << (g_en-g_st)/double(CLOCKS_PER_SEC)*1000.0f << "\n";
        }    
}


/***************************************************************************************************************************************************/
/***************************************************************************************************************************************************/
/***************************************************************************************************************************************************/
/***************************************************************************************************************************************************/

// disable the raw Channel message periodically to prevent Mission Planner starting and resetting the update for the unwanted message
//
void alrm( int signo )
{
    // set slow rate on servo output
    int st = clock();
    //SendComRequestSERVO_OUTPUT_RAWInterval(system_ID, 0, 1000000000000000.0f);
    //SendComRequest_RC_CHANNELS(system_ID, 1, 1000000.0f);
    int en = clock();
    std::cout << "action time from alarm handler : " << (en-st)/double(CLOCKS_PER_SEC)*1000.0f << "\n";
    // this would stop the RC_CHAN message SendComRequest_RC_CHANNELS(system_ID, 0, 1000000000000000.0f); 
}

int main(int argc, char * argv[])
{   
    std::cout<<std::endl<<std::endl<<VER<<std::endl<<std::endl<<std::endl;  
    argc_man(argc,argv); 
    sleep(1);
    bool setup = false;
    mavlink_message_t mav_msg;
    heartbeat_timeout.tv_sec = 0;
    heartbeat_timeout.tv_nsec = 0;
    heartbeat.autopilot = MAV_AUTOPILOT_INVALID;
    print_heart = arg.d_heart;
 
    mavlink_status_t status;
    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    socklen_t addrlen = sizeof(sockaddr);
    uint8_t sen_q;
    setup_signal_handlers();       // clean-up on kill 
    // set up poll action timer to keep unwanted messages out
    // at present when Mission Planner is connected it resets the SErvo RAW frequency message
    // therefore we time an action every RAW_STOP_SECS to supress it
    //
    const uint16_t RAW_STOP_SECS = 15u;
    struct sigaction sa_alarm;
    struct itimerval itimer;
    // MSC06-C suggests use memset_s rather than memset we dont seem to have it though
    #ifdef __STDC_LIB_EXT1__
        memset_s(& sa_alarm, sizeof (sa_alarm), 0, sizeof (sa_alarm));
    #else
        memset(&sa_alarm, 0, sizeof (sa_alarm));
    #endif
    sa_alarm.sa_handler = alrm;
    sa_alarm.sa_flags = SA_RESTART;
    if (sigaction (SIGALRM, & sa_alarm, NULL) <0) {
      perror("sigaction");
      exit (1);
    }
    itimer.it_value.tv_sec = itimer.it_interval.tv_sec = RAW_STOP_SECS;
    itimer.it_value.tv_usec = itimer.it_interval.tv_usec = 0;
    if (setitimer(ITIMER_REAL, &itimer, NULL) < 0) {
        perror("set timer");
        exit (1);
    }

    ssize_t n = recvfrom(server_socket_fd, buf, sizeof(buf), 0, (struct sockaddr *)&sockaddr, &addrlen);

    mlr::local_client_socket mavlink_router_server(true,arg.mavrout_TCP,arg.c_mavrout_IP,arg.mavrout_port,arg.non_block);
    server_socket_fd = mavlink_router_server.socket_fd;

    float x = 0;
    std::cout<<"Listening for a vehical heartbeat\n";
    while (!setup) 
    {
    // Adopt Vehical System ID
    
    process_mavlink(mavlink_router_server.socket_fd);
    heart = false;
    if(heartbeat.autopilot !=  MAV_AUTOPILOT_INVALID)                                           // Did we get a hearbeat from a Autopilot (Vehical)?
    {
        std::cout<<"Vehical Detected\n";
        system_ID = heart_system_ID;
        printf("\t Adopting system ID:- %i\n",heart_system_ID);
        send_sony_connected();
        setup = true;
        // reference to this link https://github.com/mavlink/qgroundcontrol/blob/master/src/FirmwarePlugin/APM/ArduSubFirmwarePlugin.cc
        //
       // requestDataStream(system_ID, 0, MAV_DATA_STREAM_RC_CHANNELS, 1,  2);
    }
 }
 
// Main loop
while (!g_should_exit) 
{
   heartbeat_time();
   process_mavlink(mavlink_router_server.socket_fd);
   // because Mission Planner then increase the frequency periodically stop the message (incase mp started-up)
}

 connect_error:
    std::cout<<"Closing Server Socket\n";
    close(server_socket_fd);
    return -1;
}
