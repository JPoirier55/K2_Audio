#!/usr/bin/env bash
sudo pydoc -w panel_main
sudo pydoc -w globals
sudo pydoc -w message_utils
sudo pydoc -w unsolicited_utils
sudo pydoc -w button_led_map

sudo cp panel_main.html doc/panel_main.html
sudo cp globals.html doc/globals.html
sudo cp message_utils.html doc/message_utils.html
sudo cp unsolicited_utils.html doc/unsolicited_utils.html
sudo cp button_led_map.html doc/button_led_map.html
sudo cp panel_main.html /var/www/html/panel_main.html
sudo cp globals.html /var/www/html/globals.html
sudo cp message_utils.html /var/www/html/message_utils.html
sudo cp unsolicited_utils.html /var/www/html/unsolicited_utils.html
sudo cp button_led_map.html /var/www/html/button_led_map.html
rm -rf *.html
