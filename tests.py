"""
FILE:   tests.py
DESCRIPTION: Set of unit tests for methods. Verifies functionality
of most small methods as well as testing for correct responses
from methods

WRITTEN BY: Jake Poirier

MODIFICATION HISTORY:

date           programmer         modification
-----------------------------------------------
2/1/17          JDP                original
"""
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

    '''
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
    '''

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
  
    '''
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
    '''

    def test_single_led_command(self):
        cmd = {"category": "BTN", "component": "LED", "component_id": "155", "action": "SET", "value": "1"}
        micro_cmd = translate_single_led(cmd)
        self.assertEquals(micro_cmd, ("E80340019BC7EE", '/dev/ttyO1'))

    def test_led_array_command(self):
        cmd = {"category": "BTN","component": "LED","component_id":
            ["34", "35", "123", "203","78","56","25","201","106"],"action": "SET", "value":"1"}
        micro_cmd = translate_led_array(cmd)
        self.assertEquals(micro_cmd[0]['/dev/ttyO1'], "E8044201CBC9C3EE")
        self.assertEquals(micro_cmd[0]['/dev/ttyO2'], "E80442014E6AE7EE")
        self.assertEquals(micro_cmd[0]['/dev/ttyO4'], "E8054201222338ADEE")
        self.assertEquals(micro_cmd[0]['/dev/ttyO5'], "E80442017B19C3EE")

    def test_slow_dcyc_command(self):
        cmd = {"category": "CFG", "component": "CYC", "component_id": "SLO", "action": "SET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E80224010FEE", '/dev/ttyO1'))
        cmd = {"category": "CFG", "component": "CYC", "component_id": "SLO", "action": "GET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E80225000FEE", '/dev/ttyO1'))

    def test_fast_dcyc_command(self):
        cmd = {"category": "CFG", "component": "CYC", "component_id": "FST", "action": "SET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E802260111EE", '/dev/ttyO1'))
        cmd = {"category": "CFG", "component": "CYC", "component_id": "FST", "action": "GET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E802270011EE", '/dev/ttyO1'))

    def test_slow_rate_command(self):
        cmd = {"category": "CFG", "component": "RTE", "component_id": "SLO", "action": "SET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E80220010BEE", '/dev/ttyO1'))
        cmd = {"category": "CFG", "component": "RTE", "component_id": "SLO", "action": "GET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E80221000BEE", '/dev/ttyO1'))

    def test_fast_rate_command(self):
        cmd = {"category": "CFG", "component": "RTE", "component_id": "FST", "action": "SET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E80222010DEE", '/dev/ttyO1'))
        cmd = {"category": "CFG", "component": "RTE", "component_id": "FST", "action": "GET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E80223000DEE", '/dev/ttyO1'))

    def test_enc_sens_command(self):
        cmd = {"category": "CFG", "component": "ENC", "component_id": "SEN", "action": "SET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E802280113EE", '/dev/ttyO1'))
        cmd = {"category": "CFG", "component": "ENC", "component_id": "SEN", "action": "GET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E802290013EE", '/dev/ttyO1'))

    '''
    def test_panel_status_command(self):
        cmd = {"category": "STS", "component": "SYS", "component_id": "STS", "action": "GET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E802220110EE", '/dev/ttyO1'))

    def test_panel_fw_version_command(self):
        cmd = {"category": "CFG", "component": "RTE", "component_id": "FST", "action": "SET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, ("E802220110EE", '/dev/ttyO1'))
    '''

    # def test_checksum(self):
    #     cmd_chk = 'E80310050000EE'
    #     cmd = 'E8031005000EE'
    #     self.assertEquals(bytearray.fromhex(cmd_chk)[-2], calculate_checksum_string(cmd))
    #
    #     cmd2_chk = 'E80842010E0F1018191AABEE'
    #     cmd2 = 'E80842010E0F1018191A0EE'
    #     self.assertEquals(bytearray.fromhex(cmd2_chk)[-2], calculate_checksum_string(cmd2))
    #
    #     cmd3_chk = 'E81042010405060708090A11121314151617F8EE'
    #     cmd3 = 'E81042010405060708090A111213141516170EE'
    #     self.assertEquals(bytearray.fromhex(cmd3_chk)[-2], calculate_checksum_string(cmd3))
    #
    #     cmd4_chk = 'E80942010102030B0C0D1B79EE'
    #     cmd4 = 'E80942010102030B0C0D1B0EE'
    #     self.assertEquals(bytearray.fromhex(cmd4_chk)[-2], calculate_checksum_string(cmd4))
    #
    #     cmd5_chk = 'E80242012DEE'
    #     cmd5 = 'E80242010EE'
    #     self.assertEquals(bytearray.fromhex(cmd5_chk)[-2], calculate_checksum_string(cmd5))
    #
    #     cmd6_chk = 'E800E8EE'
    #     cmd6 = 'E8000EE'
    #     self.assertEquals(bytearray.fromhex(cmd6_chk)[-2], calculate_checksum_string(cmd6))
    #
    #     cmd7_chk = '000000'
    #     cmd7 = '000'
    #     self.assertEquals(bytearray.fromhex(cmd7_chk)[-2], calculate_checksum_string(cmd7))


class TestCommands():
    def test_bytearray_change(self):
        start = 'E8'
        length = '02'
        cmd = '42'
        end = 'EE'
        # micro_cmd = bytearray([int(start, 16), int(length, 16), int(cmd, 16), int(end, 16)])
        # print ":".join("{:02x}".format(c) for c in micro_cmd)
        cmd = {"category": "CFG", "component": "RTE", "component_id": "SLO", "action": "GET", "value": "1"}
        r = translate_cfg_cmd(cmd)
        print ":".join("{:02x}".format(c) for c in r[0])

        cmd = {"category": "BTN", "component": "LED", "component_id": "155", "action": "GET", "value": "1"}
        r1 = translate_single_led(cmd)
        print r1
        print ":".join("{:02x}".format(c) for c in r1[0])

        cmd = {"category": "BTN", "component": "LED", "component_id": ["34", "35", "123", "203", "78", "56", "25",
                                                                       "201", "106"], "action": "SET", "value": "1"}
        micro_cmd = translate_led_array(cmd)
        for port, cmd in micro_cmd[0].iteritems():
            print ":".join("{:02x}".format(c) for c in cmd[0])

        print '-----'

        t = ["18","1A", "1234","150","45t", "1234","150","45", "1234","150","45", "1234","150","45",
              "1234","150","45", "1234","150","45", "1234","150","45", "1234","45", "1234","150","45",
              "1234","150","45", "1234","150","45", "1234","45", "1234","150","45", "1234","150","45",
             "1234", "150", "45", "1234", "45", "1234", "150", "45", "1234", "150", "45", "1234", "150", "45", "1234",
              "1234","150","45", "1234","45", "1234","150","45", "1234","150","45", "1234","150","45", "1234"]

        cmd2 = {"category": "BTN", "component": "LED", "component_id": t, "action": "SET", "value": "1"}
        micro_cmd2 = translate_led_array(cmd2)

        for port, cmd in micro_cmd2[0].iteritems():
            for cmd_ in cmd:
                print ":".join("{:02x}".format(c) for c in cmd_)

if __name__ == '__main__':
    # unittest.main()
    t = TestCommands()
    t.test_bytearray_change()
