import subprocess
import sys
import serial
import json


def check_status():
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
    uarts = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
    status_msg = {"category": "SYS", "component": "STS"}
    for uart in uarts:
      ser = serial.Serial(uart, 115200, None)
      ser.write(json.dumps(status_msg)+"\n")