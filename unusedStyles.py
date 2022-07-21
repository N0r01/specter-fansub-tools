#!/usr/local/bin/python3
import os,sys,pysubs2,glob,shutil,re,string

#make sure you have pysubs2 libraries installed
#pip install pysubs2

#make sure we have an ass file
if len(sys.argv) != 2:
	print("script usage: \n" + sys.argv[0] + " <ass script>")
	sys.exit(1)

#make sure the ass file exists
ass_file = sys.argv[1]
ass_path = os.path.join(os.getcwd(), ass_file)
if not os.path.isfile(ass_path):
	raise ValueError(ass_path + ' is this the right ass file?')

doc = pysubs2.SSAFile.load(ass_file)

#find all styles that are *actually* being used
used_styles_names = set([x.style for x in doc.events])
unused_styles = set([x for x,y in doc.styles.items() if x not in used_styles_names])
missing_styles = set([x for x in used_styles_names if x not in doc.styles.keys()])
if len(unused_styles) > 0:
	print("UNUSED STYLES:\n" + "\n".join(unused_styles) + "\n\n")

if len(used_styles_names) > 0:
	print("USED STYLES:\n" + "\n".join(used_styles_names) + "\n\n")

if len(missing_styles) > 0:
	print("WARNING: MISSING STYLES\n" + "\n".join(missing_styles) + "\n\n")