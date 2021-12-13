#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendVideoStreamHandler::SendVideoStreamHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40); // 25 Hz
}

void SendVideoStreamHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

void SendVideoStreamHandler::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)

    if ((m_substate == DO_SENDING_ACK) && (m_sendState == SENS_VS))
    {
        std::uint16_t len=0u;
        mavlink_message_t message;
        mavlink_video_stream_information_t com = NULL;                                                                   /* Command Type */

        m_sendState = SEND_VS;
        com.framerate = 30.2f;
        com.bitrate = 11;                                                              /*< [bits/s] Bit rate.*/
        com.flags = 4;                                                                 /*<  Bitmap of stream status flags.*/
        com.resolution_h = 300;                                                        /*< [pix] Horizontal resolution.*/
        com.resolution_v = 400;                                                        /*< [pix] Vertical resolution.*/
        com.rotation = 1;                                                              /*< [deg] Video image rotation clockwise.*/
        com.hfov = 34;                                                                 /*< [deg] Horizontal Field of view.*/
        com.stream_id = 3;                                                             /*<  Video Stream ID (1 for first, 2 for second, etc.)*/
        com.count = 99;                                                                /*<  Number of streams available.*/
        com.type = 2;                                                                  /*<  Type of stream.*/
        strcpy(&com.name,"stream 1!",strlen("stream1"));                               /*<  Stream name.*/
        strcpy(&com.uri,"http::/111.11.1.1/pics",strlen("http::/111.11.1.1/pics"));    /*<  Video stream URI (TCP or RTSP URI ground station should connect to) or port number (UDP port ground station should listen to).*/		

        len = mavlink_msg_video_stream_information_encode(m_communicator->systemId(), m_communicator->componentId(), &message, &com);

        m_communicator->sendMessageOnLastReceivedLink(message);
        m_sendState = SENT_VS;
    }
}
