#!/bin/bash

ps aux|grep -v grep|grep -q "python /home/debian/K2_Audio/uart_server.py" || python /home/debian/K2_Audio/uart_server.py &
ps aux|grep -v grep|grep -q "python /home/debian/K2_Audio/tcp_server.py" || python /home/debian/K2_Audio/tcp_server.py &