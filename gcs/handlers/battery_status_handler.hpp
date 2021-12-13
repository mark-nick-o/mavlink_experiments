#ifndef SEND_BATT_STAT_HANDLER_H
#define SEND_BATT_STAT_HANDLER_H

#include "abstract_handler.h"

namespace domain
{

    class GcsModel;
    
    class BattStatHandler: public AbstractHandler
    {
    public:
        BattStatHandler(MavLinkCommunicator* communicator, GcsModel* model);

    public slots:
        void processMessage(const mavlink_message_t& message) override;

    protected:
        void timerEvent(QTimerEvent *event) override;

    private:
        GcsModel* m_model;
    };
}

#endif
