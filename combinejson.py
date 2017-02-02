import json

import button_led_map

buts = button_led_map.map_overview

micros = {"micro_0": [],
          "micro_1": [],
          "micro_2": [],
          "micro_3": []}


for button in buts:
   if button['micro'] == 0:
     micros['micro_0'].append({'logical': button['logical'], 'panel': button['panel']})
   if button['micro'] == 1:
     micros['micro_1'].append({'logical': button['logical'], 'panel': button['panel']})
   if button['micro'] == 2:
     micros['micro_2'].append({'logical': button['logical'], 'panel': button['panel']})
   if button['micro'] == 3:
     micros['micro_3'].append({'logical': button['logical'], 'panel': button['panel']})
     
print micros