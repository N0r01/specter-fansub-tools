import re
def parse_credits_file(filename):
    f = open(filename,'r')
    lines = list(f.readlines())
    f.close()
    return parse_lines(lines)

def parse_lines(in_lines):
    lines = [re.sub("\n","",l) for l in in_lines if len(l) > 0 and re.search("\w",l) != None]
    retval = [[[lines[0]]]] + [[cl.split(";") for cl in l.split(":",1)] for l in lines[1:]]
    return retval
