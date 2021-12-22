#ifndef GCS_MODEL_H
#define GCS_MODEL_H

#include <QObject>
#include <QGeoCoordinate>

namespace domain
{
    class GcsModel : public QObject
    {
        Q_OBJECT

    public:
        explicit GcsModel(QObject* parent = nullptr);

    public slots:
        void setHomePosition(const QGeoCoordinate& homePosition);
        std::uint16_t GcsModel::get_cancelCmd();
        void GcsModel::set_cancelCmd(const std::uint16_t& h);
        std::int8_t GcsModel::get_substate();
        std::int8_t GcsModel::get_sendState();
        std::int8_t GcsModel::get_batteryRemain();
        float GcsModel::get_focalLen();
        void GcsModel::set_substate(const std::int8_t& h);
        void GcsModel::set_sendState(const std::int8_t& h);	
	
    protected:
        void timerEvent(QTimerEvent* event);

    private:
        std::uint32_t m_time_boot_ms;                                                         /*< [ms] Timestamp (time since system boot).*/
        std::uint32_t m_firmware_version;                                                     /*<  Version of the camera firmware (v << 24 & 0xff = Dev, v << 16 & 0xff = Patch, v << 8 & 0xff = Minor, v & 0xff = Major)*/
        float m_focal_len;                                                           /*< [mm] Focal length*/
        float m_sensor_size_h;                                                       /*< [mm] Image sensor size horizontal*/
        float m_sensor_size_v;                                                       /*< [mm] Image sensor size vertical*/
        std::uint32_t m_flags;                                                                /*<  Bitmap of camera capability flags.*/
        std::uint16_t m_resolution_h;                                                         /*< [pix] Horizontal image resolution*/
        std::uint16_t m_resolution_v;                                                         /*< [pix] Vertical image resolution*/
        std::uint16_t m_cam_definition_version;                                               /*<  Camera definition version (iteration)*/
        std::uint8_t m_vendor_name[32u];                                                      /*<  Name of the camera vendor*/
        std::uint8_t m_model_name[32u];                                                       /*<  Name of the camera model*/
        std::uint8_t m_lens_id;                                                               /*<  Reserved for a lens ID*/
        std::uint8_t m_cam_definition_uri[140u];  

        std::int8_t m_battery_remain = 0;
	
	std::int8_t m_substate = 0;                                                           /*<  substate for sending ACK or Cancel */                                                     
	std::int8_t m_sendState = 0;                                                          /*<  sending state */

        std::uint16_t m_cancel_cmd = 0;                                                       /*< command you wish to send cancel operation to */
    };
}

#endif // GCS_MODEL_H
