#include "send_camera_settings_handler.h"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendCameraSettingsHandler::SendCameraSettingsHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40); // 25 Hz
}

void SendCameraSettingsHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

void SendCameraSettingsHandler::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)

    if ((m_substate == DO_SENDING_ACK) && (m_sendState == SENS_CS))
    {
        std::uint16_t len=0u;
        mavlink_message_t message;
        mavlink_camera_settings_t com = NULL;                                                                   /* Command Type */

        m_sendState = SEND_CS;
        com.mode_id = 76;                                                               /*<  Camera mode*/
        com.zoomLevel = 2.43f;                                                           /*<  Current zoom level (0.0 to 100.0, NaN if not known)*/
        com.focusLevel = 1.9f;  

        len = mavlink_msg_camera_settings_encode(m_communicator->systemId(), m_communicator->componentId(), &message, &com);

        m_communicator->sendMessageOnLastReceivedLink(message);
        m_sendState = SENT_CS;
    }
}
