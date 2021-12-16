#ifndef SEND_CAM_CANCL_HANDLER_H
#define SEND_CAM_CANCL_HANDLER_H

#include "abstract_handler.h"

namespace domain
{

    class GcsModel;
    
    class SendCameraCancelHandler: public AbstractHandler
    {
    public:
        SendCameraCancelHandler(MavLinkCommunicator* communicator, GcsModel* model);

    public slots:
        void processMessage(const mavlink_message_t& message) override;

    protected:
        void timerEvent(QTimerEvent *event) override;

    private:
        GcsModel* m_model;
    };
}
