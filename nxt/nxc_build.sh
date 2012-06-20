#!/usr/bin/env bash
if [ "$#" = "2" ]
then
BRICK=$1
NXC=$2

## USB verwenden:
ALIAS=USB0::0X0694::0X0002::0016531048$BRICK::RAW
## Bluetooth verwenden:
#ALIAS=BTH::LEMMI::00:16:53:10:FD:2C::5

nbc -S=$ALIAS -T=NXT -d $NXC
else
echo "2 Args erwartet 1: die letzten 2 Stellen von Brick-MAC und 2: das nxc-file"
fi
