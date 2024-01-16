#!/bin/bash

SCRIPTPATH=$(dirname $(realpath $0))
if [ -f $SCRIPTPATH/launch_SwierVision.sh ]
then
echo "Running "$SCRIPTPATH"/launch_SwierVision.sh"
$SCRIPTPATH/launch_SwierVision.sh
exit $?
fi

echo "Running SwierVision on X in display :0 by default"
/usr/bin/xinit $SV_XCLIENT
