
 #ifndef MAV_H
 #define MAV_H

 #include "defs.hpp"
 #include "libs/mavlink2C/common/mavlink.h"
 #include "libs/mavlink2C/common/common.h"
 #include <arpa/inet.h>
 #include <errno.h>
 #include <fcntl.h>
 #include <signal.h>
 #include <stdbool.h>
 #include <stdint.h>
 #include <stdio.h>
 #include <sys/socket.h>
 #include <time.h>
 #include <unistd.h>
 #include <errno.h>
 #include <time.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include "/usr/include/libexplain/socket.h" // Socket error disctrption
#include <time.h>



namespace mlr
{
    // static long int timespec_compare(timespec *t1, timespec *t2)
    // {
    //     long int r = t1->tv_sec - t2->tv_sec;
    //     if (r) {
    //         return r;
    //     }
 
    // return t1->tv_nsec - t2->tv_nsec;
    // }
  
  class local_server_socket

  {
    private:

    public:
        struct socket_stat_t
        {
            bool is_open =0;
            bool is_none_blocking =0;
            bool is_local =0;
            bool is_remote =0;
            char IP_protocal[3];
        };
        char ip[16u];
        int port;
        sockaddr_in sockAddr;
        socket_stat_t info;
        int socket_fd;

      local_server_socket(bool coot = 1,bool tcp =0, char *_ip =0, int _port =5770);
      ~local_server_socket();
  };
  
  local_server_socket::local_server_socket(bool coot,bool tcp, char *_ip, int _port)
  {
      int ret =0;
        int err = errno;
        char err_str[100];
        this->port = _port;
            
            if(tcp)  strcpy(this->info.IP_protocal,"TCP");
            if(!tcp) strcpy(this->info.IP_protocal,"UDP");    
            strcpy(this->ip,_ip);
            this->info.is_local = true;
            this->info.is_remote = false;   


            if(coot)std::cout<<std::endl<<"> Creating Server endpoint socket "<<this->info.IP_protocal<<" "<<this->ip<<": "<<this->port <<std::endl;
            if(tcp) // TCP
            {
                          
                this->socket_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
                if( this->socket_fd  ==-1)
                {            
                    fprintf(stderr, "> Could not create TCP socket (%m)\n");
                    explain_message_socket(err_str,err,AF_INET,SOCK_STREAM, 0);
                    fprintf(stderr, "> Explain messafe error %s\n",err_str) ; 
                    printf("> Set socket port failed\n Goodby\n");
                    close(this->socket_fd );
                    exit(2);                  
                }
            }
            else // This UDP
            {
                std::cout<<"udp"<<std::endl;
                this->socket_fd = socket(AF_INET, SOCK_DGRAM,0);
                if( this->socket_fd  ==-1)
                {            
                    fprintf(stderr, "> Could not create UDP socket (%m)\n");
                    explain_message_socket(err_str,err,AF_INET,SOCK_STREAM, 0);
                    fprintf(stderr, "> Explain messafe error %s\n",err_str) ; 
                    printf("> Set socket port failed\n Goodby\n");
                    close(this->socket_fd );
                    exit(2);  
                }
            }    
 
                
            printf("> Created Server endpoint socket %d %s IP address: %s, Port Number: %d (%m)\n",this->socket_fd,this->info.IP_protocal,this->ip,this->port);
            printf("> Trying to bind the soket %d %s IP address: %s, Port Number: %d\n",this->socket_fd,this->info.IP_protocal,this->ip,this->port);
            memset(&this->sockAddr , 0, sizeof(struct sockaddr_in));
            this->sockAddr.sin_family = AF_INET;
            // sockaddr.sin_addr.s_addr =INADDR_ANY;
            this-> sockAddr.sin_addr.s_addr =  inet_addr(this->ip);
            this->sockAddr.sin_port = htons(_port);          

            ret = bind(this->socket_fd, (struct sockaddr *)&this->sockAddr, sizeof(struct sockaddr_in));
            if (ret)
            {   
                printf("> Binding the soket %d %s IP address: %s, Port Number: %d  failed (%m)\n",this->socket_fd,this->info.IP_protocal,this->ip,this->port);
                exit(1);
            }        
                
            printf("> Binding of socket %d %s IP address: %s, Port Number: %d (%m)\n",this->socket_fd,this->info.IP_protocal,this->ip,this->port);
            if(coot)std::cout <<"> Trying to make socket none-blocking"<<std::endl;
            int block_status =fcntl(this->socket_fd, F_SETFL, fcntl(this->socket_fd, F_GETFL, 0) | O_NONBLOCK);//try to make socket none blocking
            // did we manage to make socket none blocking? 
            printf("> None blocking (%m)\n");
            this->info.is_none_blocking = true;
            if(block_status)
               this->info.is_none_blocking = false;
            if(coot)std::cout <<"> Its all good, we are now a server hosting.\n\n\n";
    }
  
  
  local_server_socket::~local_server_socket()
  {
  }
  
/**************************************************************************************************/
    class local_client_socket

    {
    private:

    public:
        struct socket_stat_t
        {
            bool is_open =0;
            bool is_none_blocking =0;
            bool is_local =0;
            bool is_remote =0;
            char IP_protocal[3];
        };
        char ip[16u];
        int port; 
        sockaddr_in sockAddr;
        socket_stat_t info;
        int socket_fd;
        local_client_socket(bool coot = 1,bool tcp =0, char *_ip =0, int _port =5770,bool block =0);
        ~local_client_socket();
    };
   local_client_socket::local_client_socket(bool coot,bool tcp, char *_ip, int _port,bool block)
    {
       
        int ret =0;
        int err = errno;
        char err_str[100];
        this->port = _port;
            if(tcp)  strcpy(this->info.IP_protocal,"TCP");
            if(!tcp) strcpy(this->info.IP_protocal,"UDP");    
            strcpy(this->ip,_ip);
            this->info.is_local = false;
            this->info.is_remote = true;   

            if(coot)std::cout<<std::endl<<"> Creating endpoint socket to mavlink-router server "<<this->info.IP_protocal<<" "<<this->ip<<": "<<this->port<<std::endl;
        
            if(tcp) // TCP
            {
               this->socket_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
        
                if(this->socket_fd  ==-1)
                {            
                    fprintf(stderr, "> Could not create TCP socket (%m)\n");
                    explain_message_socket(err_str,err,AF_INET,SOCK_STREAM, 0);
                    fprintf(stderr, "> Explain messafe error %s\n",err_str) ; 
                    printf("> Set socket port failed\n Goodby\n");
                    close(this->socket_fd );
                    exit(2);                  
                }
            }
            else // This UDP
            {
                this->socket_fd = socket(AF_INET, SOCK_DGRAM,0);
                if(this->socket_fd  ==-1)
                {            
                    fprintf(stderr, "> Could not create UDP socket (%m)\n");
                    explain_message_socket(err_str,err,AF_INET,SOCK_STREAM, 0);
                    fprintf(stderr, "> Explain message error %s\n",err_str) ; 
                    printf("> Set socket port failed\n Goodby\n");
                    close(this->socket_fd );
                    exit(2);  
                }
            }    
 
                
            printf("> Created endpoint socket to mavlink-router server %d %s IP address: %s, Port Number: %d (%m)\n",this->socket_fd,this->info.IP_protocal,this->ip,this->port);
            printf("> Trying to connect to mavlink-router server on soket %d %s IP address: %s, Port Number: %d\n",this->socket_fd,this->info.IP_protocal,this->ip,this->port);
            memset(&this->sockAddr , 0, sizeof(struct sockaddr_in));
            this->sockAddr.sin_family = AF_INET;
            // sockaddr.sin_addr.s_addr =INADDR_ANY;
            this->sockAddr.sin_addr.s_addr =  inet_addr(this->ip);
            this->sockAddr.sin_port = htons(_port);            
            ret = connect(this->socket_fd, (struct sockaddr *)&this->sockAddr, sizeof(struct sockaddr_in)); 
            if (ret)
            {   
                printf("> Connect to mavlink-router server soket %d %s IP address: %s, Port Number: %d  failed (%m)\n",this->socket_fd,this->info.IP_protocal,this->ip,this->port);
                exit(1);
            }        
                
            printf("> Connect to mavlink-router server soket %d %s IP address: %s, Port Number: %d (%m)\n",this->socket_fd,this->info.IP_protocal,this->ip,this->port);
            
            
            if (block==true)
            {
                if(coot)std::cout <<"> Trying to make socket none-blocking"<<std::endl;
                int block_status =fcntl(this->socket_fd, F_SETFL, fcntl(this->socket_fd, F_GETFL, 0) | O_NONBLOCK);//try to make socket none blocking
                // did we manage to make socket none blocking? 
                
                if(block_status)
                {
                    if(coot)std::cout <<"> None blocking failed"<<std::endl;
                    this->info.is_none_blocking = false;
                }
                else
                {
                    if(coot)std::cout <<"> None blocking sucsessful"<<std::endl;
                    this->info.is_none_blocking = true;
                } 
                if(coot)std::cout <<"> Its all good, we are connected to mavlink-router server.\n\n\n";
            }
            this->info.is_open = true;
    }

    local_client_socket::~local_client_socket()
    {
        this->info.is_open = false;
        std::cout <<"> Distroying socket to server"<<std::endl;
        close(this->socket_fd);
    }

/**************************************************************************************************/
    class remote_target

    {
    private:
        int op;
        struct socket_stat_t
        {bool is_open =0;
        bool is_none_blocking =0;
        bool is_local =0;
        bool is_remote =0;
        char IP_protocal[3];
        };
    public:
        char ip[16u];
        int port;       
        int socket_fd;
        sockaddr_in sockAddr;
        socket_stat_t info;
        remote_target(bool coot = 1,bool tcp = 0,char *_ip =0, int _port =5760);
        ~remote_target();
    };
   remote_target::
   remote_target(bool coot,bool tcp,char *_ip, int _port)
    {
            this->port = _port;
            if(tcp)  strcpy(this->info.IP_protocal,"TCP");
            if(!tcp) strcpy(this->info.IP_protocal,"UDP");  
            strcpy(this->ip,_ip); 
            this->info.is_local = false;
            this->info.is_remote = true;   
            printf("> Created target endpoint %s IP address: %s, Port Number: %d (%m)\n",this->info.IP_protocal,this->ip,this->port);
            if(tcp) //This is TCP 
            this->socket_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
            else
            this->socket_fd = socket(AF_INET, SOCK_DGRAM,0);
            
            memset(&this->sockAddr , 0, sizeof(struct sockaddr_in));
            this->sockAddr.sin_family = AF_INET;
            // sockaddr.sin_addr.s_addr =INADDR_ANY;
            this->sockAddr.sin_addr.s_addr =  inet_addr(this->ip);
            this->sockAddr.sin_port = htons(_port);  
            printf("> Target endpoint socket %d %s IP address: %s, Port Number: %d (%m)\n",this->socket_fd,this->info.IP_protocal,this->ip,this->port);
            printf("> ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ <\n\n");
    }

    remote_target::
    ~remote_target
    ()
    {
    }

/**************************************************************************************************/
    class heartbeat
    {
    private:
    

    public:
        friend class local_client_socket;
        mavlink_message_t heart_msg{};
        mavlink_status_t status{};
        timespec period_time;
        timespec timeout;
        unsigned long long sleep_ms;
        float frequency_hZ;
        int send_heartbeat(mlr::remote_target *_target);
        heartbeat(float  _frequency_hZ);
        ~heartbeat();
        void poop()
        {
            sleep(1);
        }
    };
    heartbeat::heartbeat(float  _frequency_hZ)
    { 
      //#error "to do haert to socket and auto send"
      long double nsec =0 ;
      unsigned int sec = 0;
      this->timeout.tv_sec =0;
      nsec = (1000000000/ _frequency_hZ);
      if(nsec >= 1000000000)
      {
          sec = (nsec / 1000000000);
          nsec -=(1000000000*sec);
      }
      std::cout<< "Heartbeat info for "<<sec<<" seconds and "<<nsec<<"ns"<<std::endl;
    }

    heartbeat::~heartbeat()
    {
    }
 int mlr::heartbeat:: send_heartbeat(mlr::remote_target *_target)


    {
//      timespec time_now;
//      mavlink_message_t msg;
//      uint8_t buf[2041];
//      int bytes_sent =0;
//      mavlink_heartbeat_t heartbeat;
//      uint16_t mav_msg_len =0;
//      clock_gettime(CLOCK_MONOTONIC, &time_now);
//      if (timespec_compare(&time_now, &this->timeout) > 0) 
//         {
// std::cout<<"Send Heart"<<std::endl;
//             int sock_fd = _target->socket_fd;
//             struct sockaddr_in socAddr = _target->sockAddr;          
            
            
//             heartbeat.type = MAV_TYPE_ONBOARD_CONTROLLER;
//             heartbeat.autopilot = MAV_AUTOPILOT_INVALID;
//             heartbeat.base_mode = 0;
//             heartbeat.custom_mode = 0;
//             heartbeat.system_status = MAV_STATE_ACTIVE;
//             mavlink_msg_heartbeat_pack(SYSTEM_ID, COMPONENT_ID, &msg, MAV_TYPE_ONBOARD_CONTROLLER, MAV_AUTOPILOT_GENERIC, MAV_MODE_GUIDED_ARMED, 0, MAV_STATE_ACTIVE,2);
//             mav_msg_len = mavlink_msg_to_send_buffer(buf, &msg);      
//             bytes_sent = sendto(sock_fd, buf, mav_msg_len, 0,(struct sockaddr*)&socAddr ,sizeof(struct sockaddr_in));
//             this->timeout.tv_sec = time_now.tv_sec + HEARTBEAT_TIMEOUT_SEC;
//             this->timeout.tv_nsec = time_now.tv_nsec;
//             }  
//      return bytes_sent;
    }


}// namespect mav


#endif