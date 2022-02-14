# ============================================================================================
#
# Check if the process is running if its not then respawn via the crontab file
#
# ============================================================================================
#
MAVROUTEHOME=/home/pi/mav/mav_route/mavlink-router/build
ps -ael | grep mavlink-routerd > /dev/null 2>&1
if [ $? -ne 0 ]
then
    sudo $MAVROUTEHOME/kill_all_mavroute_ports.sh > /dev/null 2>&1
    /usr/bin/mavlink-routerd  -e 10.0.2.51:14550 -e 127.0.0.1:14551 /dev/ttyACM0:115200 > /home/pi/mav/mav_route/mavlink-router/build/mavrd.log 2>&1 &
fi
