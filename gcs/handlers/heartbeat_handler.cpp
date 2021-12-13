#include "heartbeat_handler.h"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

using namespace domain;

HeartHandler::HeartHandler(MavLinkCommunicator* communicator,
                                         GcsModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    // so far we dont send it back so this is out this->startTimer(40); // 25 Hz
}

void HeartHandler::processMessage(const mavlink_message_t& message)
{
    if (message.msgid != MAVLINK_MSG_ID_HEARTBEAT ||
        message.sysid == 0) return;

    mavlink_heartbeat_t heart;
    mavlink_msg_heartbeat_decode(&message, &heart);

    qDebug() << "pitch" << heart.mavlink_version;
    m_sendState = HEART_RCV;     
}
