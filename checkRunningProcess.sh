#!/bin/bash

ps aux|grep -v grep|grep -q "python /root/K2_Audio/uart_receive.py" || python /root/K2_Audio/uart_receive.py &
ps aux|grep -v grep|grep -q "python /root/K2_Audio/ethernet.py" || python /root/K2_Audio/ethernet.py &