__author__ = 'Owner'

SUCCESS = 0x01
NONEXISTENTKEY = 0x02
OUTOFSPACE = 0x03
OVERLOAD = 0x04
STOREFAILURE = 0x05
UNRECOGNIZED = 0x06
RPNOREPLY = 0x21

# RESPONSE = {
#     "SUCCESS" : 0x01 ,  # store data indexed by strings.
#     "NONEXISTENTKEY" : 0x02,
#     "OUTOFSPACE" : 0x03,
#     "OVERLOAD" : 0x03,
#     "STOREFAILURE" : 0x03,
#     "UNRECOGNIZED" : 0x03,
#     "RPNOREPLY" : 0x03
# }



# 1. The code is 1 byte long. It can be:
# 0x00. This means the operation is successful.
# 0x01.  Non-existent key requested in a get or delete operation
# 0x02.  Out of space  (returned when there is no space left for a put).
# 0x03.  System overload.
# 0x04.  Internal KVStore failure
# 0x05.  Unrecognized command.
#      [possibly more standard codes will get defined here]
# anything > 0x20. Your own error codes. [Define them in your Readme]
