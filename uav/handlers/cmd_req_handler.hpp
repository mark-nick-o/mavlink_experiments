#ifndef CMD_REQ_HANDLER_H
#define CMD_REQ_HANDLER_H

#include "abstract_handler.h"

namespace domain
{
    class CmdReqHandler: public CmdReqHandler
    {
        Q_OBJECT

    public:
        CmdReqHandler(MavLinkCommunicator* communicator);

    public slots:
        void processMessage(const mavlink_message_t& message) override;
    };
}

#endif // CMD_REQ_HANDLER_H
