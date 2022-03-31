#!/bin/bash

######################################################################################
#
#   This is to simplify the whole intallation process of python and by extension, 
#   RESTful service managed by Vertical Data Management Team.
#   
#   REQUIREMENT: 
#       - Python tarball
#       - dependencies.tar.gz
#
#   ARGUMENT1 Python-{version}-tar  (NOT tar.gz)
#   ARGUMENT2 dependencies.tar.gz   (Where you place all the python dependencies)
######################################################################################
SCRIPT=$(realpath $0)
CURDIR=$(dirname $SCRIPT)

TAR_FILENAME=$1
FILENAME="${TAR_FILENAME%.*}"
VERSION=$(echo $FILENAME | grep -Po "[0-9]{1}\.[0-9]{1,2}")
DEPENDENCY_TAR=$2
DEPENDENCY="${DEPENDENCY_TAR%%.}"

#Decompressed tar 
tar xfz $TAR_FILENAME

#Preliminary steps
sudo apt-get update 
sudo apt-get upgrade
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
       libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
       libncurses5-dev libncursesw5-dev xz-utils tk-dev 

#For Systemd control
sudo apt install -y dbus libdbus-glib-1-dev libdbus-1-dev python-dbus 

#prepare build python
cd $FILENAME
./configure --enable-optimizations --with-ensurepip=install
#enable-optimizations flag will enable some optimizations within Python to make it run about 10 percent faster.
#with-ensurepip=install flag will install pip bundled with this installation.

#build python using make
make -j 8
# -j option simply tells make to split the building into parallel steps to speed up


# You’ll use the altinstall target here to avoid overwriting 
# the system Python. Since you’re installing into /usr/bin, 
# you’ll need to run as root:
sudo make altinstall

cd $CURDIR
tar zxvf $DEPENDENCY_TAR
cd $DEPENDENCY
sudo pip${VERSION} install * -f ./ --no-index

echo '
[Unit]
Description=Health Check Service
After=multi-user.target


[Service]
Type=simple
WorkingDirectory=/root/vertica-agent
ExecStart=python3.9 -m flask run
StandardInput=tty-force
Restart=always
RestartSec=30s
StartLimitIntervalSec=100
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
' | sudo tee "/lib/systemd/system/vertica-agent.service" /dev/null

sudo systemctl enable vertica-agent.service

sudo mkdir /root/vertica-agent

#Move files except for the unwanted
cd $CURDIR
sudo mv ./!(installation.sh|$TAR_FILENAME|$FILE_NAME|$DEPENDENCY_TAR|$DEPENDENCY) /root/vertica-agent

sudo service vertica-agent start 