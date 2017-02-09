import unittest
from message_utils import *
import json

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


class TestButtonMapping(unittest.TestCase):
  
  def test_micro(self):
    self.assertEquals(translate_uart_port(170), '/dev/ttyO5')
    self.assertEquals(translate_uart_port(156), '/dev/ttyO1')
    self.assertEquals(translate_uart_port(77), '/dev/ttyO2')
    self.assertEquals(translate_uart_port(73), '/dev/ttyO4')
    self.assertEquals(translate_uart_port(96), '/dev/ttyO5')
  
  def test_logical(self):
    self.assertEquals(translate_logical_id(66), 9)
    self.assertEquals(translate_logical_id(79), 46)
    self.assertEquals(translate_logical_id(98), 0)
    self.assertEquals(translate_logical_id(99), 0)
    self.assertEquals(translate_logical_id(122), 59)
    
  def test_array(self):
    msg = MessageHandler(TEST_CMD1)
    msg.process_command()


if __name__ == '__main__':
  unittest.main()