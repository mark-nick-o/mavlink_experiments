#include "heartbeat_handler.h"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

using namespace domain;

HeartHandler::HeartHandler(MavLinkCommunicator* communicator):
    AbstractHandler(communicator)
{}

void HeartHandler::processMessage(const mavlink_message_t& message)
{
    if (message.msgid != MAVLINK_MSG_ID_HEARTBEAT ||
        message.sysid == 0) return;

    mavlink_heartbeat_t heart;
    mavlink_msg_heartbeat_decode(&message, &heart);

    qDebug() << "pitch" << heart.mavlink_version;
    m_substate = HEART_RCV; 
    
}
