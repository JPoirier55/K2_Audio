import binascii
# test = "7B04400196137D"
# #
# t =  bytearray.fromhex(test)
# for i in t:
#     print hex(i)
# #
# # g = binascii.unhexlify(test)
# print int(test, 16)
# # print test
# # print int(test,2)
# # import time
# # test = False
# #
# # for i in range(10):
# #     while True:
# #         if not test:
# #             print 'okay'
# #             break
# #
# #         print 'hello'
# #         time.sleep(.5)
# #     print i
# import pprint
#
# my_dict = {'name': 'Yasoob', 'age': 'undefined', 'personality': 'awesome'}
# pprint.pprint(my_dict)
# print my_dict

t = bytearray.fromhex('E8023181EE')

print bin(0x81)[2:]

if t[2] == 0x31:
    bit_response = bin(t[3])[2:]
    print int(bit_response[-1])
    if int(bit_response[-1]) == 1:
        print 'okay'
        print bit_response[-1]
