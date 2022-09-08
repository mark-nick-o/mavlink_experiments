  // Main code exicution argument manager
  
   #ifndef ARG_MAN_HPP
   #define ARG_MAN_HPP
   #include <iostream>  // defines the standard input/output stream objects
   #include <stdio.h>       
                        /* stdio.h >> C library to perform Input/Output operations
                        Input and Output operations can also be performed in C++ using the C Standard Input and Output Library (cstdio, known as 
                        stdio.h in the C language). This library uses what are called streams to operate with physical devices such as keyboards, 
                        printers, terminals or with any other type of files supported by the system. Streams are an abstraction to interact with 
                        these in an uniform way; All streams have similar properties independently of the individual characteristics of the 
                        physical media they are associated with.

                        Streams are handled in the cstdio library as pointers to FILE objects. A pointer to a FILE object uniquely identifies 
                        a stream, and is used as a parameter in the operations involving that stream.
                        There also exist three standard streams: stdin, stdout and stderr, which are automatically created and opened for all 
                        programs using the library.*/


   #include <string.h>  //This header file defines several functions to manipulate C strings and arrays.
   
struct _argval
    {    
        char c_local_type[7];
        bool local_server =true;
        char c_local_protocal[4];
        bool local_TCP = false;  
        char c_local_IP[16u];
        int  local_port = 14560;
              
        char c_mavrout_type[7];
        char c_mavrout_protocol[4];
        bool mavrout_TCP =false;
        char c_mavrout_IP[16u];
        int  mavrout_port = 5760;
        bool mavrout_server =false;
        bool non_block = true;
        bool d_heart = false;
        bool d_atitude = false;
        bool d_gui = false;
        bool d_pose = false;
    };_argval arg;   


void argc_man(int _argc,char *argv[])
 {
        char c_server[]     = "SERVER";
        char c_client[]     = "CLIENT";    
        char c_arg_help[]   = "--help";
        char c_lip[]        = "--lip";
        char c_lpo[]        = "--lpo";
        char c_ltcp[]       = "-ltcp";
        char c_ludp[]       = "-ludp";
        char c_tip[]        = "--mip";
        char c_mpo[]        = "--mpo";
        char c_arg_ttcp[]   = "-mtcp";
        char c_arg_tudp[]   = "-mudp";
        char c_TCP[]        = "TCP";
        char c_UDP[]        = "UDP";
        char c_ls[]         = "-ls";
        char c_lc[]         = "-lc";
        char c_ms[]         = "-ms";
        char c_mc[]         = "-mc";
        char c_block[]      = "-bl";
        char c_heart[]      = "-dh";
        char c_atit[]       = "-da";
        char c_gui[]        = "-gui";
        char c_pose[]       = "-dp";
    /* SETUP DEFAULTS */     
            
        arg.local_server = false;

        arg.local_TCP = true;
        arg.local_port = 14561;
        strcpy(arg.c_local_IP, "127.0.0.1");
        arg.mavrout_server = true;
        arg.mavrout_TCP = true;
        arg.mavrout_port = 5760;
        strcpy(arg.c_mavrout_IP, "127.0.0.1");    //Target IP   
    /* DEFAULTS DONE */   

        if (_argc >= 2) 
        {
                if ((_argc == 2) && (strcmp(argv[1], c_arg_help) == 0))
                {
                    printf("\n");
                    printf("\tUsage for:");
                    printf("%s\n", argv[0]);
                    printf("\t\t -ls Local Server Mode\n");
                    printf("\t\t -lc Local Client Mode\n");
                    printf("\t\t --lip <ip address for local (this) endpoint>\n");
                    printf("\t\t -ludp <Protocall for local is UDP\n");
                    printf("\t\t -ltcp <Protocall for local is TCP\n");
                    printf("\t\t --lpo <port for local (this) endpoint>\n");
                    printf("\t\t -bl <disable none-blocking\n\n");
                    
                    printf("\t\t -ms MAVLINK-ROUTER Server Mode\n");
                    printf("\t\t -mc MAVLINK-ROUTER Client Mode\n");
                    printf("\t\t --mip <ip address for  MAVLINK-ROUTER endpoint>\n");
                    printf("\t\t -mudp <Protocall for  MAVLINK-ROUTER is UDP\n");
                    printf("\t\t -mtcp <Protocall for  MAVLINK-ROUTER is TCP\n");
                    printf("\t\t --mpo <port for  MAVLINK-ROUTER endpoint>\n\n");
                    printf("\t\t Local Default: %s IP address: %s, Port Number:%u\n",arg.c_local_protocal,arg.c_local_IP,arg.local_port);
                    printf("\t\t MAVLINK-ROUTER Default: %s IP address: %s, Port Number:%un\n\n",arg.c_mavrout_protocol,arg.c_mavrout_IP,arg.mavrout_port);
                    printf("\t\t -dh <display heartbeat>\n");
                    printf("\t\t -gui <display GUI>\n");
                    printf("\t\t -da <display FC_Atitude>\n");
                    printf("\t\t -dp <display Pose>\n\n");

                    exit(EXIT_FAILURE);
                }
                // Change the target ip if parameter was given
                std::string::size_type sz;   // alias of size_t
                for (int ind=1; ind<_argc; ind++) 
                {      
                    if (strcmp(argv[ind], c_lc) == 0)
                    {
                        arg.local_server = false;
                    }
                    if (strcmp(argv[ind], c_ls) == 0)
                    {
                        arg.local_server = true;
                    }
                    if (strcmp(argv[ind], c_lip) == 0)
                    {
                        strcpy(arg.c_local_IP, argv[ind+1]);
                    }
                    if (strcmp(argv[ind], c_lpo) == 0)
                    {
                        arg.local_port = std::stoi(argv[ind+1]);
                    }
                    if (strcmp(argv[ind], c_ltcp) == 0)
                    {
                        arg.local_TCP = true;
                        strcpy(arg.c_local_protocal,c_TCP);
                    }
                    if (strcmp(argv[ind], c_ludp) == 0)
                    {
                        arg.local_TCP = false;
                        strcpy(arg.c_local_protocal,c_UDP);
                    }
                    if (strcmp(argv[ind], c_mc) == 0)
                    {
                        arg.mavrout_server = false;
                    }
                    if (strcmp(argv[ind], c_ms) == 0)
                    {
                        arg.mavrout_server = true;
                    }
                    if (strcmp(argv[ind], c_tip) == 0)
                    {
                        strcpy(arg.c_mavrout_IP, argv[ind+1]);
                    }
                    if (strcmp(argv[ind], c_mpo) == 0)
                    {
                        arg.mavrout_port = std::stoi(argv[ind+1]);
                    }   
                    if (strcmp(argv[ind], c_arg_ttcp) == 0)
                    {
                        arg.mavrout_TCP = true;
                        strcpy(arg.c_mavrout_protocol,c_TCP);
                    }
                    if (strcmp(argv[ind], c_arg_tudp) == 0)
                    {
                        arg.mavrout_TCP = false;
                        strcpy(arg.c_mavrout_protocol,c_UDP);
                    }
                    if (strcmp(argv[ind], c_block) == 0)
                    {
                        arg.non_block = false;
                    }
                
                    if (strcmp(argv[ind], c_heart) == 0)
                    {
                        arg.d_heart = true;
                    }
                    if (strcmp(argv[ind], c_atit) == 0)
                    {
                        arg.d_atitude = true;
                    }   
                    if (strcmp(argv[ind], c_gui) == 0)
                    {
                        arg.d_gui = true;
                    }                
                    if (strcmp(argv[ind], c_pose) == 0)
                    {
                        arg.d_pose = true;
                    }   
            }  
        printf("> USING INPUT ARGUMENTS\n");  
        }
        
        else
            printf("> USING DEFAULTS\n");
        if(arg.local_TCP) strcpy(arg.c_local_protocal,c_TCP);
        if(!arg.local_TCP) strcpy(arg.c_local_protocal,c_UDP);
        if(arg.mavrout_TCP) strcpy(arg.c_mavrout_protocol,c_TCP);
        if(!arg.mavrout_TCP) strcpy(arg.c_mavrout_protocol,c_UDP);
        if(arg.local_server) strcpy(arg.c_local_type,c_server);
        if(!arg.local_server) strcpy(arg.c_local_type,c_client);
        if(arg.mavrout_server) strcpy(arg.c_mavrout_type,c_server);
        if(!arg.mavrout_server) strcpy(arg.c_mavrout_type,c_client);



        printf("> Local   %s %s: IP address: %s, Port Number:%u\n",arg.c_local_type,arg.c_local_protocal,arg.c_local_IP,arg.local_port);  
        printf("> Mav-Rou %s %s: IP address: %s, Port Number:%u\n\n",arg.c_mavrout_type,arg.c_mavrout_protocol,arg.c_mavrout_IP,arg.mavrout_port);  
        /* SANITY CHECK */
         if(arg.local_server == arg.mavrout_server)
        {
           printf("> Seriousaly you CAN NOT have both local and mavlink-router as a %s\n",arg.c_local_type);
           exit(EXIT_FAILURE);
        }
        // if(arg.local_port == arg.mavrout_port)
        // {
        //    printf("> Seriousaly you CAN NOT have both local and mavlink-router on the same port LOCAL:%u MAVLINK-ROUTER:%u\n",arg.local_port,arg.mavrout_port);
        //    exit(EXIT_FAILURE);
        // }
        if(arg.local_TCP != arg.mavrout_TCP)
        {
           printf("> Hmm!! you have set local protocol to be %s but mavlink-router as %s \n",arg.c_local_protocal,arg.c_mavrout_protocol);
           exit(EXIT_FAILURE);               
        }   
}

#endif