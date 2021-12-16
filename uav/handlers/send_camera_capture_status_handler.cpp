#include "send_camera_capture_status_handler.hpp"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendCameraCaptureStatusHandler::SendCameraCaptureStatusHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40);                                                                       // 25 Hz
}

void SendCameraCaptureStatusHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

void SendCameraCaptureStatusHandler::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)

    if ((m_substate == DO_SENDING_ACK) && (m_sendState == SENS_CCS))
    {
        std::uint16_t len=0u;
        mavlink_message_t message;
        mavlink_camera_capture_status_t com = NULL;                                       /*< Command Type */

        m_sendState = SEND_CCS;
        /*
            now get the data from the camera 
            com = getCamCapStatDataFromCam();
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

        com.time_boot_ms = 11111; /*< [ms] Timestamp (time since system boot).*/
        com.image_interval = 3.3f; /*< [s] Image capture interval*/
        com.recording_time_ms = 10000; /*< [ms] Time since recording started*/
        com.available_capacity = 0.34f; /*< [MiB] Available storage capacity.*/
        com.image_status = 1; /*<  Current status of image capturing (0: idle, 1: capture in progress, 2: interval set but idle, 3: interval set and capture in progress)*/
        com.video_status = 1; /*<  Current status of video capturing (0: idle, 1: capture in progress)*/
        com.image_count = m_count_of_images;
	    
        len = mavlink_msg_camera_capture_status_encode(m_communicator->systemId(), m_communicator->componentId(), &message, &com);

        m_communicator->sendMessageOnLastReceivedLink(message);
        m_sendState = SENT_CCS;
    }
}
