#include "camera_status_data.h"
#include "send_camera_storage_info_handler.hpp"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendCameraStorageInfoHandler::SendCameraStorageInfoHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40);                                                                       // 25 Hz
}

void SendCameraStorageInfoHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

void SendCameraStorageInfoHandler::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)

    if ((m_model->get_substate() == DO_SENDING_ACK) && (m_model->get_sendState() == SENS_SI))
    {
        std::uint16_t len=0u;
        mavlink_message_t message;
        mavlink_storage_information_t com;                                       /*< Command Type */

        //m_sendState = SEND_SI;
        /*
            now get the data from the camera 
            com = getSettingsDataFromCam();
            if (com.reqfailure == 1)
            {
                m_reject |= CS_FAIL_BIT;
				        !!!!! CHECK !!!!! if you want to still send message then set this not sure you should just the error ACK message above com.status = STORAGE_STATUS_NOT_SUPPORTED;
            }
            else
            {
                << code as below success ...... >>
            }
            for the purpose of testing we are just filling in the values here 
        */ 

        com.time_boot_ms = 7540u;                                                       /*<  [ms] Timestamp (time since system boot).*/
        com.total_capacity = 1.2f;                                                      /*<  [MiB] Total capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.*/
        com.used_capacity = 1.1f;                                                       /*<  [MiB] Used capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.*/
        com.available_capacity = 0.1f;                                                  /*<  [MiB] Available storage capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.*/
        com.read_speed = 0.67f;                                                         /*<  [MiB/s] Read speed.*/
        com.write_speed = 0.76f;                                                        /*<  [MiB/s] Write speed.*/
        com.storage_id = 1;                                                             /*<  Storage ID (1 for first, 2 for second, etc.)*/
        com.storage_count = 2;                                                          /*<  Number of storage devices*/
        com.status = STORAGE_STATUS_READY;                                              /*<  Status of storage*/
 
        /* else if unformatted media returned
		
        com.time_boot_ms = 7540u;                                                       
        com.storage_id = 1;                                                            
        com.storage_count = 2;                                                          
        com.status = STORAGE_STATUS_UNFORMATTED; 		
		*/
        len = mavlink_msg_storage_information_encode(m_communicator->systemId(), m_communicator->componentId(), &message, &com);

        m_communicator->sendMessageOnLastReceivedLink(message);
        //m_sendState = SENT_SI;
    }
}
