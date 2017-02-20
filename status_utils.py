"""
FILE:   status_utils.py
DESCRIPTION: Utils module which checks status of beaglebone and parses any
bash script output from commands.
WRITTEN BY: Jake Poirier

MODIFICATION HISTORY:

date           programmer         modification
-----------------------------------------------
1/27/17          JDP                original
"""

import subprocess
import sys
import serial
import json


def check_status():
    """
    Checks status of various elements on the beaglebone
    @return: Status id 0,1,2 depending on status
    """
    """
      Need to set some status protocols for bbb with response codes
      check uarts - send msg to each micro, check status, return with status of each micro
      check power - ??
      check memtotal vs memfree - cat /proc/meminfo or egrep 'MemTotal|MemFree|MemAvailable' /proc/meminfo
      check system functionality
      need restart?
      Have warnings
      
    """
    mem_error = check_memory()
    
    board = True
    if board:
        return 1
    elif not board:
        return 2
    else:
        return 0


def check_memory():
    """
    Checks memory by doing a grep of meminfo for total memory,
    free memory, and available memory. Checks if free is less than
    15% of the total, which there should be an error because the
    beaglebone does not use very much mem in processing commands.
    @return: Error status
    """
    mem_error = 0
    try:
        val = subprocess.check_output(['sh', 'mem_check.sh']).split(" ")
        mem_total = val[1]
        mem_free = val[4]
        if (float(mem_free) / float(mem_total)) < .15:
            mem_error = 1
    except Exception as e:
        sys.stderr.write(str(e))
        pass
    return mem_error


def check_uarts():
    """
    Checks all uarts by sending a sample status command
    and waiting for a return call of OK
    @return: Error status for each uart
    """
    uarts = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
    status_msg = {"category": "SYS", "component": "STS"}
    for uart in uarts:
        ser = serial.Serial(uart, 115200, None)
        ser.write(json.dumps(status_msg)+"\n")
