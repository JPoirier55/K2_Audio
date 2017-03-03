import binascii
test = "7B04400196137D"

t =  bytearray.fromhex(test)
for i in t:
    print bin(i)

g = binascii.unhexlify(test)
# print int(g, 16)
print test
print int(test,2)



