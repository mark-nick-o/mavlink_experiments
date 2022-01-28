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
        float focal_length() const;                                                        /*< [mm] Focal length*/
        float sensor_size_h() const;                                                       /*< [mm] Image sensor size horizontal*/
        float sensor_size_v() const;                                                       /*< [mm] Image sensor size vertical*/
        std::uint32_t flags() const;                                                                /*<  Bitmap of camera capability flags.*/
        std::uint16_t resolution_h() const;                                                         /*< [pix] Horizontal image resolution*/
        std::uint16_t resolution_v() const;                                                         /*< [pix] Vertical image resolution*/
        std::uint16_t cam_definition_version() const;                                               /*<  Camera definition version (iteration)*/
        std::uint8_t* vendor_name() const;                                                          /*<  Name of the camera vendor*/
        std::uint8_t* model_name() const;                                                           /*<  Name of the camera model*/
        std::uint8_t lens_id() const;                                                               /*<  Reserved for a lens ID*/
        std::uint8_t* cam_definition_uri() const;  
        std::int8_t get_sendState() const;
        std::int8_t get_substate() const;
        void set_sendState( std::int8_t dataVal );
        void set_substate( std::int8_t dataVal );
        std::uint16_t get_reject() const;
        std::int32_t get_disk1data() const;
        std::int32_t get_disk2data() const;

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

        QGeoCoordinate m_position;
        QGeoCoordinate m_homePosition;

        std::uint32_t m_time_boot_ms;                                                         /*<  [ms] Timestamp (time since system boot).*/
        std::uint32_t m_firmware_version;                                                     /*<  Version of the camera firmware (v << 24 & 0xff = Dev, v << 16 & 0xff = Patch, v << 8 & 0xff = Minor, v & 0xff = Major)*/
        float m_focal_length;                                                        /*<  [mm] Focal length*/
        float m_sensor_size_h;                                                       /*<  [mm] Image sensor size horizontal*/
        float m_sensor_size_v;                                                       /*<  [mm] Image sensor size vertical*/
        std::uint32_t m_flags;                                                                /*<  Bitmap of camera capability flags.*/
        std::uint16_t m_resolution_h;                                                         /*<  [pix] Horizontal image resolution*/
        std::uint16_t m_resolution_v;                                                         /*<  [pix] Vertical image resolution*/
        std::uint16_t m_cam_definition_version;                                               /*<  Camera definition version (iteration)*/
        std::uint8_t m_vendor_name[32u];                                                      /*<  Name of the camera vendor*/
        std::uint8_t m_model_name[32u];                                                       /*<  Name of the camera model*/
        std::uint8_t m_lens_id;                                                               /*<  Reserved for a lens ID*/
        std::uint8_t m_cam_definition_uri[140u];  
	std::int8_t m_substate = 0;                                                           /*<  substate for sending ACK or Cancel */                                                     
	std::int8_t m_sendState = 0;                                                          /*<  sending state */
        std::uint16_t m_reject = 0;                                                           /*   reject message we are in progress of another conflicting action */
        std::uint32_t m_ccs_update_trigger = 0;                                               /*   frequency in multiples of 25Hz that CCS update is sent when MAV_CMD_VIDEO_START_CAPTURE sent */
        std::uint32_t m_ccs_time_cycle = 0;                                                   /*   counter in multiples of 25Hz to check against the above limit to retriger CCS message */
        std::uint32_t m_cic_interval = 0;
        float m_missing_image_index = 0;

        std::int32_t m_disk1_count_of_images = 0;
        std::int32_t m_disk2_count_of_images = 0;
	
	std::uint16_t m_ack_cmd = 0;

    };
}

#endif // UAV_MODEL_H
