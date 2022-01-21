#include "camera_status_data.h"
#include "send_camera_info_handler.hpp"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendCameraInfoHandler::SendCameraInfoHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40); // 25 Hz
}

void SendCameraInfoHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

void SendCameraInfoHandler::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)

    if ((m_model->get_substate() == DO_SENDING_ACK) && (m_model->get_sendState() == SENS_CI))
    {
        std::uint16_t len=0u;
        mavlink_message_t message;
        mavlink_camera_information_t com;                                                                   /* Command Type */

        //m_sendState = SEND_CI;
        /*
            now get the data from the camera 
            com = getInfoDataFromCam();
            if (com.reqfailure == 1)
            {
                m_reject |= CI_FAIL_BIT;
            }
            else
            {
                << code as below success ...... >>
            }
           for the purpose of testing we are jsut filling in the values here 
        */    
        com.time_boot_ms = 65321;                                                                                  /*< [ms] Timestamp (time since system boot).*/
        com.firmware_version = 10000;                                                                              /*<  Version of the camera firmware (v << 24 & 0xff = Dev, v << 16 & 0xff = Patch, v << 8 & 0xff = Minor, v & 0xff = Major)*/
        com.focal_length = 1.4;                                                                                    /*< [mm] Focal length*/
        com.sensor_size_h = 600.0;                                                                                 /*< [mm] Image sensor size horizontal*/
        com.sensor_size_v = 300.0;                                                                                 /*< [mm] Image sensor size vertical*/
        com.flags = 123;                                                                                           /*<  Bitmap of camera capability flags.*/
        com.resolution_h = 100;                                                                                    /*< [pix] Horizontal image resolution*/
        com.resolution_v = 200;                                                                                    /*< [pix] Vertical image resolution*/
        com.cam_definition_version = 250;                                                                          /*<  Camera definition version (iteration)*/
        memcpy(&com.vendor_name[0],"sony", 4);                                                                       /*<  Name of the camera vendor*/
        memcpy(&com.model_name[0], "alpha", 5);                                                                   /*<  Name of the camera model*/
        com.lens_id = 12;                                                                             /*<  Reserved for a lens ID*/
        strcpy(com.cam_definition_uri, "http:121.1.2.4/cam_pics/1.jpg"); 

        len = mavlink_msg_camera_information_encode(m_communicator->systemId(), m_communicator->componentId(), &message, &com);

        m_communicator->sendMessageOnLastReceivedLink(message);
        //m_sendState = SENT_CI;
    }
}
