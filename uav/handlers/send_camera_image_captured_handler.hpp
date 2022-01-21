#ifndef SEND_CAM_IMG_CAP_HANDLER_H
#define SEND_CAM_IMG_CAP_HANDLER_H

#include "abstract_handler.h"

namespace domain
{
    class UavModel;

    class SendCameraImageCapturedHandler: public AbstractHandler
    {
    public:
        SendCameraImageCapturedHandler(MavLinkCommunicator* communicator,
                            UavModel* model);

    public slots:
        void processMessage(const mavlink_message_t& message) override;

    protected:
        void timerEvent(QTimerEvent *event) override;

    private:
        UavModel* m_model;
    };
}

#endif // SEND_CAM_IMG_CAP_HANDLER_H
