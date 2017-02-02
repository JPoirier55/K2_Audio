#!/bin/bash          
 
val=$(egrep 'MemTotal|MemFree|MemAvailable' /proc/meminfo)
echo $val