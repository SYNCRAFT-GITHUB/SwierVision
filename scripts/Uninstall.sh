#!/bin/bash

echo "Uninstalling IDEXScreen"
echo ""
echo "* Stopping service"
sudo service IDEXScreen stop
echo "* Removing unit file"
sudo rm /etc/systemd/system/IDEXScreen.service
echo "* Removing enviroment"
sudo rm -rf ~/.IDEXScreen-env
echo "!! Please remove $(dirname `pwd`) manually"
echo "Done"
