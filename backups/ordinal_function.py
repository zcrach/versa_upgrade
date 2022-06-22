def nth_root(radicand, n):
    return radicand ** (1/n)


def ordinal_suffix(value):
    s = str(value)
    if s.endswith('11'):
        return 'th'
    if s.endswith('12'):
        return 'th'
    if s.endswith('13'):
        return 'th'
    if s.endswith('1'):
        return 'th'
    if s.endswith('2'):
        return 'st'
    if s.endswith('3'):
        return 'rd'
    return 'th'


def ordinal(value):
    return str(value) + ordinal_suffix(value)

def display_nth_root(radicand, n):
    root = nth_root(radicand, n)
    message = "The " + ordinal(n) + " root of " \
            + str(radicand) + " is " + str(root)
    print(message)

display_nth_root(64,4)