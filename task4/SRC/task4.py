from sys import argv
import re


str1, str2 = argv[1:3]

def str2_compile(str2):
    """Замена повторяющихся звезд"""
    if str2[0] == '*':
        str2 = '.' + str2
    return re.sub(r'\*+', '\w*', str2)

def string_match(str1, str2):
    reg = str2_compile(str2)
    if re.fullmatch(reg, str1):
        return 'OK'
    return 'KO'


if __name__ == '__main__':
    print(string_match(str1, str2))
