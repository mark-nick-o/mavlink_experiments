#include "gcs_model.h"

// Qt
#include <QDateTime>
#include <QtMath>
#include <QDebug>

namespace
{
    const int interval = 40; // 25 Hz
    const int timeFactor = 1000 / ::interval;

    int randNum(int min, int max)
    {
        return min + qrand() % (max - min);
    }
}

using namespace domain;

GcsModel::GcsModel(QObject* parent):
    QObject(parent),
    m_substate(0),
    m_sendState(0),
    m_focal_len(0),
    m_battery_remain(0)
{
    qsrand(QDateTime::currentMSecsSinceEpoch() / 1000);
    this->startTimer(::interval);
}

void GcsModel::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)

}

void GcsModel::set_substate(const std::int8_t& h)
{
    m_substate = h;
}

void GcsModel::set_sendState(const std::int8_t& h)
{
    m_sendState = h;
}

void GcsModel::set_cancelCmd(const std::uint16_t& h)
{
    m_cancel_cmd = h;
}

std::int8_t GcsModel::get_substate() const
{
    return m_substate;       
}

std::int8_t GcsModel::get_sendState() const
{
    return m_sendState;       
}

std::int8_t GcsModel::get_batteryRemain() const
{
    return m_battery_remain;       
}

std::float32_t GcsModel::get_focalLen() const
{
    return m_focal_len;       
}

std::uint16_t GcsModel::get_cancelCmd() const
{
    return m_cancel_cmd;       
}
