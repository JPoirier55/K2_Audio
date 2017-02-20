import unittest
from message_utils import *
import json
from button_led_map import map_arrays
import socket
import SocketServer

TEST_MAP = {'panel': [1,2,3,4],
            'micro': [0,2,1,3],
            'logical': [0,2,0,1]
            }

TEST_CMD = {'category': 'BTN',
            'component': 'LED',
            'component_id': '1',
            'action': 'SET',
            'value': '1',
            }  
TEST_CMD1 = {'category': 'BTN',
             'component': 'LED',
             'component_id': ['1','75','23','18','62','31','101','198','81','87',
                              '12','65','13','28','63','32','102','199','82','88',
                              '13','55','33','38','64','33','103','200','83','89',
                              '14','45','43','48','54','34','104','201','84','90',
                              '15','25','53','58','123','35','105','202','85','91',
                              '16','35','63','68','123','36','106','203','86','92'],
             'action': 'SET',
             'value': '1',
             }
TEST_CMD2 = '''{"category": "BTN","component": "LED","component_id":
            ["34", "35", "123", "203","78","56","25","201","106"],"action": "SET", "value":"1"}'''
CMD_RESP = '''{"category": "BTN", "action": "=", "component_id": ["34", "35", "123",
            "203", "78", "56", "25", "201", "106"], "component": "LED", "value": "1"}'''
   

class TestButtonMapping(unittest.TestCase):
  
    def test_micro(self):
        """
        Basic tests to check mapping of map_arrays with the
        method in translate_uart_port in message_utils.py
        @return: None
        """
        self.assertEquals(translate_uart_port(170), '/dev/ttyO5')
        self.assertEquals(translate_uart_port(156), '/dev/ttyO1')
        self.assertEquals(translate_uart_port(77), '/dev/ttyO2')
        self.assertEquals(translate_uart_port(73), '/dev/ttyO4')
        self.assertEquals(translate_uart_port(96), '/dev/ttyO5')
  
    def test_logical(self):
        """
        Basic tests to check mapping of map_arrays with
        the method in translate_logical_id in message_utils.py
        @return: None
        """
        self.assertEquals(translate_logical_id(66), 9)
        self.assertEquals(translate_logical_id(79), 46)
        self.assertEquals(translate_logical_id(98), 0)
        self.assertEquals(translate_logical_id(99), 0)
        self.assertEquals(translate_logical_id(122), 59)
    
    def test_array(self):
        """
        Test to check validity of algorithm for pulling apart
        arrays into smaller 16 len arrays or assigning uart port
        to each array and message
        @return: None
        """
        button_cmd_array = button_command_array_handler(TEST_CMD1)
        self.assertEquals(len(button_cmd_array), 4)
        for key, value in button_cmd_array.iteritems():
            self.assertEquals(value[0]['category'], 'BN_LED')
            self.assertEquals(value[0]['value'], '1')
            for i in value[0]['id']:
                self.assertEquals(UART_PORTS[map_arrays['micro'][int(i)-1]], key)
  
    def test_split_array(self):
        """
        Test to check lengths of arrays that have been split by
        split_id_array in message_utils.py
        @return: None
        """
        arr = TEST_CMD1['component_id']
        id_arrays = split_id_array(arr)
        num_full = len(arr)/16
        left = len(arr) % 16
        count = 0
        last_len = 0
        for arr in id_arrays:
            if len(arr) == 16:
                count += 1
            else:
                last_len = len(arr)

        self.assertEquals(count, num_full)
        self.assertEquals(last_len, left)
  
    def test_tcp_server(self):
        """
        Simple test to check for tcp server status
        and functionality
        @return: None
        """
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(('0.0.0.0', 65005))
            client.sendall(TEST_CMD2)
            rec = client.recv(1024)
            self.assertEquals(rec+'\n', CMD_RESP)
        finally:
            client.close()

if __name__ == '__main__':
    unittest.main()
