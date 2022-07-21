#!/usr/bin/env python3

import os,sys,glob,shutil,re,string,subprocess
print("Super Scuffed Font import/optimization for anime typesetting version 0.0.1 by Noroino Hanako")
print("note: make sure you have pysubs2, fontTools, and argparse python libraries installed")
print("Also make sure you're running this with Python 3")
print("usage example:")
print("$ ./fontimport.py --assfile subtitles.ass --inputfontdir /dir/with/all/my/fonts --outputfontdir /dir/to/write/to/fontdir")
import pysubs2,argparse,argcomplete,fileinput
import xml.etree.cElementTree as etree
from fontTools.ttLib import TTFont
from fontTools.subset import main as FTsubset

parser = argparse.ArgumentParser(description='Strip fonts used in an ass file so that only glyphs used in that ass files are included. All arguments are required.')
parser.add_argument('-i', '--inputfontdir',required=True, help='specify the folder/dir with all your fonts')
parser.add_argument('-o', '--outputfontdir',required=True, help='specify an EMPTY folder/dir where you want your stripped fonts to be written to. If it does not exist, this folder will be created')
parser.add_argument('-a', '--assfile', required=True, help='name of the ASS subtitle file').completer = argcomplete.completers.FilesCompleter(['ass'], directories=False)
args = parser.parse_args()

#Are we optimizing fonts?
optimizing_fonts = True

#make sure the ass file exists
ass_file = args.assfile
ass_path = os.path.join(os.getcwd(), ass_file)
if not os.path.isfile(ass_path):
	raise ValueError(ass_path + ' does not exist?)')

temp_fonts_folder = args.outputfontdir
temp_fonts_path = os.path.join(os.getcwd(), temp_fonts_folder)
global_fonts_folder = args.inputfontdir
global_fonts_path = os.path.join(os.getcwd(), global_fonts_folder)

#make sure the global fonts directory exists
if not os.path.isdir(global_fonts_path):
	raise ValueError('global shared font path ' + global_fonts_path + " does not exist. Is this the right path?")

#make sure the local fonts directory exists
if not os.path.isdir(temp_fonts_path):
	print('font path ' + temp_fonts_path + " does not exist. Creating it.")
	os.mkdir(temp_fonts_path)

#list all unique fonts
ass_fonts_names = []
doc = pysubs2.SSAFile.load(ass_file)

#find all styles that are *actually* being used
used_styles_names = set([x.style for x in doc.events])
ass_fonts_names = set([y.fontname for x,y in doc.styles.items() if x in used_styles_names])
print("UNIQUE FONTS :\n" + "\n".join(ass_fonts_names) + "\n")

#for informational purposes only
unused_fonts_names = set([y.fontname for x,y in doc.styles.items() if y.fontname not in ass_fonts_names])
if len(unused_fonts_names) > 0:
	unused_styles = set([x for x,y in doc.styles.items() if y.fontname not in ass_fonts_names])
	print("UNUSED FONTS :\n" + "\n".join(unused_fonts_names) + "\n")
	print("Consider deleting these unused styles:\n" + "\n".join(unused_styles) + "\n")

#Detect if we're using the \fn tag because that's going to be missed by this script.
fn_fontset = set([])
fn_matches = [x for x in doc.events if re.search("\\\\fn",x.text)]
if len(fn_matches) > 0:
	print("\nWARNING: \\fn tag found on the following events:")
	for x in fn_matches:
		print(str(x))
	for fns in [re.findall("\\\\fn[^}\\\\]*",y.text) for y in fn_matches]:
		for x in fns:
			addfont = x[3:]
			print("adding " + addfont + " from " + x)
			fn_fontset.add(addfont)
	for x in fn_fontset:
		print(x)
ass_fonts_names = ass_fonts_names.union(fn_fontset)

#filter out any stray @at characters that aegisub inexplicably puts in
ass_fonts_names = [re.sub("^@","",x) for x in ass_fonts_names]

#search global font dir for fonts with font name
font_files = glob.glob(global_fonts_path + "/*.[a-zA-Z][a-zA-Z][a-zA-Z]")
print(global_fonts_path)
print("candidate font files :\n" + "\n".join(font_files))
font_name_to_file_dict = dict()

def find_name_in_records(records):
	retval = []
	for record in records:
		if b'\x00' in record:
			filtered_string = record.decode('utf-16-be')
		else:
			filtered_string = record.decode('latin-1')
		if filtered_string in ass_fonts_names:
			retval.append(filtered_string)
	if len(retval) == 0:
		return None
	return set(retval)

for font_file_path in font_files:
	font = TTFont(font_file_path,fontNumber=0)
	#the way fonts store their "name" is somewhat exoteric...
	#see https://docs.microsoft.com/en-us/typography/opentype/spec/name for nameID descriptions
	#But yeah we should prioritize whatever's stored with the Full font name
	nameRecords = [x.string for x in font.get("name").names if x.nameID == 4]
	nameRecords = nameRecords + [x.string for x in font.get("name").names if x.nameID in [1,6,16]]
	nameRecords = nameRecords + [x.string for x in font.get("name").names if x.nameID in [20,21,22,25]]
	font_names = find_name_in_records(nameRecords)
	if font_names is not None:
		for font_name in font_names:
			font_name_to_file_dict[font_name] = font_file_path
			print("matching name record in " + font_file_path + " for " + font_name)
	#else:
		# print("no matching name record in " + font_file_path)

#check to see that we have all the fonts we need,
need_to_exit = False
for font_needed in ass_fonts_names:
	if font_needed not in font_name_to_file_dict.keys():
		print("ERROR: MISSING FONT FILE FOR FONT WITH NAME: " + font_needed)
		need_to_exit = True
if need_to_exit:
	print("ABORTING.")
	sys.exit(1)

#todo: remove need to copy directly
optimized_fonts = []
for file in font_name_to_file_dict.values():
	not_optimizing_for_other_reasons = False
	problematic_fonts = ["SitkaText.ttf"] 	#problematic font(s) that we are not dealing with
	if optimizing_fonts:
		for problematic_font in problematic_fonts:
			if len(re.findall(problematic_font,file)) > 0:
				print("problematic font " + file + " encountered, copying instead")
				not_optimizing_for_other_reasons = True
	if not_optimizing_for_other_reasons or not optimizing_fonts:
		print("copying " + file + " to " + temp_fonts_path)
		shutil.copy(file,temp_fonts_path + "/")
	else:
		tofilepath = temp_fonts_path + "/" + "optimized_" + re.sub(".*/","",re.sub(" ","_",file))
		optimized_fonts.append(tofilepath)
		print("subsetting " + file + " to " + tofilepath)
		sys.argv = [None, file, '--text-file='+ass_file, '--output-file='+tofilepath]
		FTsubset()

print("Renaming optimized fonts")
for font_path in optimized_fonts:
	subprocess.call(["ttx", "-otemptxx", font_path])
	name_mapping = {}
	for event, elem in etree.iterparse("temptxx", events=["start"]):
		if elem.tag == "namerecord" and elem.attrib.get("nameID", None) == "1":
			nt = elem.text.replace('\n', '').rstrip()
			name_mapping[nt] = f"{nt.rstrip()}.subset"
		if elem.tag == "namerecord" and elem.attrib.get("nameID", None) == "4":
			nt = elem.text.replace('\n', '').rstrip()
			name_mapping[nt] = f"{nt.rstrip()}.subset"
		if elem.tag == "namerecord" and elem.attrib.get("nameID", None) == "6":
			nt = elem.text.replace('\n', '').rstrip()
			name_mapping[nt] = f"{nt.rstrip()}.subset"
	for line in fileinput.input("temptxx", inplace=True):
		if line.replace('\n', '').rstrip() in name_mapping.keys():
		    line = name_mapping[line.replace('\n', '').rstrip()] + "\n"
		print(line, end="")
	os.remove(font_path)
	subprocess.call(["ttx", f"-o{font_path}", "temptxx"])
	os.remove("temptxx")
