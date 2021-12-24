# ============================================================================================
#
# Check if the process is running if its not then respawn via the crontab file
#
# ============================================================================================
#
ps -ael | grep mavlink-routerd > /dev/null
if [ $? -ne 0 ]
then
    /usr/bin/mavlink-routerd  -e 10.0.2.51:14550 /dev/ttyACM0:115200 > /home/pi/mav/mav_route/mavlink-router/build/mavrd.log &
fi
