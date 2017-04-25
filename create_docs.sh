#!/usr/bin/env bash
sudo pydoc -w tcp_server
sudo pydoc -w globals
sudo pydoc -w message_utils

sudo cp tcp_server.html doc/tcp_server.html
sudo cp globals.html doc/globals.html
sudo cp message_utils.html doc/message_utils.html
sudo cp tcp_server.html /var/www/html/tcp_server.html
sudo cp globals.html /var/www/html/globals.html
sudo cp message_utils.html /var/www/html/message_utils.html
rm -rf *.html
