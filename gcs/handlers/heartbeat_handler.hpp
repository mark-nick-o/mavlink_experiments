#ifndef SEND_HEART_HANDLER_H
#define SEND_HEART_HANDLER_H

#include "abstract_handler.h"

namespace domain
{

    class GcsModel;
    
    class SendCmdReqHandler: public HeartBeatHandler
    {
    public:
        HeartBeatHandler(MavLinkCommunicator* communicator, GcsModel* model);

    public slots:
        void processMessage(const mavlink_message_t& message) override;

    protected:
        void timerEvent(QTimerEvent *event) override;

    private:
        GcsModel* m_model;
    };
}
