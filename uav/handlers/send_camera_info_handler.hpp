#ifndef SEND_CAMERA_INFO_HANDLER_H
#define SEND_CAMERA_INFO_HANDLER_H

#include "abstract_handler.h"

namespace domain
{
    class UavModel;

    class SendCameraInfoHandler: public AbstractHandler
    {
    public:
        SendCameraInfoHandler(MavLinkCommunicator* communicator,
                            UavModel* model);

    public slots:
        void processMessage(const mavlink_message_t& message) override;

    protected:
        void timerEvent(QTimerEvent *event) override;

    private:
        UavModel* m_model;
    };
}

#endif // SEND_CAMERA_INFO_HANDLER_H
