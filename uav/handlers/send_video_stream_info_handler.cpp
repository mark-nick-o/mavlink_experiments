#include "send_video_stream_info_handler.hpp"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendVideoStreamInfoHandler::SendVideoStreamInfoHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40);                                                                       // 25 Hz
}

void SendVideoStreamInfoHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

void SendVideoStreamInfoHandler::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)

    if ((m_substate == DO_SENDING_ACK) && (m_sendState == SENS_VS))
    {
        std::uint16_t len=0u;
        mavlink_message_t message;
        mavlink_video_stream_information_t com = NULL;                                       /*< Command Type */

        m_sendState = SEND_VS;
        /*
            now get the data from the camera 
            com = getVideoStreamDataFromCam();
            if (com.reqfailure == 1)
            {
                m_reject |= VS_FAIL_BIT;
				!!!!! CHECK !!!!! if you want to still send message then set this not sure you should just the error ACK message above com.status = STORAGE_STATUS_NOT_SUPPORTED;
            }
            else
            {
                << code as below success ...... >>
            }
            for the purpose of testing we are just filling in the values here 
        */ 

        com.framerate = 30.0f; /*< [Hz] Frame rate.*/
        com.bitrate = 3000; /*< [bits/s] Bit rate.*/
        com.flags = 3; /*<  Bitmap of stream status flags.*/
        com.resolution_h = 300; /*< [pix] Horizontal resolution.*/
        com.resolution_v = 400; /*< [pix] Vertical resolution.*/
        com.rotation = 90; /*< [deg] Video image rotation clockwise.*/
        com.hfov = 45; /*< [deg] Horizontal Field of view.*/
        com.stream_id = 2; /*<  Video Stream ID (1 for first, 2 for second, etc.)*/
        com.count = 4; /*<  Number of streams available.*/
        com.type = ; /*<  Type of stream.*/
        strcpy(&com.name,"vid01",5); /*<  Stream name.*/
        strcpy(&com.uri,"http://10.1.2.4/vids/01.mov",strlen("http://10.1.2.4/vids/01.mov")); /*<  Video stream URI (TCP or RTSP URI ground station should connect to) or port number (UDP port ground station should listen to).*/
 
        len = mavlink_msg_video_stream_information_encode(m_communicator->systemId(), m_communicator->componentId(), &message, &com);

        m_communicator->sendMessageOnLastReceivedLink(message);
        m_sendState = SENT_VS;
    }
}
