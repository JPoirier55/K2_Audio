#!/bin/bash          
#
#   Simple shell script which calls meminfo and parses results for
#   finding the total free memory available in the system
#

val=$(egrep 'MemTotal|MemFree|MemAvailable' /proc/meminfo)
echo $val
