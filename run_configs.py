"""
    Configuration file for all runtime configs

    host: Host IP to run TCP server
    port: Port to run TCP server
    tcp_client: True/False to connect as client to DSP tcp server
    startup_sequence: True/False to begin running start up lighting sequence
    client_host: Host IP of DSP tcp server to connect to
    client_port Port of DSP tcp server to connect to
"""
config_dict = {'host': '0.0.0.0',
               'port': 8003,
               'tcp_client': True,
               'startup_sequence': True,
               'client_host': '192.168.255.76',
               'client_port': 7477,
               'debug': True}
