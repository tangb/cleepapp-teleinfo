#!/bin/sh

#install libs
/usr/local/bin/pip2 install --trusted-host pypi.org "teleinfo==1.1.1"
if [ $? -ne 0 ]; then
    exit 1
fi

