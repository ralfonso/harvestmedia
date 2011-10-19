import random

def get_random_md5():
    return '%032x' % (random.getrandbits(128))
