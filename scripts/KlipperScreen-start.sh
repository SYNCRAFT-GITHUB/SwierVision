#!/bin/bash

SCRIPTPATH=$(dirname $(realpath $0))
if [ -f $SCRIPTPATH/launch_IDEXScreen.sh ]
then
echo "Running "$SCRIPTPATH"/launch_IDEXScreen.sh"
$SCRIPTPATH/launch_IDEXScreen.sh
exit $?
fi

echo "Running IDEXScreen on X in display :0 by default"
/usr/bin/xinit $KS_XCLIENT
