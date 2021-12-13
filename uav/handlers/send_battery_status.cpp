#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendBatterStatusHandler::SendBatterStatusHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40); // 25 Hz
}

void SendBatterStatusHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

/*
   send battery status message
*/
void SendBatterStatusHandler::sendBatteryStatusMAVLinkMessage( std::uint8_t target_sys, std::uint8_t target_comp )
{
  std::uint16_t len=0u;

  mavlink_battery_status_t com = NULL;                          // Command Type
  mavlink_message_t message;                                           
 
  com.target_system    = target_sys;
  com.target_component = target_comp;

  com.current_consumed = 1; /*< [mAh] Consumed charge, -1: autopilot does not provide consumption estimate*/
  com.energy_consumed = 21; /*< [hJ] Consumed energy, -1: autopilot does not provide energy consumption estimate*/
  com.temperature = 11; /*< [cdegC] Temperature of the battery. INT16_MAX for unknown temperature.*/
  com.voltages[0] = 11; /*< [mV] Battery voltage of cells. Cells above the valid cell count for this battery should have the UINT16_MAX value.*/
  com.voltages[1] = 18;
  com.current_battery = 4; /*< [cA] Battery current, -1: autopilot does not measure the current*/
  com.id = 5; /*<  Battery ID*/
  com.battery_function = 1; /*<  Function of the battery*/
  com.type = 5; /*<  Type (chemistry) of the battery*/
  com.battery_remaining = 7; /*< [%] Remaining battery energy. Values: [0-100], -1: autopilot does not estimate the remaining battery.*/
  com.time_remaining = 66; /*< [s] Remaining battery time, 0: autopilot does not provide remaining battery time estimate*/
  com.charge_state = 5; /*<  State for extent of discharge, provided by autopilot for warning or external reactions*/
 
  /* encode */
  len = mavlink_msg_battery_status_encode(target_sys, target_comp, &message, &com);
        m_communicator->sendMessageOnLastReceivedLink(message);
}

void SendBatterStatusHandler::timerEvent(QTimerEvent* event)
{
    SendBatterStatusHandler::sendBatteryStatusMAVLinkMessage( m_communicator->systemId(), m_communicator->componentId() );
}
