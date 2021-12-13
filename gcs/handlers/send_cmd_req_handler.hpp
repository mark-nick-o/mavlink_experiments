#ifndef SEND_CMD_REQ_HANDLER_H
#define SEND_CMD_REQ_HANDLER_H

#include "abstract_handler.h"

namespace domain
{

    class SendCmdReqHandler: public AbstractHandler
    {
    public:
        SendCmdReqHandler(MavLinkCommunicator* communicator);

    public slots:
        void processMessage(const mavlink_message_t& message) override;

    protected:
        void timerEvent(QTimerEvent *event) override;

    };
}
