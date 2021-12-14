#include "heartbeat_handler.hpp"
#include "camera_data.h"

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
    this->startTimer(40); // 25 Hz
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

void SendHeartBeatHandler::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)

    // reset the heartbeat state
    //
    m_sendState = GO_IDLE;     
  
    // we are mot sending heartbeats out of the gcs 
    //
    // mavlink_message_t message;
    // mavlink_heartbeat_t heartbeat;
    // heartbeat.type = 1;

    // mavlink_msg_heartbeat_encode(m_communicator->systemId(), m_communicator->componentId(), &message, &heartbeat);

    // m_communicator->sendMessageOnLastReceivedLink(message);
}
