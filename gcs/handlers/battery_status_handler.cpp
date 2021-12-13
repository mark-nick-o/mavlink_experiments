#include "battery_status_handler.hpp"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

using namespace domain;

BattStatHandler::BattStatHandler(MavLinkCommunicator* communicator,
                                         GcsModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40); // 25 Hz
}

void BattStatHandler::processMessage(const mavlink_message_t& message)
{
    if (message.msgid != MAVLINK_MSG_ID_BATTERY_STATUS ||
        message.sysid == 0) return;

    mavlink_battery_status_t bs;
    mavlink_msg_battery_status_decode(&message, &bs);

    m_battery_remain = bs.battery_remaining;
    qDebug() << "current : " << bs.current_consumed
             << "energy : " << bs.energy_consumed
	     << "remaining : " << bs.battery_remaining
             << "temperature : " << bs.temperature;
}
