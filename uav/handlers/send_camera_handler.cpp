#include "send_camera_info_handler.h"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

// Internal
#include "uav_model.h"
#include "mavlink_communicator.h"

using namespace domain;

SendCameraInfoHandler::SendCameraInfoHandler(MavLinkCommunicator* communicator,
                                         UavModel* model):
    AbstractHandler(communicator),
    m_model(model)
{
    this->startTimer(40); // 25 Hz
}

void SendCameraInfoHandler::processMessage(const mavlink_message_t& message)
{
    Q_UNUSED(message)
}

void SendCameraInfoHandler::timerEvent(QTimerEvent* event, mavlink_camera_information_t* ci_data)
{
    Q_UNUSED(event)

    std::uint16_t len=0u;
    mavlink_message_t message;
    mavlink_camera_information_t com = NULL;                                                                   /* Command Type */

    com.time_boot_ms = ci_data->time_boot_ms;                                                                  /*< [ms] Timestamp (time since system boot).*/
    com.firmware_version = ci_data->firmware_version;                                                          /*<  Version of the camera firmware (v << 24 & 0xff = Dev, v << 16 & 0xff = Patch, v << 8 & 0xff = Minor, v & 0xff = Major)*/
    com.focal_length = ci_data->focal_length;                                                                  /*< [mm] Focal length*/
    com.sensor_size_h = ci_data->sensor_size_h;                                                                /*< [mm] Image sensor size horizontal*/
    com.sensor_size_v = ci_data->sensor_size_v;                                                                /*< [mm] Image sensor size vertical*/
    com.flags = ci_data->flags;                                                                                /*<  Bitmap of camera capability flags.*/
    com.resolution_h = ci_data->resolution_h;                                                                  /*< [pix] Horizontal image resolution*/
    com.resolution_v = ci_data->resolution_v;                                                                  /*< [pix] Vertical image resolution*/
    com.cam_definition_version = ci_data->cam_definition_version;                                              /*<  Camera definition version (iteration)*/
    strcpy(&com.vendor_name, &ci_data->vendor_name, sizeof(com.vendor_name));                                  /*<  Name of the camera vendor*/
    strcpy(&com.model_name, &ci_data->model_name, sizeof(com.model_name));                                     /*<  Name of the camera model*/
    com.lens_id = ci_data->lensId;                                                                             /*<  Reserved for a lens ID*/
    strcpy(&com.cam_definition_uri, &ci_data->cam_definition_uri, sizeof(com.cam_definition_uri)); 

    len = mavlink_msg_camera_information_encode(m_communicator->systemId(), m_communicator->componentId(), &message, &com);

    m_communicator->sendMessageOnLastReceivedLink(message);
}
