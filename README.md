# Specter Fansub Tools
Miscellaneous tools that aid in the task of anime fansubbing. These are being released free of charge in hopes that they might be useful to somebody. These are mostly written in python, because this is the author's scripting lanaguage of choice at the moment. Information about prerequisite libraries will be in the help printout of each script. Not every script requires every prerequisite

### fontimport.py
Analyses all the fonts referenced in a .assfile, and then pulls those fonts from folder/dir with a large collection of fonts into a new folder. It also optimizes the fonts by only including glyphs that are needed. Useful when paired with subkt.

### credits_svg.py / credits_ascii.py
Generates a table in svg or ascii. Used to neatly format a list of contributers to a fansub project. Input is a text file formated to a very simple DSL.

