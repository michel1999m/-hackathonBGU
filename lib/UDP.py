import struct
from lib.ANSI import color_red, bold, reset
# Constant variables
MAGIC_COOKIE = 0xfeedbeef
MESSAGE_TYPE = 0x2
FORMAT = 'IBH'


def create_offer(offer):
    data = struct.pack(FORMAT, MAGIC_COOKIE, MESSAGE_TYPE, offer)
    return data


def resolve_offer(data):
    offer = None
    try:
        unpacked_data = struct.unpack(FORMAT, data)
        if unpacked_data[0] == MAGIC_COOKIE and unpacked_data[1] == MESSAGE_TYPE:
            offer = unpacked_data[2]
    except struct.error as err:
        print(color_red() + bold() + f"Error while unpacking UDP offer : {str(err)}" + reset())
    return offer
