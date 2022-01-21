#include "uav_model.h"

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

    float formatYaw(float angle)
    {
        return angle > 360 ? angle - 360 : (angle < 0 ? angle + 360 : angle);
    }

    float formatPitchRoll(float angle)
    {
        return angle > 45 ? 45 : (angle < -45 ? -45 : angle);
    }
}

using namespace domain;

UavModel::UavModel(QObject* parent):
    QObject(parent),
    m_pitch(::randNum(0, 600) * 0.1),
    m_roll(::randNum(-50, 50) * 0.1),
    m_yaw(::randNum(0, 360)),
    m_airspeed(::randNum(150, 500) * 0.1),
    m_position(55.9837, 37.2088, 0),
    m_time_boot_ms(65501),
    m_firmware_version(1001),
    m_focal_length(1.2),
    m_sensor_size_h(1),
    m_sensor_size_v(2),
    m_flags(43),
    m_resolution_h(4),
    m_resolution_v(6),
    m_cam_definition_version(8),
    m_vendor_name("Sony"),
    m_model_name("alpha750"),
    m_lens_id(67),
    m_cam_definition_uri("http://121.1.1.2/pics/1.jpg"),
    m_substate(0),
    m_sendState(0),
    m_reject(0),
    m_ccs_update_trigger(0),
    m_ccs_time_cycle(0),    
    m_cic_interval(0),
    m_disk1_count_of_images(0),
    m_disk2_count_of_images(0)
       
{
    qsrand(QDateTime::currentMSecsSinceEpoch() / 1000);
    this->startTimer(::interval);
}

void UavModel::timerEvent(QTimerEvent* event)
{
    Q_UNUSED(event)

    m_climb = qSin(qDegreesToRadians(m_pitch)) * m_airspeed;

    double distance = m_airspeed / ::timeFactor;
    double distanceUp = m_climb / ::timeFactor;

    m_position = m_position.atDistanceAndAzimuth(distance, m_yaw, distanceUp);
    if (!m_homePosition.isValid()) m_homePosition = m_position;

    m_airspeed += ::randNum(-100, 100) * 0.001;

    if (m_airspeed < 0) m_airspeed *= -1;

    m_pitch = formatPitchRoll(m_pitch + ::randNum(-500, 500) * 0.01);
    m_roll = formatPitchRoll(m_roll + ::randNum(-500, 500) * 0.01);
    m_yaw = formatYaw(m_yaw + ::randNum(-250, 250) * 0.01);
    
    m_time_boot_ms = 655;
}

QGeoCoordinate UavModel::position() const
{
    return m_position;
}

QGeoCoordinate UavModel::homePosition() const
{
    return m_homePosition;
}

void UavModel::setHomePosition(const QGeoCoordinate& homePosition)
{
    m_homePosition = homePosition;
}

float UavModel::airspeed() const
{
    return m_airspeed;
}

float UavModel::groundspeed() const
{
    return m_airspeed; // TODO: wind
}

float UavModel::climb() const
{
    return m_climb;
}

float UavModel::yaw() const
{
    return m_yaw;
}

float UavModel::roll() const
{
    return m_roll;
}

float UavModel::pitch() const
{
    return m_pitch;
}

std::uint32_t UavModel::time_boot_ms() const
{
    return m_time_boot_ms; 
}                                                    /*< [ms] Timestamp (time since system boot).*/
            
std::uint32_t UavModel::firmware_version() const
{
    return m_firmware_version;
}
                                                     /*<  Version of the camera firmware (v << 24 & 0xff = Dev, v << 16 & 0xff = Patch, v << 8 & 0xff = Minor, v & 0xff = Major)*/
float UavModel::focal_length() const
{
    return m_focal_length;    
}
                                                       /*< [mm] Focal length*/
float UavModel::sensor_size_h() const
{
    return m_sensor_size_h;        
}
                                                      /*< [mm] Image sensor size horizontal*/
float UavModel::sensor_size_v() const
{
    return m_sensor_size_v;        
}
                                                      /*< [mm] Image sensor size vertical*/
std::uint32_t UavModel::flags() const
{
    return m_flags;     
}
                                                      /*<  Bitmap of camera capability flags.*/
std::uint16_t UavModel::resolution_h() const
{
    return m_resolution_h;        
}
                                                      /*< [pix] Horizontal image resolution*/
std::uint16_t UavModel::resolution_v() const
{
    return m_resolution_v;   
}
                                                     /*< [pix] Vertical image resolution*/
std::uint16_t UavModel::cam_definition_version() const
{
    return m_cam_definition_version;   
}
                                                     /*<  Camera definition version (iteration)*/
std::uint8_t* UavModel::vendor_name() const
{
    return const_cast<std::uint8_t*>(m_vendor_name);  
}
                                                     /*<  Name of the camera vendor*/
std::uint8_t* UavModel::model_name() const
{
    return const_cast<std::uint8_t*>(m_model_name);      
}
                                                    /*<  Name of the camera model*/
std::uint8_t UavModel::lens_id() const
{
    return m_lens_id;       
}
                                                   /*<  Reserved for a lens ID*/
std::uint8_t* UavModel::cam_definition_uri() const
{
    return const_cast<std::uint8_t*>(m_cam_definition_uri);                  /*<  Camera definition URI (if any, otherwise only basic functions will be available). HTTP- (http://) and MAVLink FTP- (mavlinkftp://) formatted URIs are allowed (and both must be supported by any GCS that implements the Camera Protocol).*/
}

std::int8_t UavModel::get_substate() const
{
    return m_substate;       
}

std::int8_t UavModel::get_sendState() const
{
    return m_sendState;       
}

std::int32_t UavModel::get_disk1data() const
{
    return m_disk1_count_of_images;
}

std::int32_t UavModel::get_disk2data() const
{
    return m_disk2_count_of_images;
}
