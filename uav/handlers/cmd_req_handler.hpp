#ifndef CMD_REQ_HANDLER_H
#define CMD_REQ_HANDLER_H

#include "abstract_handler.h"

namespace domain
{
    class UavModel;
    
    class CmdReqHandler: public AbstractHandler
    {
        Q_OBJECT

    public:
        CmdReqHandler(MavLinkCommunicator* communicator, UavModel* model);

    public slots:
        void processMessage(const mavlink_message_t& message) override;
        
    private:
        UavModel* m_model;
    };
}

#endif // CMD_REQ_HANDLER_H
