# cleepmod-teleinfo [![Coverage Status](https://coveralls.io/repos/github/tangb/cleepapp-teleinfo/badge.svg?branch=master)](https://coveralls.io/github/tangb/cleepapp-teleinfo?branch=master)

Teleinfo module for Cleep

![alt text](https://github.com/tangb/cleepmod-teleinfo/raw/master/resources/linky.jpg)

## Teleinfo
Teleinfo is France Enedys (ex EDF) energy provider protocol for their home electric meters.

It provides 2 wires that can be connected to specific equipements to read power consumption, energy subscription informations...

## Installation
To use this application you need to buy the only supported teleinfo dongle built by [Charles Hallard](http://hallard.me/utinfo/) (and available on [Tindie](https://www.tindie.com/products/hallard/micro-teleinfo-v20/)). It costs around 20€. It's not the less expensive dongle but it the simplest one to use ;-)

Then simply connect the USB dongle to your raspberrypi and install "Teleinfo" application from CleepOS.

Once installed, open the application configuration page and check everything is running fine. You should see informations retrieved from your electric meter on the page.

## How it works
The application reads teleinfo data every minute and publish an event to Cleep.

## Troubleshoot
If problem occurs, please open logs file from "System" application.

## Charts
This application is able to generate charts to follow easily your power consumption. It can generate:
* a line chart for your current power consumption (data updated every 1 minute)
* a bar chart for your daily power consumption (data updated every day at midnight)

To automatically generate those charts, install "Charts" application. There is noting else to configure.

After application is installed, please wait few hours to see enough values displayed on charts (particularly the bar chart).

Charts are available from Teleinfo dashboard widget clicking on `Charts` button.
