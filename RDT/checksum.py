window = 10          # window size

def sexyChecksum(data):
    p = 31
    m = 1e9 + 9    
    hash_value = 0 # make unsigned
    p_pow = 1
    
    data = str(data)
    for c in data:
        hash_value = (hash_value + (ord(c) - ord('a') + 1) * p_pow) % m
        p_pow = (p_pow * p) % m

    tmp = hash_value % 9e8
    tmp = int(tmp)
    tmp = str(tmp)
    tmp = "0"*(9-len(tmp)) + tmp

    return tmp