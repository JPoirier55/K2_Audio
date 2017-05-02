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
from unsolicited_utils import *
from button_led_map import *
from panel_main import *

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
        self.assertEquals(translate_uart_port(73), '/dev/ttyO2')
        self.assertEquals(translate_uart_port(96), '/dev/ttyO4')
  
    def test_logical(self):
        """
        Basic tests to check mapping of map_arrays with
        the method in translate_logical_id in message_utils.py
        @return: None
        """
        self.assertEquals(translate_logical_id(66), 28)
        self.assertEquals(translate_logical_id(79), 5)
        self.assertEquals(translate_logical_id(98), 1)
        self.assertEquals(translate_logical_id(99), 49)
        self.assertEquals(translate_logical_id(122), 58)

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

    def test_single_led_command(self):
        cmd = {"category": "BTN", "component": "LED", "component_id": "155", "action": "SET", "value": "1"}
        micro_cmd = translate_single_led(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E80340019BC7EE"), '/dev/ttyO1'))

    def test_led_array_command(self):
        cmd = {"category": "BTN","component": "LED","component_id":
            ["34", "35", "123", "203","78","56","25","201","106"],"action": "SET", "value":"1"}
        micro_cmd = translate_led_array(cmd)
        self.assertEquals(micro_cmd[0]['/dev/ttyO1'][0], bytearray.fromhex("E811420800000000000000000000000000000043EE"))
        self.assertEquals(micro_cmd[0]['/dev/ttyO2'][0], bytearray.fromhex("E811422A2F0B3B000000000000000000000000DAEE"))
        self.assertEquals(micro_cmd[0]['/dev/ttyO4'][0], bytearray.fromhex("E81142190B00000000000000000000000000005FEE"))
        self.assertEquals(micro_cmd[0]['/dev/ttyO5'][0], bytearray.fromhex("E811423800000000000000000000000000000073EE"))

    def test_slow_dcyc_command(self):
        cmd = {"category": "CFG", "component": "CYC", "component_id": "SLO", "action": "SET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E80224010FEE"), '/dev/ttyO1'))
        cmd = {"category": "CFG", "component": "CYC", "component_id": "SLO", "action": "GET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E801250EEE"), '/dev/ttyO1'))

    def test_fast_dcyc_command(self):
        cmd = {"category": "CFG", "component": "CYC", "component_id": "FST", "action": "SET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E802260111EE"), '/dev/ttyO1'))
        cmd = {"category": "CFG", "component": "CYC", "component_id": "FST", "action": "GET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E8012710EE"), '/dev/ttyO1'))

    def test_slow_rate_command(self):
        cmd = {"category": "CFG", "component": "RTE", "component_id": "SLO", "action": "SET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E80220010BEE"), '/dev/ttyO1'))
        cmd = {"category": "CFG", "component": "RTE", "component_id": "SLO", "action": "GET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E801210AEE"), '/dev/ttyO1'))

    def test_fast_rate_command(self):
        cmd = {"category": "CFG", "component": "RTE", "component_id": "FST", "action": "SET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E80222010DEE"), '/dev/ttyO1'))
        cmd = {"category": "CFG", "component": "RTE", "component_id": "FST", "action": "GET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E801230CEE"), '/dev/ttyO1'))

    def test_enc_sens_command(self):
        cmd = {"category": "CFG", "component": "ENC", "component_id": "SEN", "action": "SET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E802280113EE"), '/dev/ttyO1'))
        cmd = {"category": "CFG", "component": "ENC", "component_id": "SEN", "action": "GET", "value": "1"}
        micro_cmd = translate_cfg_cmd(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E8012912EE"), '/dev/ttyO1'))

    def test_panel_status_command(self):
        cmd = {"category": "STS", "component": "SYS", "component_id": "STS", "action": "GET", "value": "1"}
        micro_cmd = check_fw_or_status(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E801311AEE"), 'ALL'))

    def test_panel_fw_version_command(self):
        cmd = {"category": "STS", "component": "SYS", "component_id": "FW", "action": "GET", "value": "1"}
        micro_cmd = check_fw_or_status(cmd)
        self.assertEquals(micro_cmd, (bytearray.fromhex("E801331CEE"), 'ALL'))

    def test_checksum(self):
        cmd = 'E802310520EE'
        self.assertEquals(bytearray.fromhex(cmd)[-2], calculate_checksum_bytes(bytearray.fromhex(cmd)))

        cmd2 = 'E805842010E0F101819185EE'
        self.assertEquals(bytearray.fromhex(cmd2)[-2], calculate_checksum_bytes(bytearray.fromhex(cmd2)))

        cmd3 = 'E81042010405060708090A11121314151617F8EE'
        self.assertEquals(bytearray.fromhex(cmd3)[-2], calculate_checksum_bytes(bytearray.fromhex(cmd3)))

        cmd4 = 'E80942010102030B0C0D1B79EE'
        self.assertEquals(bytearray.fromhex(cmd4)[-2], calculate_checksum_bytes(bytearray.fromhex(cmd4)))

        cmd5 = 'E80242012DEE'
        self.assertEquals(bytearray.fromhex(cmd5)[-2], calculate_checksum_bytes(bytearray.fromhex(cmd5)))

        cmd6 = 'E800E8EE'
        self.assertEquals(bytearray.fromhex(cmd6)[-2], calculate_checksum_bytes(bytearray.fromhex(cmd6)))

        cmd7 = '000000'
        self.assertEquals(bytearray.fromhex(cmd7)[-2], calculate_checksum_bytes(bytearray.fromhex(cmd7)))

    def test_unsolicited_exception(self):
        unsol_handler = UnsolicitedHandler()
        unsol_handler.allocate_command(bytearray.fromhex('E80290209AEE'), '/dev/ttyO1')
        tcp_message = unsol_handler.handle_exception()
        self.assertEquals(tcp_message['value'], '32')
        self.assertEquals(tcp_message['description'], 'marginal_5v')

        unsol_handler.allocate_command(bytearray.fromhex('E80290118BEE'), '/dev/ttyO1')
        tcp_message = unsol_handler.handle_exception()
        self.assertEquals(tcp_message['value'], '17')
        self.assertEquals(tcp_message['description'], 'other_reset_occurred')

    def test_unsolicited_switch(self):
        unsol_handler = UnsolicitedHandler()
        tcp_message = unsol_handler.allocate_command(bytearray.fromhex('E80310050101EE'), '/dev/ttyO1')
        self.assertEquals(tcp_message['value'], '1')
        self.assertEquals(tcp_message['component_id'], '146')

    def test_uart1_switches(self):
        unsol_handler = UnsolicitedHandler()
        for i in range(0, 23):
            cmd = bytearray.fromhex('E80310{0:0{1}X}0101EE'.format(i, 2))
            cmd = finalize_cmd(cmd)
            tcp_message = unsol_handler.allocate_command(cmd, '/dev/ttyO1')
            self.assertEquals(tcp_message['value'], '1')
            index = micro_array['/dev/ttyO1']['logical'].index(i)
            self.assertEquals(tcp_message['component_id'], str(micro_array['/dev/ttyO1']['panel'][index]))

    def test_uart2_switches(self):
        unsol_handler = UnsolicitedHandler()
        for i in range(0, 60):
            cmd = bytearray.fromhex('E80310{0:0{1}X}0101EE'.format(i, 2))
            cmd = finalize_cmd(cmd)
            tcp_message = unsol_handler.allocate_command(cmd, '/dev/ttyO2')
            index = micro_array['/dev/ttyO2']['logical'].index(i)
            self.assertEquals(tcp_message['component_id'], str(micro_array['/dev/ttyO2']['panel'][index]))

    def test_uart4_switches(self):
        unsol_handler = UnsolicitedHandler()
        for i in range(0, 60):
            cmd = bytearray.fromhex('E80310{0:0{1}X}0101EE'.format(i, 2))
            cmd = finalize_cmd(cmd)
            tcp_message = unsol_handler.allocate_command(cmd, '/dev/ttyO4')
            self.assertEquals(tcp_message['value'], '1')
            index = micro_array['/dev/ttyO4']['logical'].index(i)
            self.assertEquals(tcp_message['component_id'], str(micro_array['/dev/ttyO4']['panel'][index]))

    def test_uart5_switches(self):
        unsol_handler = UnsolicitedHandler()
        for i in range(0, 60):
            cmd = bytearray.fromhex('E80310{0:0{1}X}0101EE'.format(i, 2))
            cmd = finalize_cmd(cmd)
            tcp_message = unsol_handler.allocate_command(cmd, '/dev/ttyO5')
            self.assertEquals(tcp_message['value'], '1')
            index = micro_array['/dev/ttyO5']['logical'].index(i)
            self.assertEquals(tcp_message['component_id'], str(micro_array['/dev/ttyO5']['panel'][index]))

    def test_finalize_function(self):
        ba = bytearray([start_char, 0x00, 0x21, 0x01, 0x00, stop_char])
        ba = finalize_cmd(ba)
        self.assertEquals(ba, bytearray.fromhex('E80221010CEE'))

    def test_wrong_finalize(self):
        ba = bytearray([start_char, 0x02, 0x21, 0x01, 0x00, stop_char])
        ba = finalize_cmd(ba)
        self.assertNotEqual(ba, bytearray.fromhex('E80321010CEE'))

    def test_datahandler_btn_errors(self):
        dh = DataHandler()
        json_data = {"category": "BTN$", "component": "LED", "component_id": "155", "action": "SET", "value": "1"}
        dh.setup(json_data)
        self.assertEquals(dh.allocate()['category'], 'ERROR')
        json_data = {"category": "BTN", "component": "LE5D", "component_id": "155", "action": "SET", "value": "1"}
        dh.setup(json_data)
        self.assertEquals(dh.allocate()['category'], 'ERROR')
        json_data = {"category": "BTN", "component": "LED", "component_id": "155", "action": "SET", "value": "67"}
        dh.setup(json_data)
        self.assertEquals(dh.allocate()['category'], 'ERROR')
        json_data = {"category": "BTN", "component": "LED", "component_id": "12355", "action": "SET", "value": "6"}
        dh.setup(json_data)
        self.assertEquals(dh.allocate()['category'], 'ERROR')

    def test_datahandler_enc_errors(self):
        dh = DataHandler()
        json_data = {"category": "ENC", "component": "DIS", "component_id": "0", "action": "SETu", "value": "1"}
        dh.setup(json_data)
        self.assertEquals(dh.allocate()['category'], 'ERROR')
        json_data = {"category": "ENC", "component": "DIS", "component_id": "0", "action": "SET", "value": "er"}
        dh.setup(json_data)
        self.assertEquals(dh.allocate()['category'], 'ERROR')
        json_data = {"category": "ENC", "component": "DISt", "component_id": "0", "action": "SET", "value": "1"}
        dh.setup(json_data)
        self.assertEquals(dh.allocate()['category'], 'ERROR')
        json_data = {"category": "ENC", "component": "DIS", "component_id": "0", "action": "SET", "value": "1"}
        dh.setup(json_data)
        self.assertEquals(dh.allocate()['category'], 'ERROR')

if __name__ == '__main__':
    unittest.main()
