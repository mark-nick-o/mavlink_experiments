#include "send_heartbeat_handler.hpp"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

using namespace domain;

SendHeartBeatHandler::SendHeartBeatHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40); // 25 Hz
}

void SendHeartBeatHandler::processMessage(const mavlink_message_t& message)
{
    if (message.msgid != MAVLINK_MSG_ID_HEARTBEAT) return;
    
    mavlink_heartbeat_t heartbeat; // heartbeat type
    mavlink_msg_heartbeat_decode(&message, &heartbeat); // decode it
    
    // print it
    qDebug() << "Heartbeat received, system type:" << heartbeat.type;
}

void SendHeartBeatHandler::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)

    mavlink_message_t message;
    mavlink_heartbeat_t heartbeat;
    heartbeat.type = 1;

    mavlink_msg_heartbeat_encode(m_communicator->systemId(), m_communicator->componentId(), &message, &heartbeat);

    m_communicator->sendMessageOnLastReceivedLink(message);
}
