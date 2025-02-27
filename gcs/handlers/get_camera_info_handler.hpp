#ifndef GET_CAM_INFO_HANDLER_H
#define GET_CAM_INFO_HANDLER_H

#include "abstract_handler.h"

namespace domain
{

    class GcsModel;
    
    class getCamInfoHandler: public AbstractHandler
    {
    public:
        getCamInfoHandler(MavLinkCommunicator* communicator, GcsModel* model);

    public slots:
        void processMessage(const mavlink_message_t& message) override;

    protected:
        void timerEvent(QTimerEvent *event) override;

    private:
        GcsModel* m_model;
    };
}
