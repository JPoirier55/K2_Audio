
"""
FILE:   command_map.py
DESCRIPTION: Map of all commands, exceptions, errors, and messages for
Beaglebone<->micro communication

WRITTEN BY: Jake Poirier from Mike Lease's protocol definition

MODIFICATION HISTORY:

date           programmer         modification
-----------------------------------------------
2/23/17          JDP                original

-----------------------------------------------------

    Commands from beaglebone to micro

    Byte #	    Function	        Notes
    ----------------------------------------
    0   	   | start char	       | "{" (0x7b)
    1   	   | length	           | # of bytes that follow excluding checksum
    2   	   | command/status	   |
    3   	   | parameter(s)	   | set to 0 if not used
    3+ length  | checksum	       |
    4+ length  | stop char	       | "}" (0x7d)

"""

start_char = 0xe8
stop_char = 0xee
"""
    Command messages fall within 4 ranges:
    0x20 0x2f = configuration commands
    0x30 0x3f = status request commands
    0x40 0x4f = button LED related commands
    0x50 0x4f = encoder related commands
"""

command_dict = {'set_led_slow_rate': 0x20,
                'get_led_slow_rate': 0x21,
                'set_led_fast_rate': 0x22,
                'get_led_fast_rate': 0x23,
                'set_led_slow_dcyc': 0x24,
                'get_led_slow_dcyc': 0x25,
                'set_led_fast_dcyc': 0x26,
                'get_led_fast_dcyc': 0x27,
                'set_enc_sens': 0x28,
                'get_enc_sens': 0x29,
                'set_led_pwm_dcyc': 0x2a,
                'set_led_pwm_period': 0x2b,
                'get_panel_status': 0x31,
                'get_fw_version': 0x33,
                'set_led_button': 0x40,
                'get_led_button': 0x41,
                'set_led_list': 0x42,
                'execute_led_list': 0x43,
                'set_enc_disp': 0x50,
                'get_enc_disp': 0x51,
                'set_enc_pos': 0x52,
                'get_enc_pos': 0x53
                }
button_numbers = {'semicircle': 0xf0,
                  'center_group': 0xf1,
                  'upper_right_group': 0xf2,
                  'upper_left_group': 0xf3,
                  'all': 0xf8
                  }
button_actions = {'off': 0,
                  'solid_green': 1,
                  'slow_flash_green': 2,
                  'fast_flash_green': 3,
                  'solid_red': 4,
                  'slow_flash_red': 5,
                  'fast_flash_red': 6,
                  'flash_red_green': 7
                  }
"""

    Status and exceptions from control board

    These message codes fall within 3 ranges
    0 0x1f = report normal user activity
    0x20 0x5f = response to command requesting information
    0x80 0xff = message ACK and exception/error reporting
"""
status_and_exceptions = {'switch_action': 0x10,
                         'encoder_pos_change': 0x11,
                         'get_led_slow_rate': 0x21,
                         'get_led_fast_rate': 0x23,
                         'get_led_slow_dcyc': 0x25,
                         'get_led_fast_dcyc': 0x27,
                         'get_enc_sens': 0x29,
                         'get_panel_status': 0x31,
                         'get_fw_version': 0x33,
                         'get_led_button': 0x41,
                         'get_enc_disp': 0x51,
                         'get_enc_pos': 0x53,
                         'ack': 0x80,
                         'exception': 0x90,
                         'error': 0xf0}

"""
    Exception Codes
    
    Below are the possible exception codes reported with 
    the Exception message.
"""

exception_codes = {'power_up_reset_occurred': 0x10,
                   'other_reset_occurred': 0x11,
                   'marginal_5v': 0x20,
                   'high_low_5v': 0x21,
                   'marginal_3.3v': 0x22,
                   'high_low_3.3v': 0x23,
                   'button_stuck_on': 0x30}

"""
    Error codes
    
    Below are the possible error codes reported with the Error message. 
    Error codes below 0x80 are indicative of a properly formatted message 
    with incorrect contents. Error codes above 0x80 are indicative of 
    badly formatted messages, dropped characters, UART errors, etc. 

"""
error_codes = {'invalid_command': 0x11,
               'incorrect_length': 0x12,
               'invalid_parameter': 0x13,
               'rx_misc_error': 0x81,
               'bad_start_char': 0x82,
               'invalid_length': 0x83,
               'bad_checksum': 0x84,
               'bad_stop_char': 0x85,
               'rx_timeout': 0x86,
               'rx_buffer_overflow': 0x87,
               'rx_message_timeout': 0x88}
