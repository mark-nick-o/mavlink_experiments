#include "get_cam_info_handler.h"

// MAVLink
#include <mavlink.h>

// Qt
#include <QtMath>
#include <QDebug>

using namespace domain;

getCamInfoHandler::getCamInfoHandler(MavLinkCommunicator* communicator):
    AbstractHandler(communicator)
{}

void getCamInfoHandler::processMessage(const mavlink_message_t& message)
{
    if (message.msgid != MAVLINK_MSG_ID_CAMERA_INFORMATION ||
        message.sysid == 0) return;

    mavlink_camera_information_t info;
    mavlink_msg_camera_information_decode(&message, &info);

    qDebug() << "firmware version : " << info.firmware_version
             << "focal length : " << info.focal_length
             << "url : " << info.cam_definition_uri;
}

