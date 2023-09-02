def dot_string_to_float(price_string):
    # Convert the string to an integer
    int_value = int(price_string)
    
    float_value = int_value / 1e10
    
    return float_value