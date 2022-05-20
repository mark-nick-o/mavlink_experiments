#include <ctime>
#include <cstdlib>
#if defined(USE_EXPERIMENTAL_FS)
#include <experimental/filesystem>
namespace fs = std::experimental::filesystem;
#else
#include <filesystem>
namespace fs = std::filesystem;
#if defined(__APPLE__)
#include <unistd.h>
#endif
#endif
#include <cstdint>
#include <iomanip>
#include "CRSDK/CameraRemote_SDK.h"
#include "CameraDevice.h"
#include "Text.h"

#ifdef _WIN32
#include <Windows.h>
#else
#include <unistd.h>
#endif

#include <signal.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>

static int g_hoge = 0;

#include <time.h>
#include <sys/time.h>

//#define LIVEVIEW_ENB

namespace SDK = SCRSDK;

// MAVLink
#include "common/mavlink.h"
#include <mavlink_types.h>

// Global dll object
// cli::CRLibInterface* cr_lib = nullptr;

//auto ncams;
//auto camera_info;
//bool connect_status;
SDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
typedef std::shared_ptr<cli::CameraDevice> CameraDevicePtr;
CameraDevicePtr camera;
typedef std::vector<CameraDevicePtr> CameraDeviceList;
CameraDeviceList cameraList;                                                     // all
std::int32_t cameraNumUniq = 1;
std::int32_t selectCamera = 1;

#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/sinks/text_file_backend.hpp>
#include <boost/log/utility/setup/file.hpp>
#include <boost/log/utility/setup/common_attributes.hpp>
#include <boost/log/sources/severity_logger.hpp>
#include <boost/log/sources/record_ostream.hpp>

namespace logging = boost::log;
namespace src = boost::log::sources;
namespace sinks = boost::log::sinks;
namespace keywords = boost::log::keywords;

#if 0

void init()
{
    logging::add_file_log("sample.log");

    logging::core::get()->set_filter
    (
        logging::trivial::severity >= logging::trivial::info
    );
}

void init()
{
    logging::add_file_log
    (
        keywords::file_name = "sample_%N.log",
        keywords::rotation_size = 10 * 1024 * 1024,
        keywords::time_based_rotation = sinks::file::rotation_at_time_point(0, 0, 0),
        keywords::format = "[%TimeStamp%]: %Message%"
    );

    logging::core::get()->set_filter
    (
        logging::trivial::severity >= logging::trivial::info
    );
}

#else

void init()
{
    logging::add_file_log
    (
        keywords::file_name = "sample_%N.log",                                        /*< file name pattern >*/
        keywords::rotation_size = 10 * 1024 * 1024,                                   /*< rotate files every 10 MiB... >*/
        keywords::time_based_rotation = sinks::file::rotation_at_time_point(0, 0, 0), /*< ...or at midnight >*/
        keywords::format = "[%TimeStamp%]: %Message%"                                 /*< log record format >*/
    );

    logging::core::get()->set_filter
    (
        logging::trivial::severity >= logging::trivial::info
    );
}

#endif

// ==================== multi threading =================================
#include <boost/thread/thread.hpp>//Include boost header file
#include <iostream>
#include <cstdlib>
using namespace std;
volatile bool isRuning = true;

// ==================== include object library ==========================
#include "object_store_class.hpp"
// ==================== include enumeration library ====================
#include "sony_a7_enumerate.cpp"

void sig_handler(int signo) {

    if (signo == SIGUSR1) {
        cli::tout << " --------- GOt the SIGUSR1 ------------------- " << "\n";
//        camera->capture_image();
    } else if (signo == SIGHUP) {
        cli::tout << " --------- GOt the SIGHUP ------------------- " << "\n";
//        camera->get_aperture();
    } 
}

// http://www.coins.tsukuba.ac.jp/~syspro/2005/No5.html
//
void alrm( int signo )
{
    // take a photo
    int st = clock();
    camera->capture_image();
    int en = clock();
    cli::tout << "time from alarm handler : " << (en-st)/double(CLOCKS_PER_SEC)*1000.0f << "\n";
    cli::tout << " timer action took a picture" << "\n";
}

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/wait.h>
extern char **environ;

int reset_usb_link(){
  int pid;
  int code;
  int status;
  pid_t result;
  int i = 0;

  // performs a fork to usb control to turn off then on the usb
  //
  while(i < 2){
    pid = fork();

    // fork
    if(pid == -1){
      fprintf(stderr, "Error\n\n");
    }

    // this is the program that resets the usb power
    //
    char *argv[6];
    std::string s1 = "/home/pi/cams/SonyTEST32/uhubctl/uhubctl";
    std::string s2 = "-l";
    std::string s3 = "1-1";
    std::string s4 = "-a";
    argv[0] = &*s1.begin();
    argv[1] = &*s2.begin();
    argv[2] = &*s3.begin();
    argv[3] = &*s4.begin();


    // first time disable then enable the usb power
    if ( i == 0 ) {
        std::string s5 = "0";
        argv[4] = &*s5.begin();
    } else {
        std::string s5 = "1";
        argv[4] = &*s5.begin();
    }
    argv[5] = NULL;

    // Processing Child Processes
    if(pid == 0){
      //execl("/home/pi/cams/SonyTEST32/uhubctl/uhubctl", "/home/pi/cams/SonyTEST32/uhubctl/uhubctl", NULL);
      execve(argv[0], argv, environ);
    }else{
      result = wait(&status);

     if(result < 0){
        fprintf(stderr, "Wait Error.\n\n");
        exit(-1);
     }

     //Check the Exit status
     if(WIFEXITED(status)){
        printf("Child process Termination");
        code = WEXITSTATUS(status);
        printf("the code %d\n", code);
      }else{
        printf("wait failuer");
        printf("exit code : %d\n", status);
      }

      i++;
    }

  }
  printf("Parent process Termination\n");
  return 0;
}


// Create a global object for each item that is controlled via mavlink
//
storage_object sony_iso("S_ISO");
storage_object sony_aper("S_APERTURE");
storage_object sony_ss("S_SHUT_SPD");
storage_object sony_expro("S_EX_PRO_MODE");
storage_object sony_foc_mode("S_FOCUS_MODE");
storage_object sony_foc_area("S_FOCUS_AREA");
storage_object sony_white_bal("S_WHITE_BAL");
storage_object sony_sc("S_STILL_CAP");

// In this single tasking mode we will use this state Engine to determine the camera actions
//
enum CrCameraAction : std::uint32_t
{
	Sony_Camera_Idle = 0,
	Sony_Camera_Get_A = 1,
	Sony_Camera_Action_Init_A = 2,
	Sony_Camera_Set_Begin_A = 3,
	Sony_Camera_Set_A = 4,
	Sony_Camera_Set_Wait_A = 5,
    Sony_Camera_Check_A = 6,
	Sony_Camera_Photo = 7,
	Sony_Camera_Get_I = 8,
	Sony_Camera_Action_Init_I = 9,
	Sony_Camera_Set_Begin_I = 10,
	Sony_Camera_Set_I = 11,
	Sony_Camera_Set_Wait_I = 12,
    Sony_Camera_Check_I = 13,
	Sony_Camera_Get_FM = 14,
	Sony_Camera_Action_Init_FM = 15,
	Sony_Camera_Set_Begin_FM = 16,
	Sony_Camera_Set_FM = 17,
	Sony_Camera_Set_Wait_FM = 18,
    Sony_Camera_Check_FM = 19,
	Sony_Camera_Get_FA = 20,
	Sony_Camera_Action_Init_FA = 21,
	Sony_Camera_Set_Begin_FA = 22,
	Sony_Camera_Set_FA = 23,
	Sony_Camera_Set_Wait_FA = 24,
    Sony_Camera_Check_FA = 25,
	Sony_Camera_Get_SS = 26,
	Sony_Camera_Action_Init_SS = 27,
	Sony_Camera_Set_Begin_SS = 28,
	Sony_Camera_Set_SS = 29,
	Sony_Camera_Set_Wait_SS = 30,
    Sony_Camera_Check_SS = 31,
	Sony_Camera_Get_SC = 32,
	Sony_Camera_Action_Init_SC = 33,
	Sony_Camera_Set_Begin_SC = 34,
	Sony_Camera_Set_SC = 35,
	Sony_Camera_Set_Wait_SC = 36,
    Sony_Camera_Check_SC = 37,
	Sony_Camera_Get_WB = 38,
	Sony_Camera_Action_Init_WB = 39,
	Sony_Camera_Set_Begin_WB = 40,
	Sony_Camera_Set_WB = 41,
	Sony_Camera_Set_Wait_WB = 42,
    Sony_Camera_Check_WB = 43,
	Sony_Camera_Get_EP = 44,
	Sony_Camera_Action_Init_EP = 45,
	Sony_Camera_Set_Begin_EP = 46,
	Sony_Camera_Set_EP = 47,
	Sony_Camera_Set_Wait_EP = 48,
    Sony_Camera_Check_EP = 49,
};
std::uint32_t actionState = Sony_Camera_Idle;

#include "ini_file_reader.cpp"
#include "DronePayloadMan.cpp"
#include "xml_reader.cpp"
#define SONY_XML_FILE "sony_new_xml.xml"

int main(void)
{
	// read the .ini file to get the camera ID
	//
    auto camId_photo = get_ini_int_component("sony_photo", "camera_id" );
	std::cout << " read the photo ID from the .ini " << camId_photo << std::endl;
    auto camId_actions = get_ini_int_component("sony", "camera_id" );
	std::cout << " read the actions ID from the .ini " << camId_actions << std::endl;
    auto one_shot = get_ini_int_component("sony_photo", "one_shot" );
    auto xml_def_on = get_ini_int_component("sony", "xml_defaults" );
    std::uint32_t ini_ap = 0;
    std::uint32_t ini_iso = 0;
    std::uint32_t ini_ss = 0;
    std::uint32_t ini_sc = 0;
    std::uint32_t ini_fm = 0;
    std::uint32_t ini_fa = 0;
    std::uint32_t ini_exp = 0;
    std::uint32_t ini_wb = 0;
    std::uint32_t ini_im_store = 0;
    if (xml_def_on == 0) {
       ini_ap = get_ini_int_component("sony", "aperture" );
       ini_iso = get_ini_int_component("sony", "iso" );
       ini_ss = get_ini_int_component("sony", "shutter_s" );
       ini_fm = get_ini_int_component("sony", "focus_mode" );
       ini_fa = get_ini_int_component("sony", "focus_area" );
       ini_sc = get_ini_int_component("sony", "still_cap" );
       ini_exp = get_ini_int_component("sony", "expos" );
       ini_wb = get_ini_int_component("sony", "white_bal" );
       ini_im_store = get_ini_int_component("sony", "image_store" );
    } else if (xml_def_on == 1) {
	    std::string xml_file(SONY_XML_FILE);
        Parent xml_param;
        xml_load(xml_file, xml_param);
		for(std::vector<Child>::const_iterator cit = xml_param.children.begin(); cit != xml_param.children.end(); cit++) {
	        if (levenstein("APERTURE", cit->option_name) <= LEVENSTEIN_THRESH) {
				ini_ap = cit->xml_val;
                std::cout << "found " << cit->option_name << " similar to APERTURE with value : " << cit->xml_val << " using as a default " << std::endl;
			}
	        else if (levenstein("ISO", cit->option_name) <= LEVENSTEIN_THRESH) {
				ini_iso = cit->xml_val;
                std::cout << "found " << cit->option_name << " similar to ISO with value : " << cit->xml_val << " using as a default " << std::endl;
			}
	        else if (levenstein("SHUTTERSPD", cit->option_name) <= LEVENSTEIN_THRESH) {
				ini_ss = cit->xml_val;
                std::cout << "found " << cit->option_name << " similar to SHUTTER_SPEED with value : " << cit->xml_val << " using as a default " << std::endl;
			}
	        else if (levenstein("STILL_CAP", cit->option_name) <= LEVENSTEIN_THRESH) {
				ini_sc = cit->xml_val;
                std::cout << "found " << cit->option_name << " similar to STILL_CAP with value : " << cit->xml_val << " using as a default " << std::endl;
			}
	        else if (levenstein("EXPMODE", cit->option_name) <= LEVENSTEIN_THRESH) {
				ini_exp = cit->xml_val;
                std::cout << "found " << cit->option_name << " similar to EXPOSURE_PROGRAM with value : " << cit->xml_val << " using as a default " << std::endl;
			}
	        else if ((levenstein("_WBMODE", cit->option_name) <= LEVENSTEIN_THRESH) || (levenstein("_WHITE_BAL", cit->option_name) <= LEVENSTEIN_THRESH)) {
				ini_wb = cit->xml_val;
                std::cout << "found " << cit->option_name << " similar to WHITE_BALANCE with value : " << cit->xml_val << " using as a default " << std::endl;
			}
	        else if (levenstein("FOCUS_AREA", cit->option_name) <= LEVENSTEIN_THRESH) {
				ini_fa = cit->xml_val;
                std::cout << "found " << cit->option_name << " similar to FOCUS_AREA with value : " << cit->xml_val << " using as a default " << std::endl;
			}
	        else if (levenstein("FOCUS_MODE", cit->option_name) <= LEVENSTEIN_THRESH) {
				ini_fm = cit->xml_val;
                std::cout << "found " << cit->option_name << " similar to FOCUS_MODE with value : " << cit->xml_val << " using as a default " << std::endl;
			}		
		}
	}
		
	
    // reset the usb power on the link
	//
    reset_usb_link();

    // initialise the boost logger system
    init();
    logging::add_common_attributes();
    using namespace logging::trivial;
    src::severity_logger< severity_level > lg;
    BOOST_LOG_SEV(lg, info) << "sony cam app started";

    // Create a object for each item (I made them globals for the multitasker
    //
    //storage_object sony_iso("S_ISO");
    //storage_object sony_aper("S_APERTURE");

    // This would be set over mavlink as the new value
    // when the PARAM_EXT_VALUE is written for each respective tag name
    //
    sony_iso.add_new_req(4);
    sony_aper.add_new_req(280);

    // now the driver performs the actions as requested
    // if it sees a new request for a change of option was written to the object
    //
    if (sony_iso.my_value != sony_iso.my_prev_value) {
        cli::tout << "new value for sony iso " << sony_iso.my_value << "\n";
        BOOST_LOG_SEV(lg, debug) << "new value for sony iso " << sony_iso.my_value;	   
    } 
    if (sony_aper.my_value != sony_aper.my_prev_value) {
        cli::tout << "new value for sony aper " << sony_aper.my_value << "\n";
        BOOST_LOG_SEV(lg, debug) << "new value for sony aper " << sony_aper.my_value;	   
    } 

    // if the camera was successful this is after the method was performed
    // you would use this to update the object
    // 
    //sony_iso.add_new_value();

    // when you sent the PARAM_EXT_ACK over mavlink clear the update flag
    //
    //sony_iso.clr_update();

    // if the action was unsuccessful 
    // and you cant do it as its write protected then clear the request
    // to change the option that came over mavlink with this command
    //
    //sony_aper.clr_new_req();

    // show the mimic results for test
    cli::tout << "iso " << sony_iso.my_value << " prev " << sony_iso.my_prev_value << "\n";
    cli::tout << "aper " << sony_aper.my_value << " prev " << sony_aper.my_prev_value << "\n";

    // Change global locale to native locale
    std::locale::global(std::locale(""));
    std::string input = "";
    //if (argc < 2)
    //{
    //   cli::tout << "insufficient arguments operation cancelled" << "\n";
    //   exit(-1);
    //}
    //cli::tout << "arg count " << argc << " args  " << argv[0] << " " << input << "\n";
    //input = argv[1];
    // Make the stream's locale the same as the current global locale
    cli::tin.imbue(std::locale());
    cli::tout.imbue(std::locale());

    // timer defined interrupt code
    //struct sigaction sa_alarm;
    struct itimerval itimer;

    // this is an alternate signal handler
    //
    //memset(&sa_alarm, 0, sizeof(sa_alarm));
    //sa_alarm.sa_handler = (void*) &alrm;
    //sa_alarm.sa_flags = SA_RESTART;
    // if (sigaction(SIGALRM, &sa_alarm, NULL) < 0) {
    //    perror("sigaction");
    //    exit(1);
    //}
    // to test the interrupt uncomment here 
    //
    // itimer.it_value.tv_sec = itimer.it_interval.tv_sec = 0;
    // itimer.it_value.tv_usec = itimer.it_interval.tv_usec = 100;

    //cli::tout << "RemoteSampleApp v1.04.00 running...\n\n";

    if (signal(SIGUSR1, sig_handler) == SIG_ERR) {
        cli::tout << "cant catch SIGUSR1 " << "\n";
        BOOST_LOG_SEV(lg,error) << "cat catch SIGUSR1";
    }

    if (signal(SIGHUP, sig_handler) == SIG_ERR) {
        cli::tout << "cant catch SIGHUP " << "\n";
    }

    if (signal(SIGALRM, alrm) == SIG_ERR) {
        cli::tout << "cant catch SIGALRM " << "\n";
    }

    //if (setitimer(ITIMER_REAL, &itimer, NULL) < 0) {
    //    perror("set timer");
    //    exit(1);
    //}

    CrInt32u version = SDK::GetSDKVersion();
    int major = (version & 0xFF000000) >> 24;
    int minor = (version & 0x00FF0000) >> 16;
    int patch = (version & 0x0000FF00) >> 8;
    // int reserved = (version & 0x000000FF);

    //cli::tout << "Remote SDK version: ";
    //cli::tout << major << "." << minor << "." << std::setfill(TEXT('0')) << std::setw(2) << patch << "\n";

    // Load the library dynamically
    // cr_lib = cli::load_cr_lib();

    //cli::tout << "Initialize Remote SDK...\n";
    
#if defined(__APPLE__)
        char path[255]; /*MAX_PATH*/
        getcwd(path, sizeof(path) -1);
        //cli::tout << "Working directory: " << path << '\n';
#else
        //cli::tout << "Working directory: " << fs::current_path() << '\n';
#endif
    // auto init_success = cr_lib->Init(0);
    auto init_success = SDK::Init();
    if (!init_success) {
        cli::tout << "Failed to initialize Remote SDK. Terminating.\n";
        // cr_lib->Release();
        SDK::Release();
        std::exit(EXIT_FAILURE);
    }
    //cli::tout << "Remote SDK successfully initialized.\n\n";

    //cli::tout << "Enumerate connected camera devices...\n";
    // @@@@ made a global from this
    //SDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
    // auto enum_status = cr_lib->EnumCameraObjects(&camera_list, 3);
    auto enum_status = SDK::EnumCameraObjects(&camera_list);
    if (CR_FAILED(enum_status) || camera_list == nullptr) {
        cli::tout << "No cameras detected. Connect a camera and retry.\n";
        BOOST_LOG_SEV(lg,error) << "No cameras detected connect camera and retry";
        // cr_lib->Release();
        SDK::Release();
        std::exit(EXIT_FAILURE);
    }
    auto ncams = camera_list->GetCount();
    //cli::tout << "Camera enumeration successful. " << ncams << " detected.\n\n";

    //
	// !!!!!!!!!!!!!!!!!!! check but i suspect we just always use zero and exit if ncams is > 1 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	//
    for (CrInt32u i = 0; i < ncams; ++i) {
        auto camera_info = camera_list->GetCameraObjectInfo(i);
        cli::text conn_type(camera_info->GetConnectionTypeName());
        cli::text model(camera_info->GetModel());
        cli::text id = TEXT("");
        if (TEXT("IP") == conn_type) {
            cli::NetworkInfo ni = cli::parse_ip_info(camera_info->GetId(), camera_info->GetIdSize());
            id = ni.mac_address;
        }
        else id = ((TCHAR*)camera_info->GetId());
        //cli::tout << '[' << i + 1 << "] !!!!!!!!!!!!!!!!!! model data " << model.data() << " ( id data " << id.data() << ")\n";
    }

    // ======================= dont need to choose ===========================================
	
    //cli::tout << std::endl << "Connect to camera with input number... 1 \n";
    //cli::tout << "input> ";
    cli::text connectNo = "1";
    //std::getline(cli::tin, connectNo);
    cli::tout << '\n';

    cli::tsmatch smatch;
    CrInt32u no = 0;
    while (true) {
        no = 0;
        if (std::regex_search(connectNo, smatch, cli::tregex(TEXT("[0-9]")))) {
            no = stoi(connectNo);
            if (no == 0)
                break;                                                               // finish

            if (camera_list->GetCount() < no) {
                //cli::tout << "input value over \n";
                //cli::tout << "input> ";                                              // Redo
                //std::getline(cli::tin, connectNo);
				connectNo = "1";
                continue;
            }
            else
                break;                                                               // ok
        }
        else
            break;                                                                   // not number
    }

    if (no == 0) {
        cli::tout << "Invalid Number. Finish App.\n";
        SDK::Release();
        std::exit(EXIT_FAILURE);
    }

    // ============================================================================================= */
	
    //CrInt32u no = 1;                                                                 // we are only using one camera
	
    // @@@@ : made this a global
    //
    //typedef std::shared_ptr<cli::CameraDevice> CameraDevicePtr;
    //typedef std::vector<CameraDevicePtr> CameraDeviceList;
    //CameraDeviceList cameraList;                                                     // all
    //std::int32_t cameraNumUniq = 1;
    //std::int32_t selectCamera = 1;

    //cli::tout << "Connect to selected camera...\n";
    // @@@@ make global
    auto* camera_info = camera_list->GetCameraObjectInfo(no - 1);

    //cli::tout << "Create camera SDK camera callback object.\n";
    // @@@@ : made this a global
    //
    //CameraDevicePtr camera = CameraDevicePtr(new cli::CameraDevice(cameraNumUniq, nullptr, camera_info));
    camera = CameraDevicePtr(new cli::CameraDevice(cameraNumUniq, nullptr, camera_info));
    cameraList.push_back(camera);                                                   // add 1st

    //cli::tout << "Release enumerated camera list.\n";
    camera_list->Release();
    auto connect_status = camera->connect(SDK::CrSdkControlMode_Remote);
    if (!connect_status) {
        cli::tout << "Camera connection failed to initiate. Abort.\n";
        // cr_lib->Release();
        SDK::Release();
        std::exit(EXIT_FAILURE);
    }
    //cli::tout << "Camera connection successfully initiated!\n\n";

    // Interactive loop
    // for (;;) {
		/*
        cli::tout << "What would you like to do? Enter the corresponding number.\n";
        cli::tout
            << "(s) Status display and camera switching \n"
            << "(0) Connect / Disconnect \n"
            << "(1) Shutter Release \n"
            << "(2) Shutter Half Release in AF mode \n"
            << "(3) Shutter Half and Full Release in AF mode \n"
            << "(4) Continuous Shooting \n"
            << "(5) Aperture \n"
            << "(6) ISO \n"
            << "(7) Shutter Speed \n"
            << "(8) Live View \n"
            << "(9) Live View Imege Quality \n"
            << "(a) Position Key Setting \n"
            << "(b) Exposure Program Mode \n"
            << "(c) Still Capture Mode(Drive mode) \n"
            << "(d) Focus Mode \n"
            << "(e) Focus Area \n"
            // << "(f) Release Device \n"
            << "(11) FELock \n"
            << "(12) AWBLock \n"
            << "(13) AF Area Position(x,y) \n"
            << "(14) Selected MediaFormat \n"
            << "(15) Movie Rec Button \n"
            << "(16) White Balance \n"
            << "(17) Custom WB \n"
            << "(18) Zoom Operation \n"
#if defined(LIVEVIEW_ENB)
            << "(lv) LiveView Enable \n"
#endif
            << "(x) Exit\n";
        cli::tout << "input> ";
        cli::text action;
        std::getline(cli::tin, action);
        cli::tout << '\n';
        */
		//cli::tout << "Continuous shooting mode......";
		
		/* >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		
        if (action == TEXT("x")) { 
            CameraDeviceList::const_iterator it = cameraList.begin();
            for (std::int32_t j = 0; it != cameraList.end(); ++j, ++it) {
                if ((*it)->is_connected()) {
                    cli::tout << "Initiate disconnect sequence.\n";
                    auto disconnect_status = (*it)->disconnect();
                    if (!disconnect_status) {
                        // try again
                        disconnect_status = (*it)->disconnect();
                    }
                    if (!disconnect_status)
                        cli::tout << "Disconnect failed to initiate.\n";
                    //else
                    //  cli::tout << "Disconnect successfully initiated!\n\n";
                }
                (*it)->release();
            }
            break; // quit application loop
        }
        else if (action == TEXT("s")) { 
            cli::tout << "Status display and camera switching.\n";
#if defined(LIVEVIEW_ENB)
            cli::tout << "number - connected - lvEnb - model - id\n";
#else
            cli::tout << "number - connected - model - id\n";
#endif
            CameraDeviceList::const_iterator it = cameraList.begin();
            for (std::int32_t i = 0; it != cameraList.end(); ++i, ++it)
            {
                cli::text model = (*it)->get_model();
                if (model.size() < 10) {
                    int32_t apendCnt = 10 - model.size();
                    model.append(apendCnt, TEXT(' '));
                }
                cli::text id = (*it)->get_id();
                std::uint32_t num = (*it)->get_number();
                if (selectCamera == num) { cli::tout << "* "; }
                else { cli::tout << "  "; }
                cli::tout << std::setfill(TEXT(' ')) << std::setw(4) << std::left << num
                    << " - " << ((*it)->is_connected() ? "true " : "false")
#if defined(LIVEVIEW_ENB)
                    << " - " << ((*it)->is_live_view_enable() ? "true " : "false")
#endif
                    << " - " << model.data()
                    << " - " << id.data() << std::endl;
            }
            cli::tout << std::endl << "Selected camera number = [" << selectCamera << "]" << std::endl << std::endl;
            cli::tout << "Choose a number :\n";
            cli::tout << "[-1] Cancel input\n";
            cli::tout << "[0]  Create new CameraDevice\n";
            cli::tout << "[1]  Switch cameras for controls\n";
            cli::tout << std::endl << "input> ";
            cli::text input;
            std::getline(cli::tin, input);
            cli::text_stringstream ss(input);
            int selected_index = 0;
            ss >> selected_index;
            if (selected_index < 0 || 1 < selected_index) {
                cli::tout << "Input cancelled.\n";
            }
            // new camera connect
            if (0 == selected_index) {
                enum_status = SDK::EnumCameraObjects(&camera_list);
                if (CR_FAILED(enum_status) || camera_list == nullptr) {
                    cli::tout << "No cameras detected. Connect a camera and retry.\n";
                }
                else
                {
                    cli::tout << "[-1] Cancel input\n";
                    ncams = camera_list->GetCount();
                    for (CrInt32u i = 0; i < ncams; ++i) {
                        auto camera_info = camera_list->GetCameraObjectInfo(i);
                        cli::text conn_type(camera_info->GetConnectionTypeName());
                        cli::text model(camera_info->GetModel());
                        cli::text id = TEXT("");
                        if (TEXT("IP") == conn_type) {
                            cli::NetworkInfo ni = cli::parse_ip_info(camera_info->GetId(), camera_info->GetIdSize());
                            id = ni.mac_address;
                        }
                        else id = ((TCHAR*)camera_info->GetId());
                        cli::tout << '[' << i + 1 << "] " << model.data() << " (" << id.data() << ") ";
                        CameraDeviceList::const_iterator it = cameraList.begin();
                        for (std::int32_t j = 0; it != cameraList.end(); ++j, ++it){
                            cli::text alreadyId = (*it)->get_id();
                            if (0 == id.compare(alreadyId)) {
                                cli::tout << "*";
                                break;
                            }
                        }
                        cli::tout << std::endl;
                    }
                    cli::tout << std::endl << "idx input> ";
                    std::getline(cli::tin, input);
                    cli::text_stringstream ss2(input);
                    int selected_no = 0;
                    ss2 >> selected_no;
                    if (selected_no < 1 || (std::int32_t)ncams < selected_no) {
                        cli::tout << "Input cancelled.\n";
                    }
                    else {
                        camera_info = camera_list->GetCameraObjectInfo(selected_no - 1);
                        cli::text conn_type(camera_info->GetConnectionTypeName());
                        cli::text model_select(camera_info->GetModel());
                        cli::text id_select = TEXT("");
                        if (TEXT("IP") == conn_type) {
                            cli::NetworkInfo ni = cli::parse_ip_info(camera_info->GetId(), camera_info->GetIdSize());
                            id_select = ni.mac_address;
                        }
                        else id_select = ((TCHAR*)camera_info->GetId());
                        bool findAlready = false;
                        CameraDeviceList::const_iterator it = cameraList.begin();
                        for (std::int32_t j = 0; it != cameraList.end(); ++j, ++it) {
                            if ((0 == (*it)->get_model().compare(model_select)) &&
                                (0 == (*it)->get_id().compare(id_select))) {
                                findAlready = true;
                                cli::tout << "Already connected!\n";
                                break;
                            }
                        }
                        if (false == findAlready) {
                            std::int32_t newNum = cameraNumUniq + 1;
                            CameraDevicePtr newCam = CameraDevicePtr(new cli::CameraDevice(newNum, nullptr, camera_info));
                            if (true == newCam->connect()) {
                                cameraNumUniq = newNum;
                                cameraList.push_back(newCam);                       // add
                                camera = newCam;                                    // switch target
                                selectCamera = cameraNumUniq;                       // latest
                            }
                        }
                    }
                    camera_list->Release();
                }
            }
            // switch device
            if (1 == selected_index) {
                cli::tout << std::endl << "number input> ";
                std::getline(cli::tin, input);
                cli::text_stringstream ss3(input);
                int input_no = 0;
                ss3 >> input_no;
                if (input_no < 1) {
                    cli::tout << "Input cancelled.\n";
                }
                else {
                    bool findTarget = false;
                    CameraDeviceList::const_iterator it = cameraList.begin();
                    for (; it != cameraList.end(); ++it) {
                        if ((*it)->get_number() == input_no) {
                            findTarget = true;
                            camera = (*it);
                            selectCamera = input_no;
                            break;
                        }
                    }
                    if (!findTarget) {
                        cli::tout << "The specified camera cannot be found!\n";
                    }
                }
            }
        }
        else if (action == TEXT("0")) { 
            if (camera->is_connected()) {
                camera->disconnect();
            }
            else {
                camera->connect(SDK::CrSdkControlMode_Remote);
            }
        }
		
		>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> */
		
        //else if (action == TEXT("f")) { /* ReleaseDevice */
        //    if (2 > cameraList.size()) {
        //        cli::tout << std::endl << "Does not execute if there is no camera to switch control after the release device of the specified camera." << std::endl;
        //    }
        //    else {
        //        CameraDeviceList::const_iterator it = cameraList.begin();
        //        for (; it != cameraList.end(); ++it) {
        //            if ((*it)->get_number() == camera->get_number()) {
        //                (*it)->release();
        //                cameraList.erase(it);
        //                break;
        //            }
        //        }
        //        it = cameraList.begin(); // switch to top of list
        //        camera = (*it);
        //        selectCamera = camera->get_number();
        //    }
        //}
        
		//else {
            //while (!camera->is_connected()) {
            //    cli::tout << "This camera is disabled or disconnected attempt reconnection\n" << std::endl;
		    //    camera->connect();
            //cli::tout << "waiting 5 seconds!\n";
	        // sleep(5);
            //cli::tout << "ready to capture image!\n";
            //continue;
            //}

            //if (action == TEXT("1")) {                             /* wait to take photo */


            // uncomment to activate the timed interrupt code int imgCnt = 50;
            int imgCnt = 0;

            // ------- activate a change of enumerated type at this rate
            //
            //itimer.it_value.tv_sec = itimer.it_interval.tv_sec = 5;
            //itimer.it_value.tv_usec = itimer.it_interval.tv_usec = 300000;
			//itimer.it_value.tv_usec = itimer.it_interval.tv_usec = 0;
            //itimer.it_value.tv_usec = itimer.it_interval.tv_usec = 0;
            //if (setitimer(ITIMER_REAL, &itimer, NULL) < 0) {
            //    perror("set timer");
            //    exit(1);
            //}
			
            // ================== WAIT HERE FOR SIGNALS ===========================
            //
			
			// This is the timers which allow the code to continually cycle with time
			//
            auto t_start = std::chrono::high_resolution_clock::now();
            auto t_end = std::chrono::high_resolution_clock::now();
            auto tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();			
			
            while (imgCnt > 0)
            {
                int st = clock();
                t_start = std::chrono::high_resolution_clock::now();
                cli::tout << "wall GAp : " << std::chrono::duration<double, std::milli>(t_start-t_end).count() <<  "\n";
                camera->capture_image();
                int en = clock();
                t_end = std::chrono::high_resolution_clock::now();
                cli::tout << "time : " << 1000.0f * (en-st)/double(CLOCKS_PER_SEC) << "\n";
                cli::tout << "wall : " << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
                //imgCnt--;
                //usleep(250000);
                sleep(1);                                           /* always sleep and wait for the signal */
            }


            //else if (action == TEXT("2")) { /* S1 Shooting */
            //    camera->s1_shooting();
            //}
            //else if (action == TEXT("3")) { /* AF Shutter */
            //    camera->af_shutter();
            //}
            //else if (action == TEXT("4")) { /* Continuous Shooting */
            //    camera->continuous_shooting();
            //}
            //else if (action == TEXT("5")) { /* Aperture. */
	        //  sleep(5);

            // invoke this method once on start-up to get the current set up into memory
            //
            // its private either move or just call one that calls it camera->load_properties();
            camera->get_aperture();
            sleep(2);

            // grab all data as a single shot and update the objects with the data
            //
            std::vector<std::tuple<std::string, std::uint8_t, std::uint32_t>> p;
            if (camera->LoadMavProperties(p) == 1) {
                sony_iso.update_from_cam_vec(p);
		        sony_aper.update_from_cam_vec(p);
		        sony_ss.update_from_cam_vec(p);
		        sony_expro.update_from_cam_vec(p);
		        sony_foc_mode.update_from_cam_vec(p);
		        sony_foc_area.update_from_cam_vec(p);
		        sony_white_bal.update_from_cam_vec(p);
                cli::tout << "mav props " << "\n";
            }

            /* this was the old actions from the previous program used with the python
			
            // ============ request new aperture value then set it ============
			//
            if (sony_aper.my_value != sony_aper.my_prev_value) {
              std::stringstream ss_stream;
              std::string cam_enum_aper;
              ss_stream << sony_aper.my_value;
              ss_stream >> cam_enum_aper;
              cli::tout << "\033[32m setting aperture \033[0m" << cam_enum_aper << "\n";
              sleep(5);
              camera->get_aperture();
	          sleep(5);
              camera->set_aperture_args( cam_enum_aper );
              sleep(5);
              camera->get_aperture();
              // if the action was successful 
              5ony_aper.add_new_value();
              // when you sent the PARAM_EXT_ACK clear the update flag
              sony_aper.clr_update();
              // if the action was unsuccessful 
              // sony_aper.clr_new_req();
              // show the mimic results for test
              cli::tout << "aper " << sony_aper.my_value << " prev " << sony_aper.my_prev_value << "\n";
            }
 
              endof previous code */
  
            sony_aper.add_new_req(ini_ap);
			sony_iso.add_new_req(ini_iso);
            sony_ss.add_new_req(ini_ss);
            sony_expro.add_new_req(ini_exp);
            sony_foc_mode.add_new_req(ini_fm);
            sony_foc_area.add_new_req(ini_fa);
            sony_white_bal.add_new_req(ini_wb);
            sony_sc.add_new_req(ini_sc);
			
	        int xxxx = 0;
			actionState = Sony_Camera_Idle;
			
            // this repeat is just used for testing
			//
            // ===========================================================>> for (int z=0; z < 5; z++) { <<==================================================================================
            for (;;) {                // $$$$$$$$$$$$$$$$$$$$$$$$$$$ for ever
			
            //xxxx = mav_main();
			
            //cli::tout << "z is .... " << z << "\n";
            //camera->capture_image();
	
            // ============================ Aperture ========================================================
            //	
	/*	
            if ((sony_aper.my_value != sony_aper.my_prev_value) && (actionState == Sony_Camera_Idle)) {
				
                if (actionState == Sony_Camera_Idle) {
                  actionState = Sony_Camera_Action_Init_A;
				  cli::tout << "init action aper" << "\n";
			    }	
			}
            else if (sony_aper.my_value != sony_aper.my_prev_value) {
				
			    if ( not(actionState == Sony_Camera_Idle) ) { 
				
                    switch(actionState) 
			        {
				        case Sony_Camera_Action_Init_A:
						{
                            auto ap_data = camera->GetAperture();                                                                // invoke this on the camera object
                            cli::tout << "ApertureSet " << std::get<0>(ap_data) << "\n";                                         // this is the 1st string being printed
                            cli::tout << "ApertureVal " << std::get<2>(ap_data) << "\n";                                         // this is the 2nd string being printed   
				            if (std::get<2>(ap_data) == sony_aper.my_value) {                                                    // value match already by manual intervention
                               cli::tout << "\033[31m aperture request already matched the value \033[0m" << sony_aper.my_value << "\n";
                               sony_aper.add_new_value();					  
                               actionState = Sony_Camera_Idle;
				            }
					        else {
                               cli::tout << "\033[32m aperture request being made for \033[0m" << sony_aper.my_value << "\n";
						       actionState = Sony_Camera_Set_Begin_A;
						       t_start = std::chrono::high_resolution_clock::now();
					        }
						}
                        break;

					    case Sony_Camera_Set_Begin_A:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[36m time waiting : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						       cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						       actionState = Sony_Camera_Set_A;	
                            }
						}
                        break;
						
                        case Sony_Camera_Set_A:	
                        {				
                            cli::tout << " set cam " << "\n";		
			                std::stringstream ss_stream1;
                            std::string cam_enum_aper1;
                            //ss_stream1 << sony_aper.my_value;
                            ss_stream1 << enumerate_aperture_sony_a7(sony_aper.my_value);
                            ss_stream1 >> cam_enum_aper1;
                            cli::tout << "\033[32m setting aperture \033[0m" << cam_enum_aper1 << "\n";
                            if (camera->SetApertureArgs( cam_enum_aper1 ) == 1) {
                                t_start = std::chrono::high_resolution_clock::now();
			                    actionState = Sony_Camera_Set_Wait_A;
                            }
                            else {
                               // if the action was unsuccessful
                               cli::tout << "\033[31m action unsuccesful for aperture \033[0m" << "\n";
                               sony_aper.clr_new_req();
						       actionState = Sony_Camera_Idle;
                            }
						}
						break;
					  
					    case Sony_Camera_Set_Wait_A:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[34m time waiting 2 : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 10000.0) {
						        cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						        actionState = Sony_Camera_Check_A;	
                            }
						}
                        break;						
					  
					    case Sony_Camera_Check_A:
						{
					        auto ap_data = camera->GetAperture();            // invoke this on the camera object
                            cli::tout << "ApertureSet " << std::get<0>(ap_data) << "\n";   // this is the 1st string being printed
                            cli::tout << "ApertureVal " << std::get<2>(ap_data) << "\n";   // this is the 2nd string being printed
                            // if the action was successful
                            cli::tout << "requested " << sony_aper.my_value << "\n";

						    if (std::get<2>(ap_data) == sony_aper.my_value) {
                                sony_aper.add_new_value();
						    } 
						    actionState = Sony_Camera_Idle;
                        }							
					    break;
						
						default:
						actionState = Sony_Camera_Idle;	
                        break;						
                    }
			  
                    // when you sent the PARAM_EXT_ACK clear the update flag
                    sony_aper.clr_update();

                    // show the mimic results for test
					//
                    // cli::tout << "aper " << sony_aper.my_value << " prev " << sony_aper.my_prev_value << "\n";
                }
            }
*/			

            // ============================ Iso ========================================================
            //	

			
            if ((sony_iso.my_value != sony_iso.my_prev_value) && (actionState == Sony_Camera_Idle)) {
				
                if (actionState == Sony_Camera_Idle) {
                  actionState = Sony_Camera_Action_Init_I;
			    }	
			}
            else if (sony_iso.my_value != sony_iso.my_prev_value) {
				
			    if ( not(actionState == Sony_Camera_Idle) ) { 
				
                    switch(actionState) 
			        {
				        case Sony_Camera_Action_Init_I:
						{
                            auto ap_data = camera->GetIso();                                                                // invoke this on the camera object
                            cli::tout << "IsoSet " << std::get<0>(ap_data) << "\n";                                         // this is the 1st string being printed
                            cli::tout << "IsoVal " << std::get<2>(ap_data) << "\n";                                         // this is the 2nd string being printed   
				            if (std::get<2>(ap_data) == sony_iso.my_value) {                                                    // value match already by manual intervention
                               cli::tout << "\033[31m iso request already matched the value \033[0m" << sony_iso.my_value << "\n";
                               sony_iso.add_new_value();					  
                               actionState = Sony_Camera_Idle;
				            }
					        else {
                               cli::tout << "\033[32m iso request being made for \033[0m" << sony_iso.my_value << "\n";
						       actionState = Sony_Camera_Set_Begin_I;
						       t_start = std::chrono::high_resolution_clock::now();
					        }
						}
                        break;

					    case Sony_Camera_Set_Begin_I:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[36m time waiting : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 10000.0) {
						       cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						       actionState = Sony_Camera_Set_I;	
                            }
						}
                        break;
						
                        case Sony_Camera_Set_I:	
                        {				
                            cli::tout << " set cam iso " << "\n";		
			                std::stringstream ss_stream1;
                            std::string cam_enum;
                            //ss_stream1 << sony_iso.my_value;
                            ss_stream1 << enumerate_iso_sony_a7(sony_iso.my_value);
                            ss_stream1 >> cam_enum;
                            cli::tout << "\033[32m setting iso \033[0m" << cam_enum << "\n";
                            if (camera->SetIsoArgs( cam_enum ) == 1) {
                                t_start = std::chrono::high_resolution_clock::now();
			                    actionState = Sony_Camera_Set_Wait_I;
                            }
                            else {
                               // if the action was unsuccessful
                               cli::tout << "\033[31m action unsuccesful for iso \033[0m" << "\n";
                               sony_iso.clr_new_req();
						       actionState = Sony_Camera_Idle;
                            }
						}
						break;
					  
					    case Sony_Camera_Set_Wait_I:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[34m time waiting 2 : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 10000.0) {
						        cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						        actionState = Sony_Camera_Check_I;	
                            }
						}
                        break;						
					  
					    case Sony_Camera_Check_I:
						{
					        auto ap_data = camera->GetIso();            // invoke this on the camera object
                            cli::tout << "IsoSet " << std::get<0>(ap_data) << "\n";   // this is the 1st string being printed
                            cli::tout << "IsoVal " << std::get<2>(ap_data) << "\n";   // this is the 2nd string being printed
                            // if the action was successful
                            cli::tout << "requested " << sony_iso.my_value << "\n";

						    if (std::get<2>(ap_data) == sony_iso.my_value) {
                                sony_iso.add_new_value();
						    } 
						    actionState = Sony_Camera_Idle;
                        }							
					    break;
						
						default:
						actionState = Sony_Camera_Idle;	
                        break;						
                    }
			  
                    // when you sent the PARAM_EXT_ACK clear the update flag
                    sony_iso.clr_update();

                    // show the mimic results for test
					//
                    // cli::tout << "iso " << sony_iso.my_value << " prev " << sony_iso.my_prev_value << "\n";
                }
            }


            // ============================ Shutter Speed ========================================================
            //	
/*			
            if ((sony_ss.my_value != sony_ss.my_prev_value) && (actionState == Sony_Camera_Idle)) {
				
                if (actionState == Sony_Camera_Idle) {
                  actionState = Sony_Camera_Action_Init_SS;
			    }	
			}
            else if (sony_ss.my_value != sony_ss.my_prev_value) {
				
			    if ( not(actionState == Sony_Camera_Idle) ) { 
				
                    switch(actionState) 
			        {
				        case Sony_Camera_Action_Init_SS:
						{
                            auto ap_data = camera->GetShutterSpeed();                                                                // invoke this on the camera object
                            cli::tout << "SS_Set " << std::get<0>(ap_data) << "\n";                                         // this is the 1st string being printed
                            cli::tout << "SS_Val " << std::get<2>(ap_data) << "\n";                                         // this is the 2nd string being printed   
				            if (std::get<2>(ap_data) == sony_ss.my_value) {                                                    // value match already by manual intervention
                               cli::tout << "\033[31m ss request already matched the value \033[0m" << sony_ss.my_value << "\n";
                               sony_ss.add_new_value();					  
                               actionState = Sony_Camera_Idle;
				            }
					        else {
                               cli::tout << "\033[32m ss request being made for \033[0m" << sony_ss.my_value << "\n";
						       actionState = Sony_Camera_Set_Begin_SS;
						       t_start = std::chrono::high_resolution_clock::now();
					        }
						}
                        break;

					    case Sony_Camera_Set_Begin_SS:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[36m time waiting : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						       cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						       actionState = Sony_Camera_Set_SS;	
                            }
						}
                        break;
						
                        case Sony_Camera_Set_SS:	
                        {				
                            cli::tout << " set cam ss " << "\n";		
			                std::stringstream ss_stream1;
                            std::string cam_enum;
                            //ss_stream1 << sony_ss.my_value;
                            ss_stream1 << enumerate_shutter_sony_a7(sony_ss.my_value);
                            ss_stream1 >> cam_enum;
                            cli::tout << "\033[32m setting ss \033[0m" << cam_enum << "\n";
                            if (camera->SetShutterSpeedArgs( cam_enum ) == 1) {
                                t_start = std::chrono::high_resolution_clock::now();
			                    actionState = Sony_Camera_Set_Wait_SS;
                            }
                            else {
                               // if the action was unsuccessful
                               cli::tout << "\033[31m action unsuccesful for ss \033[0m" << "\n";
                               sony_ss.clr_new_req();
						       actionState = Sony_Camera_Idle;
                            }
						}
						break;
					  
					    case Sony_Camera_Set_Wait_SS:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[34m time waiting 2 : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						        cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						        actionState = Sony_Camera_Check_SS;	
                            }
						}
                        break;						
					  
					    case Sony_Camera_Check_SS:
						{
					        auto ap_data = camera->GetShutterSpeed();            // invoke this on the camera object
                            cli::tout << "SSSet " << std::get<0>(ap_data) << "\n";   // this is the 1st string being printed
                            cli::tout << "SSVal " << std::get<2>(ap_data) << "\n";   // this is the 2nd string being printed
                            // if the action was successful
                            cli::tout << "requested ss " << sony_ss.my_value << "\n";

						    if (std::get<2>(ap_data) == sony_ss.my_value) {
                                sony_ss.add_new_value();
						    } 
						    actionState = Sony_Camera_Idle;
                        }							
					    break;
						
						default:
						actionState = Sony_Camera_Idle;	
                        break;						
                    }
			  
                    // when you sent the PARAM_EXT_ACK clear the update flag
                    sony_ss.clr_update();

                    // show the mimic results for test
					//
                    // cli::tout << "iso " << sony_ss.my_value << " prev " << sony_ss.my_prev_value << "\n";
                }
            }
*/
            // ============================ Still Capture Mode ========================================================
            //	
/*			
            if ((sony_sc.my_value != sony_sc.my_prev_value) && (actionState == Sony_Camera_Idle)) {
				
                if (actionState == Sony_Camera_Idle) {
                  actionState = Sony_Camera_Action_Init_SC;
			    }	
			}
            else if (sony_sc.my_value != sony_sc.my_prev_value) {
				
			    if ( not(actionState == Sony_Camera_Idle) ) { 
				
                    switch(actionState) 
			        {
				        case Sony_Camera_Action_Init_SC:
						{
                            auto ap_data = camera->GetStillCapMode();                                                                // invoke this on the camera object
                            cli::tout << "SS_Set " << std::get<0>(ap_data) << "\n";                                         // this is the 1st string being printed
                            cli::tout << "SS_Val " << std::get<2>(ap_data) << "\n";                                         // this is the 2nd string being printed   
				            if (std::get<2>(ap_data) == sony_sc.my_value) {                                                    // value match already by manual intervention
                               cli::tout << "\033[31m sc request already matched the value \033[0m" << sony_sc.my_value << "\n";
                               sony_sc.add_new_value();					  
                               actionState = Sony_Camera_Idle;
				            }
					        else {
                               cli::tout << "\033[32m ss request being made for \033[0m" << sony_sc.my_value << "\n";
						       actionState = Sony_Camera_Set_Begin_SC;
						       t_start = std::chrono::high_resolution_clock::now();
					        }
						}
                        break;

					    case Sony_Camera_Set_Begin_SC:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[36m time waiting : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						       cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						       actionState = Sony_Camera_Set_SC;	
                            }
						}
                        break;
						
                        case Sony_Camera_Set_SC:	
                        {				
                            cli::tout << " set cam sc " << "\n";		
			                std::stringstream ss_stream1;
                            std::string cam_enum;
                            //ss_stream1 << sony_sc.my_value;
                            ss_stream1 << enumerate_still_cap_sony_a7(sony_sc.my_value);
                            ss_stream1 >> cam_enum;
                            cli::tout << "\033[32m setting sc \033[0m" << cam_enum << "\n";
                            if (camera->SetStillCaptureModeArgs( cam_enum ) == 1) {
                                t_start = std::chrono::high_resolution_clock::now();
			                    actionState = Sony_Camera_Set_Wait_SC;
                            }
                            else {
                               // if the action was unsuccessful
                               cli::tout << "\033[31m action unsuccesful for ss \033[0m" << "\n";
                               sony_sc.clr_new_req();
						       actionState = Sony_Camera_Idle;
                            }
						}
						break;
					  
					    case Sony_Camera_Set_Wait_SC:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[34m time waiting 2 : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						        cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						        actionState = Sony_Camera_Check_SC;	
                            }
						}
                        break;						
					  
					    case Sony_Camera_Check_SC:
						{
					        auto ap_data = camera->GetStillCapMode();            // invoke this on the camera object
                            cli::tout << "SSSet " << std::get<0>(ap_data) << "\n";   // this is the 1st string being printed
                            cli::tout << "SSVal " << std::get<2>(ap_data) << "\n";   // this is the 2nd string being printed
                            // if the action was successful
                            cli::tout << "requested sc " << sony_sc.my_value << "\n";

						    if (std::get<2>(ap_data) == sony_sc.my_value) {
                                sony_sc.add_new_value();
						    } 
						    actionState = Sony_Camera_Idle;
                        }							
					    break;
						
						default:
						actionState = Sony_Camera_Idle;	
                        break;						
                    }
			  
                    // when you sent the PARAM_EXT_ACK clear the update flag
                    sony_sc.clr_update();

                    // show the mimic results for test
					//
                    // cli::tout << "iso " << sony_sc.my_value << " prev " << sony_sc.my_prev_value << "\n";
                }
            }
*/

            // ============================ White Balance ========================================================
            //	
/*			
            if ((sony_white_bal.my_value != sony_white_bal.my_prev_value) && (actionState == Sony_Camera_Idle)) {
				
                if (actionState == Sony_Camera_Idle) {
                  actionState = Sony_Camera_Action_Init_WB;
			    }	
			}
            else if (sony_white_bal.my_value != sony_white_bal.my_prev_value) {
				
			    if ( not(actionState == Sony_Camera_Idle) ) { 
				
                    switch(actionState) 
			        {
				        case Sony_Camera_Action_Init_WB:
						{
                            auto ap_data = camera->GetWhiteBalance();                                                                // invoke this on the camera object
                            cli::tout << "WB_Set " << std::get<0>(ap_data) << "\n";                                         // this is the 1st string being printed
                            cli::tout << "WB_Val " << std::get<2>(ap_data) << "\n";                                         // this is the 2nd string being printed   
				            if (std::get<2>(ap_data) == sony_white_bal.my_value) {                                                    // value match already by manual intervention
                               cli::tout << "\033[31m white balance request already matched the value \033[0m" << sony_white_bal.my_value << "\n";
                               sony_white_bal.add_new_value();					  
                               actionState = Sony_Camera_Idle;
				            }
					        else {
                               cli::tout << "\033[32m wb request being made for \033[0m" << sony_white_bal.my_value << "\n";
						       actionState = Sony_Camera_Set_Begin_WB;
						       t_start = std::chrono::high_resolution_clock::now();
					        }
						}
                        break;

					    case Sony_Camera_Set_Begin_WB:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[36m time waiting : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						       cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						       actionState = Sony_Camera_Set_WB;	
                            }
						}
                        break;
						
                        case Sony_Camera_Set_WB:	
                        {				
                            cli::tout << " set cam wb " << "\n";		
			                std::stringstream ss_stream1;
                            std::string cam_enum;
                            //ss_stream1 << sony_white_bal.my_value;
                            ss_stream1 << enumerate_white_bal_sony_a7(sony_white_bal.my_value);
                            ss_stream1 >> cam_enum;
                            cli::tout << "\033[32m setting wb \033[0m" << cam_enum << "\n";
                            if (camera->SetWhiteBalanceArgs( cam_enum ) == 1) {
                                t_start = std::chrono::high_resolution_clock::now();
			                    actionState = Sony_Camera_Set_Wait_WB;
                            }
                            else {
                               // if the action was unsuccessful
                               cli::tout << "\033[31m action unsuccesful for wb \033[0m" << "\n";
                               sony_white_bal.clr_new_req();
						       actionState = Sony_Camera_Idle;
                            }
						}
						break;
					  
					    case Sony_Camera_Set_Wait_WB:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[34m time waiting 2 : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						        cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						        actionState = Sony_Camera_Check_WB;	
                            }
						}
                        break;						
					  
					    case Sony_Camera_Check_WB:
						{
					        auto ap_data = camera->GetWhiteBalance();            // invoke this on the camera object
                            cli::tout << "WBSet " << std::get<0>(ap_data) << "\n";   // this is the 1st string being printed
                            cli::tout << "WBVal " << std::get<2>(ap_data) << "\n";   // this is the 2nd string being printed
                            // if the action was successful
                            cli::tout << "requested wb " << sony_white_bal.my_value << "\n";

						    if (std::get<2>(ap_data) == sony_white_bal.my_value) {
                                sony_white_bal.add_new_value();
						    } 
						    actionState = Sony_Camera_Idle;
                        }							
					    break;
						
						default:
						actionState = Sony_Camera_Idle;	
                        break;						
                    }
			  
                    // when you sent the PARAM_EXT_ACK clear the update flag
                    sony_white_bal.clr_update();

                    // show the mimic results for test
					//
                    // cli::tout << "iso " << sony_white_bal.my_value << " prev " << sony_white_bal.my_prev_value << "\n";
                }
            }
*/

            // ============================ Focus Area ========================================================
            //	
/*			
            if ((sony_foc_area.my_value != sony_foc_area.my_prev_value) && (actionState == Sony_Camera_Idle)) {
				
                if (actionState == Sony_Camera_Idle) {
                  actionState = Sony_Camera_Action_Init_FA;
			    }	
			}
            else if (sony_foc_area.my_value != sony_foc_area.my_prev_value) {
				
			    if ( not(actionState == Sony_Camera_Idle) ) { 
				
                    switch(actionState) 
			        {
				        case Sony_Camera_Action_Init_FA:
						{
                            auto ap_data = camera->GetFocusArea();                                                                // invoke this on the camera object
                            cli::tout << "FA_Set " << std::get<0>(ap_data) << "\n";                                         // this is the 1st string being printed
                            cli::tout << "FA_Val " << std::get<2>(ap_data) << "\n";                                         // this is the 2nd string being printed   
				            if (std::get<2>(ap_data) == sony_foc_area.my_value) {                                                    // value match already by manual intervention
                               cli::tout << "\033[31m focus area request already matched the value \033[0m" << sony_foc_area.my_value << "\n";
                               sony_foc_area.add_new_value();					  
                               actionState = Sony_Camera_Idle;
				            }
					        else {
                               cli::tout << "\033[32m fa request being made for \033[0m" << sony_foc_area.my_value << "\n";
						       actionState = Sony_Camera_Set_Begin_FA;
						       t_start = std::chrono::high_resolution_clock::now();
					        }
						}
                        break;

					    case Sony_Camera_Set_Begin_FA:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[36m time waiting : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						       cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						       actionState = Sony_Camera_Set_FA;	
                            }
						}
                        break;
						
                        case Sony_Camera_Set_FA:	
                        {				
                            cli::tout << " set cam fa " << "\n";		
			                std::stringstream ss_stream1;
                            std::string cam_enum;
                            //ss_stream1 << sony_foc_area.my_value;
                            ss_stream1 << enumerate_focus_area_sony_a7(sony_foc_area.my_value);
                            ss_stream1 >> cam_enum;
                            cli::tout << "\033[32m setting fa \033[0m" << cam_enum << "\n";
                            if (camera->SetFocusAreaArgs( cam_enum ) == 1) {
                                t_start = std::chrono::high_resolution_clock::now();
			                    actionState = Sony_Camera_Set_Wait_FA;
                            }
                            else {
                               // if the action was unsuccessful
                               cli::tout << "\033[31m action unsuccesful for fa \033[0m" << "\n";
                               sony_foc_area.clr_new_req();
						       actionState = Sony_Camera_Idle;
                            }
						}
						break;
					  
					    case Sony_Camera_Set_Wait_FA:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[34m time waiting 2 : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						        cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						        actionState = Sony_Camera_Check_FA;	
                            }
						}
                        break;						
					  
					    case Sony_Camera_Check_FA:
						{
					        auto ap_data = camera->GetFocusArea();            // invoke this on the camera object
                            cli::tout << "FASet " << std::get<0>(ap_data) << "\n";   // this is the 1st string being printed
                            cli::tout << "FAVal " << std::get<2>(ap_data) << "\n";   // this is the 2nd string being printed
                            // if the action was successful
                            cli::tout << "requested fa " << sony_foc_area.my_value << "\n";

						    if (std::get<2>(ap_data) == sony_foc_area.my_value) {
                                sony_foc_area.add_new_value();
						    } 
						    actionState = Sony_Camera_Idle;
                        }							
					    break;
						
						default:
						actionState = Sony_Camera_Idle;	
                        break;						
                    }
			  
                    // when you sent the PARAM_EXT_ACK clear the update flag
                    sony_foc_area.clr_update();

                    // show the mimic results for test
					//
                    // cli::tout << "iso " << sony_foc_area.my_value << " prev " << sony_foc_area.my_prev_value << "\n";
                }
            }
*/

            // ============================ Focus Mode ========================================================
            //		
/*			
            if ((sony_foc_mode.my_value != sony_foc_mode.my_prev_value) && (actionState == Sony_Camera_Idle)) {
				
                if (actionState == Sony_Camera_Idle) {
                  actionState = Sony_Camera_Action_Init_FM;
			    }	
			}
            else if (sony_foc_mode.my_value != sony_foc_mode.my_prev_value) {
				
			    if ( not(actionState == Sony_Camera_Idle) ) { 
				
                    switch(actionState) 
			        {
				        case Sony_Camera_Action_Init_FM:
						{
                            auto ap_data = camera->GetFocusMode();                                                                // invoke this on the camera object
                            cli::tout << "FM_Set " << std::get<0>(ap_data) << "\n";                                         // this is the 1st string being printed
                            cli::tout << "FM_Val " << std::get<2>(ap_data) << "\n";                                         // this is the 2nd string being printed   
				            if (std::get<2>(ap_data) == sony_foc_mode.my_value) {                                                    // value match already by manual intervention
                               cli::tout << "\033[31m focus area request already matched the value \033[0m" << sony_foc_mode.my_value << "\n";
                               sony_foc_mode.add_new_value();					  
                               actionState = Sony_Camera_Idle;
				            }
					        else {
                               cli::tout << "\033[32m fm request being made for \033[0m" << sony_foc_mode.my_value << "\n";
						       actionState = Sony_Camera_Set_Begin_FM;
						       t_start = std::chrono::high_resolution_clock::now();
					        }
						}
                        break;

					    case Sony_Camera_Set_Begin_FM:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[36m time waiting : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						       cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						       actionState = Sony_Camera_Set_FM;	
                            }
						}
                        break;
						
                        case Sony_Camera_Set_FM:	
                        {				
                            cli::tout << " set cam fm " << "\n";		
			                std::stringstream ss_stream1;
                            std::string cam_enum;
                            //ss_stream1 << sony_foc_mode.my_value;
                            ss_stream1 << enumerate_focus_sony_a7(sony_foc_mode.my_value);
                            ss_stream1 >> cam_enum;
                            cli::tout << "\033[32m setting fm \033[0m" << cam_enum << "\n";
                            if (camera->SetFocusModeArgs( cam_enum ) == 1) {
                                t_start = std::chrono::high_resolution_clock::now();
			                    actionState = Sony_Camera_Set_Wait_FM;
                            }
                            else {
                               // if the action was unsuccessful
                               cli::tout << "\033[31m action unsuccesful for fm \033[0m" << "\n";
                               sony_foc_mode.clr_new_req();
						       actionState = Sony_Camera_Idle;
                            }
						}
						break;
					  
					    case Sony_Camera_Set_Wait_FM:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[34m time waiting 2 : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						        cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						        actionState = Sony_Camera_Check_FM;	
                            }
						}
                        break;						
					  
					    case Sony_Camera_Check_FM:
						{
					        auto ap_data = camera->GetFocusMode();            // invoke this on the camera object
                            cli::tout << "FMSet " << std::get<0>(ap_data) << "\n";   // this is the 1st string being printed
                            cli::tout << "FMVal " << std::get<2>(ap_data) << "\n";   // this is the 2nd string being printed
                            // if the action was successful
                            cli::tout << "requested fm " << sony_foc_mode.my_value << "\n";

						    if (std::get<2>(ap_data) == sony_foc_mode.my_value) {
                                sony_foc_mode.add_new_value();
						    } 
						    actionState = Sony_Camera_Idle;
                        }							
					    break;
						
						default:
						actionState = Sony_Camera_Idle;	
                        break;						
                    }
			  
                    // when you sent the PARAM_EXT_ACK clear the update flag
                    sony_foc_mode.clr_update();

                    // show the mimic results for test
					//
                    // cli::tout << "iso " << sony_foc_mode.my_value << " prev " << sony_foc_mode.my_prev_value << "\n";
                }
            }
*/

            // ============================ Exposure Program Mode ========================================================
            //	
/*			
            if ((sony_expro.my_value != sony_expro.my_prev_value) && (actionState == Sony_Camera_Idle)) {
				
                if (actionState == Sony_Camera_Idle) {
                  actionState = Sony_Camera_Action_Init_EP;
			    }	
			}
            else if (sony_expro.my_value != sony_expro.my_prev_value) {
				
			    if ( not(actionState == Sony_Camera_Idle) ) { 
				
                    switch(actionState) 
			        {
				        case Sony_Camera_Action_Init_EP:
						{
                            auto ap_data = camera->GetExproMode();                                                                // invoke this on the camera object
                            cli::tout << "EP_Set " << std::get<0>(ap_data) << "\n";                                         // this is the 1st string being printed
                            cli::tout << "EP_Val " << std::get<2>(ap_data) << "\n";                                         // this is the 2nd string being printed   
				            if (std::get<2>(ap_data) == sony_expro.my_value) {                                                    // value match already by manual intervention
                               cli::tout << "\033[31m expsosure program request already matched the value \033[0m" << sony_expro.my_value << "\n";
                               sony_expro.add_new_value();					  
                               actionState = Sony_Camera_Idle;
				            }
					        else {
                               cli::tout << "\033[32m ep request being made for \033[0m" << sony_expro.my_value << "\n";
						       actionState = Sony_Camera_Set_Begin_EP;
						       t_start = std::chrono::high_resolution_clock::now();
					        }
						}
                        break;

					    case Sony_Camera_Set_Begin_EP:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[36m time waiting : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						       cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						       actionState = Sony_Camera_Set_EP;	
                            }
						}
                        break;
						
                        case Sony_Camera_Set_EP:	
                        {				
                            cli::tout << " set cam ep " << "\n";		
			                std::stringstream ss_stream1;
                            std::string cam_enum;
                            //ss_stream1 << sony_expro.my_value;
                            ss_stream1 << enumerate_ex_pro_sony_a7(sony_expro.my_value);
                            ss_stream1 >> cam_enum;
                            cli::tout << "\033[32m setting ep \033[0m" << cam_enum << "\n";
                            if (camera->SetExposureProgramModeArgs( cam_enum ) == 1) {
                                t_start = std::chrono::high_resolution_clock::now();
			                    actionState = Sony_Camera_Set_Wait_EP;
                            }
                            else {
                               // if the action was unsuccessful
                               cli::tout << "\033[31m action unsuccesful for ep \033[0m" << "\n";
                               sony_expro.clr_new_req();
						       actionState = Sony_Camera_Idle;
                            }
						}
						break;
					  
					    case Sony_Camera_Set_Wait_EP:
						{
					        t_end = std::chrono::high_resolution_clock::now();
						    tdiff = std::chrono::duration<double, std::milli>(t_end-t_start).count();
                            //cli::tout << "\033[36m time waiting : \033[0m" << std::chrono::duration<double, std::milli>(t_end-t_start).count() <<  "\n";
						    //cli::tout << "\033[34m time waiting 2 : \033[0m" << tdiff <<  "\n";
						    if (tdiff > 1000.0) {
						        cli::tout << "\033[32m waited long enough \033[0m" << tdiff << "\n";
						        actionState = Sony_Camera_Check_EP;	
                            }
						}
                        break;						
					  
					    case Sony_Camera_Check_EP:
						{
					        auto ap_data = camera->GetExproMode();            // invoke this on the camera object
                            cli::tout << "EPSet " << std::get<0>(ap_data) << "\n";   // this is the 1st string being printed
                            cli::tout << "EPVal " << std::get<2>(ap_data) << "\n";   // this is the 2nd string being printed
                            // if the action was successful
                            cli::tout << "requested ep " << sony_expro.my_value << "\n";

						    if (std::get<2>(ap_data) == sony_expro.my_value) {
                                sony_expro.add_new_value();
						    } 
						    actionState = Sony_Camera_Idle;
                        }							
					    break;
						
						default:
						actionState = Sony_Camera_Idle;	
                        break;						
                    }
			  
                    // when you sent the PARAM_EXT_ACK clear the update flag
                    sony_expro.clr_update();

                    // show the mimic results for test
					//
                    // cli::tout << "iso " << sony_expro.my_value << " prev " << sony_expro.my_prev_value << "\n";
                }
            }
*/			
			
            } // $$$$$$$$$$$$$$$$$$$$$$$$$$$ for ever

/* =========%%%%%=========== old multi-threaded code which need to be re-written 
			
            // now chnage the setting and do it again  this would be over mavlink but this is a test stub
            //

            sony_aper.add_new_req(1800);
            if (sony_aper.my_value != sony_aper.my_prev_value) {

              std::stringstream ss_stream1;
              std::string cam_enum_aper1;
              ss_stream1 << enumerate_aperture_sony_a7(sony_aper.my_value);
              ss_stream1 >> cam_enum_aper1;
              cli::tout << "\033[32m setting aperture \033[0m" << cam_enum_aper1 << "\n";
              auto ap_data = camera->GetAperture();            // invoke this on the camera object
			  stringstream strstr;    
              strstr << std::get<1>(ap_data); int w_prot; strstr >> w_prot;
              cli::tout << "ApertureSet " << std::get<0>(ap_data) << "\n";   // this is the 1st string being printed
              cli::tout << "ApertureWriteProtect " << w_prot << "\n";   // this is the 2nd string being printed
              cli::tout << "ApertureVal " << std::get<2>(ap_data) << "\n";   // this is the 2nd string being printed   
              if (w_prot == 1) {
                 cli::tout << "aperture is write protected " << "\n";
				 sony_aper.clr_new_req();
              }
              else {  
                  if (camera->SetApertureArgs( cam_enum_aper1 ) == 1) {
                      sleep(2);
                      // here we are assuming change properties updated with load_properties and we just get the values
                      //
                      ap_data = camera->GetAperture();            // invoke this on the camera object
                      cli::tout << "ApertureSet " << std::get<0>(ap_data) << "\n";   // this is the 1st string being printed
                      cli::tout << "ApertureWriteProtect " << std::get<1>(ap_data) << "\n";   // this is the 2nd string being printed
                      cli::tout << "ApertureVal " << std::get<2>(ap_data) << "\n";   // this is the 2nd string being printed
                      // if the action was successful
                      sony_aper.add_new_value();
                  }
                  else {
                     // if the action was unsuccessful
                     cli::tout << "action unsuccesful " << "\n";
                     sony_aper.clr_new_req();
                  }
              }
              // when you sent the PARAM_EXT_ACK clear the update flag
              sony_aper.clr_update();

              // show the mimic results for test
              cli::tout << "aper " << sony_aper.my_value << " prev " << sony_aper.my_prev_value << "\n";
            }

            sony_aper.add_new_req(560);

            // add a new iso request which needs enumeration
            //
            sony_iso.add_new_req(8000);
            if (sony_iso.my_value != sony_iso.my_prev_value) {

              std::stringstream ss_stream1;
              std::string cam_enum_iso;
              ss_stream1 << enumerate_iso_sony_a7(sony_iso.my_value);
              ss_stream1 >> cam_enum_iso;
              cli::tout << "\033[32m setting iso \033[0m" << cam_enum_iso << "\n";
              auto is_data = camera->GetIso();            // invoke this on the camera object
			  stringstream strstr;    
              strstr << std::get<1>(is_data); int w_prot; strstr >> w_prot;
              cli::tout << "IsoSet " << std::get<0>(is_data) << "\n";   // this is the 1st string being printed
              cli::tout << "IsoWriteProtect " << w_prot << "\n";   // this is the 2nd string being printed
              cli::tout << "IsoVal " << std::get<2>(is_data) << "\n";   // this is the 3rd string being printed   
              if (w_prot == 1) {
                 cli::tout << "iso is write protected " << "\n";
				 sony_iso.clr_new_req();
              }
              else {  
                  if (camera->SetIsoArgs( cam_enum_iso ) == 1) {
                      sleep(2);
                      // here we are assuming change properties updated with load_properties and we just get the values
                      //
                      is_data = camera->GetIso();            // invoke this on the camera object
                      cli::tout << "IsoSet " << std::get<0>(is_data) << "\n";   // this is the 1st string being printed
                      //cli::tout << "IsoWriteProtect " << std::get<1>(is_data) << "\n";   // this is the 2nd string being printed
                      cli::tout << "IsoVal " << std::get<2>(is_data) << "\n";   // this is the 3rd string being printed
                      // if the action was successful
                      sony_iso.add_new_value();
                  }
                  else {
                     // if the action was unsuccessful
                     cli::tout << "action unsuccesful " << "\n";
                     sony_iso.clr_new_req();
                  }
              }
              // when you sent the PARAM_EXT_ACK clear the update flag
              sony_iso.clr_update();

              // show the mimic results for test
              cli::tout << "iso " << sony_iso.my_value << " prev " << sony_iso.my_prev_value << "\n";
            }
			
            // add a new shutter speed request which needs enumeration
            //
            sleep(1);
            sony_ss.add_new_req(5242890);
            if (sony_ss.my_value != sony_ss.my_prev_value) {

              std::stringstream ss_stream1;
              std::string cam_enum_ss;
              ss_stream1 << enumerate_shutter_sony_a7(sony_ss.my_value);
              ss_stream1 >> cam_enum_ss;
              cli::tout << "\033[32m setting shutter speed \033[0m" << cam_enum_ss << "\n";
              auto ss_data = camera->GetShutterSpeed();                           // invoke this on the camera object
			  stringstream strstr;    
              strstr << std::get<1>(ss_data); int w_prot; strstr >> w_prot;
              cli::tout << "SSSet " << std::get<0>(ss_data) << "\n";              // this is the 1st string being printed
              cli::tout << "SSWriteProtect " << w_prot << "\n";     // this is the 2nd string being printed
              cli::tout << "SSVal " << std::get<2>(ss_data) << "\n";              // this is the 3rd string being printed   
              if (w_prot == 1) {
                 cli::tout << "shutter speed is write protected " << "\n";
				 sony_ss.clr_new_req();
              }
              else {  
                  if (camera->SetShutterSpeedArgs( cam_enum_ss ) == 1) {
                      sleep(2);
                      // here we are assuming change properties updated with load_properties and we just get the values
                      //
                      ss_data = camera->GetShutterSpeed();                             // invoke this on the camera object
                      cli::tout << "SSSet " << std::get<0>(ss_data) << "\n";           // this is the 1st string being printed
                      cli::tout << "SSWriteProtect " << std::get<1>(ss_data) << "\n";  // this is the 2nd string being printed
                      cli::tout << "SSVal " << std::get<2>(ss_data) << "\n";           // this is the 3rd string being printed
                      // if the action was successful
                      sony_ss.add_new_value();
                  }
                  else {
                     // if the action was unsuccessful
                     cli::tout << "shut speed action unsuccesful " << "\n";
                     sony_ss.clr_new_req();
                  }
              }
              // when you sent the PARAM_EXT_ACK clear the update flag
              sony_ss.clr_update();

              // show the mimic results for test
              cli::tout << "ss " << sony_ss.my_value << " prev " << sony_ss.my_prev_value << "\n";
            }

            sleep(1);
            sony_expro.add_new_req(32851);
            if (sony_expro.my_value != sony_expro.my_prev_value) {

              std::stringstream ss_stream1;
              std::string cam_enum_ex;
              ss_stream1 << enumerate_ex_pro_sony_a7(sony_expro.my_value);
              ss_stream1 >> cam_enum_ex;
              cli::tout << "\033[32m setting expro \033[0m" << cam_enum_ex << "\n";
              auto ex_data = camera->GetExproMode();                                 // invoke this on the camera object
			  stringstream strstr;    
              strstr << std::get<1>(ex_data); int w_prot; strstr >> w_prot;
              cli::tout << "ExProSet " << std::get<0>(ex_data) << "\n";                 // this is the 1st string being printed
              cli::tout << "ExProWriteProtect " << w_prot << "\n";        // this is the 2nd string being printed
              cli::tout << "ExProVal " << std::get<2>(ex_data) << "\n";                 // this is the 3rd string being printed   
              if (w_prot == 1) {
                 cli::tout << "expro is write protected " << "\n";
				 sony_expro.clr_new_req();
              }
              else {  
                  if (camera->SetExposureProgramModeArgs( cam_enum_ex ) == 1) {
                      sleep(2);
                      // here we are assuming change properties updated with load_properties and we just get the values
                      //
                      ex_data = camera->GetExproMode();                                // invoke this on the camera object
                      cli::tout << "ExProSet " << std::get<0>(ex_data) << "\n";           // this is the 1st string being printed
                      //cli::tout << "ExProWriteProtect " << std::get<1>(ex_data) << "\n";  // this is the 2nd string being printed
                      cli::tout << "ExProVal " << std::get<2>(ex_data) << "\n";           // this is the 3rd string being printed
                      // if the action was successful
                      sony_expro.add_new_value();
                  }
                  else {
                     // if the action was unsuccessful
                     cli::tout << "action unsuccesful " << "\n";
                     sony_expro.clr_new_req();
                  }
              }
              // when you sent the PARAM_EXT_ACK clear the update flag
              sony_expro.clr_update();

              // show the mimic results for test
              cli::tout << "ex pro " << sony_expro.my_value << " prev " << sony_expro.my_prev_value << "\n";
            }

            sleep(1);
            sony_foc_mode.add_new_req(4);
            if (sony_foc_mode.my_value != sony_foc_mode.my_prev_value) {

              std::stringstream ss_stream1;
              std::string cam_enum_fm;
              ss_stream1 << enumerate_focus_sony_a7(sony_foc_mode.my_value);
              ss_stream1 >> cam_enum_fm;
              cli::tout << "\033[32m setting focus mode \033[0m" << cam_enum_fm << "\n";
              auto fm_data = camera->GetFocusMode();                                 // invoke this on the camera object
			  stringstream strstr;    
              strstr << std::get<1>(fm_data); int w_prot; strstr >> w_prot;
              cli::tout << "FocusModeSet " << std::get<0>(fm_data) << "\n";                 // this is the 1st string being printed
              cli::tout << "FocusModeWriteProtect " << w_prot << "\n";        // this is the 2nd string being printed
              cli::tout << "FocusModeVal " << std::get<2>(fm_data) << "\n";                 // this is the 3rd string being printed   
              if (w_prot == 1) {
                 cli::tout << "fcosu mode is write protected " << "\n";
				 sony_foc_mode.clr_new_req();
              }
              else {  
                  if (camera->SetFocusModeArgs( cam_enum_fm ) == 1) {
                      sleep(2);
                      // here we are assuming change properties updated with load_properties and we just get the values
                      //
                      fm_data = camera->GetFocusMode();                                // invoke this on the camera object
                      cli::tout << "FocusModeSet " << std::get<0>(fm_data) << "\n";           // this is the 1st string being printed
                      cli::tout << "FocusModeWriteProtect " << std::get<1>(fm_data) << "\n";  // this is the 2nd string being printed
                      cli::tout << "FocusModeVal " << std::get<2>(fm_data) << "\n";           // this is the 3rd string being printed
                      // if the action was successful
                      sony_foc_mode.add_new_value();
                  }
                  else {
                     // if the action was unsuccessful
                     cli::tout << "action unsuccesful " << "\n";
                     sony_foc_mode.clr_new_req();
                  }
              }
              // when you sent the PARAM_EXT_ACK clear the update flag
              sony_foc_mode.clr_update();

              // show the mimic results for test
              cli::tout << "focus mode " << sony_foc_mode.my_value << " prev " << sony_foc_mode.my_prev_value << "\n";
            }

            sleep(1);
            sony_foc_area.add_new_req(6);
            if (sony_foc_area.my_value != sony_foc_area.my_prev_value) {

              std::stringstream ss_stream1;
              std::string cam_enum_fa;
              ss_stream1 << enumerate_focus_area_sony_a7(sony_foc_area.my_value);
              ss_stream1 >> cam_enum_fa;
              cli::tout << "\033[32m setting focus area \033[0m" << cam_enum_fa << "\n";
              auto fa_data = camera->GetFocusArea();                                 // invoke this on the camera object
			  stringstream strstr;    
              strstr << std::get<1>(fa_data); int w_prot; strstr >> w_prot;
              cli::tout << "FocusAreaSet " << std::get<0>(fa_data) << "\n";                 // this is the 1st string being printed
              cli::tout << "FocusAreaWriteProtect " << w_prot << "\n";        // this is the 2nd string being printed
              cli::tout << "FocusAreaVal " << std::get<2>(fa_data) << "\n";                 // this is the 3rd string being printed   
              if (w_prot == 1) {
                 cli::tout << "focus area is write protected " << "\n";
				 sony_foc_area.clr_new_req();
              }
              else {  
                  if (camera->SetFocusAreaArgs( cam_enum_fa ) == 1) {
                      sleep(2);
                      // here we are assuming change properties updated with load_properties and we just get the values
                      //
                      fa_data = camera->GetFocusArea();                                // invoke this on the camera object
                      cli::tout << "FocusAreaSet " << std::get<0>(fa_data) << "\n";           // this is the 1st string being printed
                      cli::tout << "FocusAreaWriteProtect " << std::get<1>(fa_data) << "\n";  // this is the 2nd string being printed
                      cli::tout << "FocusAreaVal " << std::get<2>(fa_data) << "\n";           // this is the 3rd string being printed
                      // if the action was successful
                      sony_foc_area.add_new_value();
                  }
                  else {
                     // if the action was unsuccessful
                     cli::tout << "action unsuccesful " << "\n";
                     sony_foc_area.clr_new_req();
                  }
              }
              // when you sent the PARAM_EXT_ACK clear the update flag
              sony_foc_area.clr_update();

              // show the mimic results for test
              cli::tout << "focus area " << sony_foc_area.my_value << " prev " << sony_foc_area.my_prev_value << "\n";
            }

            sleep(1);
            sony_white_bal.add_new_req(36);
            if (sony_white_bal.my_value != sony_white_bal.my_prev_value) {

              std::stringstream ss_stream1;
              std::string cam_enum_wb;
              ss_stream1 << enumerate_white_bal_sony_a7(sony_white_bal.my_value);
              ss_stream1 >> cam_enum_wb;
              cli::tout << "\033[32m setting white balance \033[0m" << cam_enum_wb << "\n";
              auto wb_data = camera->GetWhiteBalance();                                 // invoke this on the camera object
			  stringstream strstr;    
              strstr << std::get<1>(wb_data); int w_prot; strstr >> w_prot;
              cli::tout << "WhiteBalanceSet " << std::get<0>(wb_data) << "\n";                 // this is the 1st string being printed
              cli::tout << "WhiteBalanceWriteProtect " << w_prot << "\n";        // this is the 2nd string being printed
              cli::tout << "WhiteBalanceVal " << std::get<2>(wb_data) << "\n";                 // this is the 3rd string being printed   
              if (w_prot == 1) {
                 cli::tout << "white balance is write protected " << "\n";
				 sony_white_bal.clr_new_req();
              }
              else {  
                  if (camera->SetWhiteBalanceArgs( cam_enum_wb ) == 1) {
                      sleep(2);
                      // here we are assuming change properties updated with load_properties and we just get the values
                      //
                      wb_data = camera->GetWhiteBalance();                                // invoke this on the camera object
                      cli::tout << "WhiteBalanceSet " << std::get<0>(wb_data) << "\n";           // this is the 1st string being printed
                      //cli::tout << "WhiteBalanceWriteProtect " << std::get<1>(wb_data) << "\n";  // this is the 2nd string being printed
                      cli::tout << "WhiteBalanceVal " << std::get<2>(wb_data) << "\n";           // this is the 3rd string being printed
                      // if the action was successful
                      sony_white_bal.add_new_value();
                  }
                  else {
                     // if the action was unsuccessful
                     cli::tout << "action unsuccesful " << "\n";
                     sony_white_bal.clr_new_req();
                  }
              }
              // when you sent the PARAM_EXT_ACK clear the update flag
              sony_white_bal.clr_update();

              // show the mimic results for test
              cli::tout << "white balance " << sony_white_bal.my_value << " prev " << sony_white_bal.my_prev_value << "\n";
            }

            ================%%%%%====================== end of old code */
			
            //}  ===============================================>> end of for loop repeat <<====================================================================================

            //else if (action == TEXT("6")) { /* ISO */
                //sleep(5);
                //camera->get_iso();
                //sleep(5);
                //camera->set_iso_args( input );
                //sleep(5);
                //camera->get_iso();
            //}
            //else if (action == TEXT("7")) { /* Shutter Speed */
                //sleep(5);
                //camera->get_shutter_speed();
                //camera->set_shutter_speed_args( input );
                //sleep(5);
                //camera->get_shutter_speed();
            //}
            //else if (action == TEXT("8")) { /* Live View */
            //    camera->get_live_view();
            //}
            //else if (action == TEXT("9")) { /* Live View Image Quality */
            //    camera->get_live_view_image_quality();
            //    camera->set_live_view_image_quality();
            //}
            //else if (action == TEXT("10")) { /* Live View Image Status */
            //    camera->get_live_view_status();
            //    camera->set_live_view_status();
            //}
            //else if (action == TEXT("a")) { /* Position Key Setting */
            //    camera->get_position_key_setting();
            //    camera->set_position_key_setting();
            //}
            //else if (action == TEXT("b")) { /* Exposure Program Mode */
            //sleep(5);
            //camera->get_exposure_program_mode();
            //sleep(5);
            //camera->set_exposure_program_mode_args( input );
            //sleep(5);
            //camera->get_exposure_program_mode();
            //}
            //else if (action == TEXT("c")) { /* Still Capture Mode(Drive mode) */
            //  sleep(5);
            //  camera->get_still_capture_mode();
            //  camera->set_still_capture_mode_args( input );
            //  sleep(5);
            //  camera->get_still_capture_mode();
            //}
            //else if (action == TEXT("d")) { /* Focus Mode */
            //  sleep(5);
            //  camera->get_focus_mode();
            //  sleep(5);
            //  camera->set_focus_mode_args( input );
            //  sleep(5);
            //  camera->get_focus_mode();
            //}
            //else if (action == TEXT("e")) { /* Focus Area */
            //    sleep(5);
            //    camera->get_focus_area();
            //    camera->set_focus_area();
            //}
            //else if (action == TEXT("11")) { /* FELock */
            //    cli::tout << "Flash device required.";
            //    camera->execute_lock_property((CrInt16u)SDK::CrDevicePropertyCode::CrDeviceProperty_FEL);
            //}
            //else if (action == TEXT("12")) { /* AWBLock */
            //    camera->execute_lock_property((CrInt16u)SDK::CrDevicePropertyCode::CrDeviceProperty_AWBL);
            //}
            //else if (action == TEXT("13")) { /* AF Area Position(x,y) */
            //    camera->set_af_area_position();
            //}
            //else if (action == TEXT("14")) { /* Selected MediaFormat */
            //    camera->get_select_media_format();
            //    camera->set_select_media_format();
            //}
            //else if (action == TEXT("15")) { /* Movie Rec Button */
            //  sleep(5);
            //  camera->execute_movie_rec();
            //}
            //else if (action == TEXT("16")) { /* White Balance */
            //  sleep(5);
            //  camera->get_white_balance();
            //  camera->set_white_balance_args( input );
            //  sleep(5);
            //  camera->get_white_balance();
            //}
            //else if (action == TEXT("17")) { /* Custom WB */
            //    camera->get_custom_wb();
            //    camera->set_custom_wb();
            //}
            //else if (action == TEXT("18")) { /* Zoom Operation */
            //    camera->get_zoom_operation();
            //    camera->set_zoom_operation();
            //}
#if defined(LIVEVIEW_ENB)
            //else if (action == TEXT("lv")) { /* LiveView Enable */
            //    camera->change_live_view_enable();
            //}
#endif
        //}
        //cli::tout << '\n';
    //}

    // now disconnect the device
    //
    CameraDeviceList::const_iterator it = cameraList.begin();
    for (std::int32_t j = 0; it != cameraList.end(); ++j, ++it) {
         if ((*it)->is_connected()) {
             //cli::tout << "Initiate disconnect sequence.\n";
             auto disconnect_status = (*it)->disconnect();
             if (!disconnect_status) {
                 // try again
                 disconnect_status = (*it)->disconnect();
             }
             if (!disconnect_status)
               cli::tout << "Disconnect failed to initiate.\n";
             //else
             //  cli::tout << "Disconnect successfully initiated!\n\n";
         }
         (*it)->release();
    }

    //cli::tout << "Release SDK resources.\n";
    // cr_lib->Release();
    SDK::Release();

    // cli::free_cr_lib(&cr_lib);

    //cli::tout << "Exiting application.\n";
    std::exit(EXIT_SUCCESS);
}

void mavlink_communicator()
{
    static int cnt2 = 0;
    while(isRuning)
    {
        //cout << "\tfunc2:" << ++cnt2 << endl;
        sleep(2);
        //sony_aper.add_new_req((std::uint32_t)cnt2);
        if ((cnt2 % 10) == 0)  cnt2 = 0;
    }
    sleep(3);
}
void mavlink_heartbeat()
{
    static int cnt2 = 0;
    while(isRuning)
    {
        cout << "\theartbeat:" << ++cnt2 << endl;
        sleep(1);
    }
    sleep(3);
}
/*
int main()
{
    // start your threads here
    boost::thread thread1(&cam_main);
//    boost::thread thread2(&mavlink_communicator);
//    boost::thread thread3(&mavlink_heartbeat);
    system("read");
    // tell the threads to complete using the global
    isRuning = false;
    // wait for the threads here
//    thread3.join();
//    thread2.join();
    thread1.join();
    cout << "exit" << endl;
    return 0;
}
*/
