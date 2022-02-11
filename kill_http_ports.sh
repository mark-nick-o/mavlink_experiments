#
# list the used ports being used by http on port80 (by flask) amd kill them so the flask webserver runs clean
#
TMPLIST=/home/pi/tmp/tmplist
touch $TMPLIST
sudo lsof -i :80 | awk '{ if (tag==1) {print $2} if($2=="PID") tag=1 }' > $TMPLIST
if [ -f $TMPLIST ]
then
    for pid in `cat $TMPLIST`
    do
        kill -9 "$pid"
    done
    rm $TMPLIST
fi
