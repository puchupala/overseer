from itertools import tee, izip


def pairwise(iterable):
    """
    Taken from: http://stackoverflow.com/questions/5764782/iterate-through-pairs-of-items-in-python-list

    s -> (s0,s1), (s1,s2), (s2, s3), ...

    for v, w in pairwise(a):
    ...
    """
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def create_path_identifier(from_ip, from_port, to_ip, to_port):
    """
    Create path identifier to use with flow-preference table

    The identifier is just a tuple containing various information
    """
    return (from_ip, from_port, to_ip, to_port)
