#include "send_camera_image_captured_handler.hpp"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendCameraImageCapturedHandler::SendCameraImageCapturedHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40);                                                                       // 25 Hz
}

void SendCameraImageCapturedHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

void SendCameraImageCapturedHandler::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)

    if ((m_substate == DO_SENDING_ACK) && (m_sendState == SENS_CIC))
    {
        std::uint16_t len=0u;
        mavlink_message_t message;
        mavlink_camera_image_captured_t com = NULL;                                       /*< Command Type */

        m_sendState = SEND_CIC;
        /*
            now get the data from the camera 
	    if (m_missing_image_index != 0)   // we requested a specific lost image
	    {
	       // com = getImageNoFromCam(m_missing_image_index);
	       m_missing_image_index = 0;
	    }
	    else
	    {
                // com = getCamImgCapDataFromCam();
	    }
            if (com.reqfailure == 1)
            {
                m_reject |= CIC_FAIL_BIT;
		!!!!! CHECK !!!!! if you want to still send message then set this not sure you should just the error ACK message above com.status = STORAGE_STATUS_NOT_SUPPORTED;
            }
            else
            {
                << code as below success ...... >>
            }
            for the purpose of testing we are just filling in the values here 
        */ 

        com.time_utc = 667700; /*< [us] Timestamp (time since UNIX epoch) in UTC. 0 for unknown.*/
        com.time_boot_ms = 54321; /*< [ms] Timestamp (time since system boot).*/
        com.lat = 30; /*< [degE7] Latitude where image was taken*/
        com.lon = 40; /*< [degE7] Longitude where capture was taken*/
        com.alt = 11; /*< [mm] Altitude (MSL) where image was taken*/
        com.relative_alt = 12; /*< [mm] Altitude above ground*/
        com.q[0] = 1; /*<  Quaternion of camera orientation (w, x, y, z order, zero-rotation is 0, 0, 0, 0)*/
        com.q[1] = 4;
        com.q[2] = 4;
        com.q[3] = 2;
        com.image_index = 4; /*<  Zero based index of this image (image count since armed -1)*/
        com.camera_id = 1; /*<  Camera ID (1 for first, 2 for second, etc.)*/
        com.capture_result = 1; /*<  Boolean indicating success (1) or failure (0) while capturing this image.*/
        strcpy(&com.file_url,"http://10.1.2.3/img/1.jpg",strlen("http://10.1.2.3/img/1.jpg")); /*<  URL of image taken. Either local storage or http://foo.jpg if camera provides an HTTP interface.*/
 
        len = mavlink_msg_camera_image_captured_encode(m_communicator->systemId(), m_communicator->componentId(), &message, &com);

        m_communicator->sendMessageOnLastReceivedLink(message);
        m_sendState = SENT_CIC;
    }
}
