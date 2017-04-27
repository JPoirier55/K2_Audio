import serial

serial_connection = serial.Serial('/dev/ttyO5', 115200)
while True:
    incoming_command = ""
    while True:
        # print "{:02x}".format(ord(serial_connection.read()))
        var = serial_connection.read(1)
        # print ord(var)
        #
        if ord(var) == 0xee:
            incoming_command += var
            print ":".join("{:02x}".format(ord(c)) for c in incoming_command)
            break
        else:
            incoming_command += var
