import unittest
from message_utils import MessageHandler
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


class TestButtonMapping(unittest.TestCase):
  
  def test_micro(self):
    msg = MessageHandler(TEST_CMD)
    self.assertEquals(msg.translate_uart_port(170), '/dev/ttyO5')
    self.assertEquals(msg.translate_uart_port(156), '/dev/ttyO1')
    self.assertEquals(msg.translate_uart_port(77), '/dev/ttyO2')
    self.assertEquals(msg.translate_uart_port(73), '/dev/ttyO4')
    self.assertEquals(msg.translate_uart_port(96), '/dev/ttyO5')
  
  def test_logical(self):
    msg = MessageHandler(TEST_CMD)
    self.assertEquals(msg.translate_logical_id(66), 9)
    self.assertEquals(msg.translate_logical_id(79), 46)
    self.assertEquals(msg.translate_logical_id(98), 0)
    self.assertEquals(msg.translate_logical_id(99), 0)
    self.assertEquals(msg.translate_logical_id(122), 59)


if __name__ == '__main__':
  unittest.main()