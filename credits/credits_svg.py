from xml.dom import minidom
from PIL import ImageFont
from credits_parser import parse_credits_file
import os, argparse
user_defined_min_width = 200
cell_H_padding = 12
cell_height = 36
cell_lheight = 21
text_start_y = 24
font_size = 15
font = ImageFont.truetype('arial.ttf', font_size)

def calc_max_line_width(creditstruct):
    header_width = font.getsize(creditstruct[0][0][0])[0] + cell_H_padding * 2
    max_width = header_width
    max_lhs = 0
    max_rhs = 0
    for row in creditstruct[1:]:
        for clidx in range(max([len(cl) for cl in row])):
            rhs = row[1][clidx] if clidx < len(row[1]) else ""
            lhs = row[0][clidx] if clidx < len(row[0]) else ""
            max_lhs = max(max_lhs,font.getsize(lhs)[0])
            max_rhs = max(max_rhs,font.getsize(rhs)[0])
    total_width = max_rhs + max_lhs + cell_H_padding * 4
    max_width = max(max_width,total_width)
    return (max_width,max_lhs,max_rhs)

def calc_row_height(row):
    num_subrows = max(len(row[0]),len(row[1]))
    return 0 if num_subrows == 0 else cell_height + cell_lheight * (num_subrows-1)

def calc_doc_height(creditstruct):
    retval = 0
    if creditstruct != None and len(creditstruct) > 0:
        for idx, row in enumerate(creditstruct):
            retval += cell_height if idx == 0 else calc_row_height(row)
    return retval

def alt_row_color_drawpath(creditstruct,width,lhs_width,doc_height):
    retval = []
    ycursor = 0
    if creditstruct != None and len(creditstruct) > 0:
        for idx, row in enumerate(creditstruct):
            height = cell_height if idx == 0 else calc_row_height(row)
            if idx % 2 == 1:
                retval.append(f"M 0 {str(ycursor)} L 0 {str(ycursor+height)} {str(width)} {str(ycursor+height)} {str(width)} {str(ycursor)} z")
            ycursor = ycursor + height
        mline_x = lhs_width + cell_H_padding * 2
        retval.append(f"M {str(mline_x)} {str(cell_height)} L {str(mline_x)} {str(doc_height)}")
    return " ".join(retval)

def tspans(creditstruct,width,textnode,xml,max_lhs):
    retval = []
    ycursor = text_start_y + cell_height
    if creditstruct != None and len(creditstruct) > 0:
        for row in creditstruct:
            for subrow_idx in range(max(len(row[0]),len(row[1]))):
                if subrow_idx < len(row[0]):
                    y = ycursor + cell_lheight * subrow_idx
                    x = cell_H_padding
                    gen_tspan(textnode,xml,x,y,row[0][subrow_idx])
                    #retval.append(f'<tspan x="{x}" y="{y}">{row[0][subrow_idx]}<\tspan>')
                if subrow_idx < len(row[1]):
                    y = ycursor + cell_lheight * subrow_idx
                    x = cell_H_padding * 3 + max_lhs
                    gen_tspan(textnode,xml,x,y,row[1][subrow_idx])
                    #retval.append(f'<tspan x="{x}" y="{y}">{row[1][subrow_idx]}<\tspan>')
            ycursor += calc_row_height(row)
    return retval

def gen_tspan(textnode,xml,x,y,text):
    tspan = xml.createElement("tspan")
    tspan.setAttribute('x',str(x))
    tspan.setAttribute('y',str(y))
    ttext = xml.createTextNode(text)
    textnode.appendChild(tspan)
    tspan.appendChild(ttext)

parser = argparse.ArgumentParser(description='output credits as svg')
parser.add_argument('-i','--infile',help='input file')
parser.add_argument('-o','--outfile',help='output file')
args = parser.parse_args()

structure = parse_credits_file(args.infile)
max_width,max_lhs,max_rhs = calc_max_line_width(structure)
doc_width = max(max_width,user_defined_min_width)
doc_height = calc_doc_height(structure)

xml = minidom.Document()
svg = xml.createElement("svg")
svg.setAttribute('height',f'{doc_height}')
svg.setAttribute('width',f'{doc_width}')
svg.setAttribute('xmlns',"http://www.w3.org/2000/svg")
xml.appendChild(svg)
color_rect = xml.createElement("rect")
color_rect.setAttribute('style','fill:#414141;fill-opacity:1;stroke:#252525;stroke-width:1.5;paint-order:fill markers stroke')
color_rect.setAttribute('height',f'{doc_height}')
color_rect.setAttribute('width',f'{doc_width}')
svg.appendChild(color_rect)
alt_color_path = xml.createElement("path")
alt_color_path.setAttribute('style','fill:#383838;fill-opacity:1;stroke:#252525;stroke-width:0.75;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:none;stroke-opacity:1;paint-order:fill markers stroke')
alt_color_path.setAttribute('d',alt_row_color_drawpath(structure,doc_width,max_lhs,doc_height))
svg.appendChild(alt_color_path)
headertextNode = xml.createElement("text")
headertextNode.setAttribute('font-size',str(font_size))
headertextNode.setAttribute('style','text-anchor:middle;fill:#9b9b9b;font-family:"Arial"')
headertextNode.setAttribute('x',str(int(doc_width/2)))
headertextNode.setAttribute('y',str(text_start_y))
svg.appendChild(headertextNode)
headertext = xml.createTextNode(structure[0][0][0])
headertextNode.appendChild(headertext)
credittextnode = xml.createElement("text")
credittextnode.setAttribute('font-size',str(font_size))
credittextnode.setAttribute('style',"text-anchor:start;text-align:start;fill:#9b9b9b;font-family:'Arial'")
svg.appendChild(credittextnode)
tspans(structure[1:],doc_width,credittextnode,xml,max_lhs)

xml_str = xml.toprettyxml(indent ="\t",standalone="no")
print(args.outfile)
with open(args.outfile, "w") as f:
    f.write(xml_str)
