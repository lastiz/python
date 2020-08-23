import sys


def num_converter(nb, base_src, base_dst):
    try:
        base_src, base_dst = int(base_src), int(base_dst)
    except TypeError:
        print('usage')
        sys.exit()

    if isinstance(nb, str):
        nb = int(nb, base_src)
    else:
        nb = int(nb)

    alph = "0123456789abcdefghijklmnopqrstuvwxyz"
    if nb < base_dst:
        return alph[nb]
    else:
        return num_converter(nb // base_dst, base_src, base_dst) + alph[nb % base_dst]

def main():
    try:
        nb, base_src, base_dst = sys.argv[1:4]
    except ValueError:
        print('usage')
        sys.exit()

    print(num_converter(nb, base_src, base_dst))


if __name__ == '__main__':
    main()