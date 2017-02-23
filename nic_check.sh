#!/bin/bash          
#
#   Simple shell script that checks nic config
#   to ensure that eth0 is up
#

val=$(cat /sys/class/net/eth0/operstate)
echo $val
