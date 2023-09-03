from substrateinterface.utils.ss58 import ss58_encode


def dot_string_to_float(price_string):
    # Convert the string to an integer
    int_value = int(price_string)

    float_value = int_value / 1e10

    return float_value


def encode(public_key):
    # Convert to address
    address = ss58_encode(public_key, 0)  # 0 is the SS58 format for Polkadot
    return address
