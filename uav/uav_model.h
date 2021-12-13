#ifndef UAV_MODEL_H
#define UAV_MODEL_H

#include <QObject>
#include <QGeoCoordinate>

namespace domain
{
    class UavModel : public QObject
    {
        Q_OBJECT

    public:
        explicit UavModel(QObject* parent = nullptr);

        float pitch() const;
        float roll() const;
        float yaw() const;

        float airspeed() const;
        float groundspeed() const;
        float climb() const;

        std::uint32_t time_boot_ms() const;                                                         /*< [ms] Timestamp (time since system boot).*/
        std::uint32_t firmware_version() const;                                                     /*<  Version of the camera firmware (v << 24 & 0xff = Dev, v << 16 & 0xff = Patch, v << 8 & 0xff = Minor, v & 0xff = Major)*/
        std::float32_t focal_length() const;                                                        /*< [mm] Focal length*/
        std::float32_t sensor_size_h() const;                                                       /*< [mm] Image sensor size horizontal*/
        std::float32_t sensor_size_v() const;                                                       /*< [mm] Image sensor size vertical*/
        std::uint32_t flags() const;                                                                /*<  Bitmap of camera capability flags.*/
        std::uint16_t resolution_h() const;                                                         /*< [pix] Horizontal image resolution*/
        std::uint16_t resolution_v() const;                                                         /*< [pix] Vertical image resolution*/
        std::uint16_t cam_definition_version() const;                                               /*<  Camera definition version (iteration)*/
        std::uint8_t* vendor_name() const;                                                          /*<  Name of the camera vendor*/
        std::uint8_t* model_name() const;                                                           /*<  Name of the camera model*/
        std::uint8_t lens_id() const;                                                               /*<  Reserved for a lens ID*/
        std::char* cam_definition_uri() const;  
        std::int8_t get_sendState() const;
	std::int8_t get_substate() const;
	
        QGeoCoordinate position() const;
        QGeoCoordinate homePosition() const;

    public slots:
        void setHomePosition(const QGeoCoordinate& homePosition);

    protected:
        void timerEvent(QTimerEvent* event);

    private:
        float m_pitch;
        float m_roll;
        float m_yaw;

        float m_airspeed;
        float m_climb;

        std::uint32_t m_time_boot_ms;                                                         /*< [ms] Timestamp (time since system boot).*/
        std::uint32_t m_firmware_version;                                                     /*<  Version of the camera firmware (v << 24 & 0xff = Dev, v << 16 & 0xff = Patch, v << 8 & 0xff = Minor, v & 0xff = Major)*/
        std::float32_t m_focal_length;                                                        /*< [mm] Focal length*/
        std::float32_t m_sensor_size_h;                                                       /*< [mm] Image sensor size horizontal*/
        std::float32_t m_sensor_size_v;                                                       /*< [mm] Image sensor size vertical*/
        std::uint32_t m_flags;                                                                /*<  Bitmap of camera capability flags.*/
        std::uint16_t m_resolution_h;                                                         /*< [pix] Horizontal image resolution*/
        std::uint16_t m_resolution_v;                                                         /*< [pix] Vertical image resolution*/
        std::uint16_t m_cam_definition_version;                                               /*<  Camera definition version (iteration)*/
        std::uint8_t m_vendor_name[32u];                                                      /*<  Name of the camera vendor*/
        std::uint8_t m_model_name[32u];                                                       /*<  Name of the camera model*/
        std::uint8_t m_lens_id;                                                               /*<  Reserved for a lens ID*/
        std::uint8_t m_cam_definition_uri[140u];  
	std::int8_t m_substate = 0;                                                           /*<  substate for sending ACK or Cancel */                                                     
	std::int8_t m_sendState = 0;                                                          /*<  sending state */
        
        QGeoCoordinate m_position;
        QGeoCoordinate m_homePosition;
    };
}

#endif // UAV_MODEL_H
