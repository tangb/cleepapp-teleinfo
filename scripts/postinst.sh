#!/bin/sh

#install libs
python3 -m pip install --trusted-host pypi.org "teleinfo==1.2.1"
if [ $? -ne 0 ]; then
    exit 1
fi

