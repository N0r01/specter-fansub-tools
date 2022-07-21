from credits_parser import parse_credits_file
from functools import reduce
import math, argparse

h_pad = 1
l_width = 1

def max_line_width(creditstruct):
    header_width = len(creditstruct[0]) + (h_pad + l_width) * 2
    max_width = header_width
    max_lhs = 0
    max_rhs = 0
    for row in creditstruct[1:]:
        for clidx in range(max([len(cl) for cl in row])):
            rhs = row[1][clidx] if clidx < len(row[1]) else ""
            lhs = row[0][clidx] if clidx < len(row[0]) else ""
            max_lhs = max(max_lhs,len(lhs))
            max_rhs = max(max_rhs,len(rhs))
    total_width = max_rhs + max_lhs + h_pad * 4 + l_width * 3
    max_width = max(max_width,total_width)
    return (max_width,max_lhs,max_rhs)

parser = argparse.ArgumentParser(description='output credits as svg')
parser.add_argument('-i','--infile',help='input file')
parser.add_argument('-o','--outfile',help='output file')
args = parser.parse_args()
structure = parse_credits_file(args.infile)
max_width,max_lhs,max_rhs = max_line_width(structure)

output = ""
h_div = "\n".join(["#" * max_width]*l_width)
l_div = "#" * l_width
pad = " " * h_pad
def extra_h_padding(header_string):
    min_width = len(header_string) + (h_pad + l_width) * 2
    rhs_pad = " " * math.ceil((max_width - min_width) / 2)
    lhs_pad = " " * math.floor((max_width - min_width) / 2)
    return (lhs_pad, rhs_pad)

def extra_cell_padding(lhs_str,rhs_str):
    min_width = len(lhs_str) + (h_pad + l_width) * 2
    rhs_pad = " " * (max_rhs - len(rhs_str))
    lhs_pad = " " * (max_lhs - len(lhs_str))
    return (lhs_pad, rhs_pad)

for idx,row in enumerate(structure):
    if idx == 0:
        lhs_pad, rhs_pad = extra_h_padding(row[0][0])
        rline = l_div + pad + lhs_pad + row[0][0] + rhs_pad + pad + l_div
        output = "\n".join([h_div,rline,h_div])
    else:
        for clidx in range(max([len(cl) for cl in row])):
            rhs = row[1][clidx] if clidx < len(row[1]) else ""
            lhs = row[0][clidx] if clidx < len(row[0]) else ""
            lhs_pad, rhs_pad = extra_cell_padding(lhs,rhs)
            rline = l_div + pad + lhs + lhs_pad + pad + l_div + pad + rhs + rhs_pad + pad + l_div
            output = output + "\n" + rline
        output = output + "\n" + h_div

print(args.outfile)
with open(args.outfile, "w") as f:
    f.write(output)
