#!/bin/bash

echo "Uninstalling SwierVision"
echo ""
echo "* Stopping service"
sudo service SwierVision stop
echo "* Removing unit file"
sudo rm /etc/systemd/system/SwierVision.service
echo "* Removing enviroment"
sudo rm -rf ~/.SwierVision-env
echo "!! Please remove $(dirname `pwd`) manually"
echo "Done"
