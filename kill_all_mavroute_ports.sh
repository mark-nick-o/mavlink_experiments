# list the used ports being used by mavlink router amd kill them all before re-starting mav-router 
#
TMPLIST=/home/pi/tmp/tmplist
touch $TMPLIST
#
# do for all ports that your mavrouter-uses we use 5760=tcp 14550=redEdge 14551=SonyCam
#
for pp in :5760 :14550 :14551
do
    sudo lsof -i $pp | awk '{ if (tag==1) {print $2} if($2=="PID") tag=1 }' > $TMPLIST
    if [ -f $TMPLIST ]
    then
        for pid in `cat $TMPLIST`
        do
            kill -9 "$pid"
        done
        rm $TMPLIST
    fi
done
