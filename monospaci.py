#!/usr/bin/python
#
import fontforge
import psMat
import subprocess
import sys

baseFont = fontforge.open(sys.argv[1])
namesList = "NamesList.txt"
mergeFonts = set()

index = 0
argv = sys.argv
for arg in argv:
    if index != 0 or index != 1:
        if len(sys.argv[index]) > 4:
            if argv[index][-4:] == '.ttf' or argv[index][-4:] == '.TTF' or argv[index][-4:] == '.otf' or argv[index][-4:] == '.OTF' or argv[index][-4:] == '.otf' or argv[index][-4:] == '.SFD' or argv[index][-4:] == '.sfd':
                mergeFonts.add(argv[index])
            if argv[index][-5:] == '.glif' or argv[index][-5:] == '.GLIF':
                print argv[index]
    index = index + 1

fontName = baseFont.fullname + " Mono"
mergedFont = baseFont

## use the following ASCII chars as baseWidthChars
## the baseWidth will determine the max width
baseWidthChars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y', 'z']

## scale all capital letters by at least the same factor as the following letters
capitalWidthChars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'X', 'Y', 'Z']

#############################################################

unicodeNamesList = open(namesList)
lines = unicodeNamesList.readlines()
unicodeNamesList.close()

unicodeNames = dict()
for line in lines:
    if line[0] == '@':
        continue
    try:
        hexval = int(line.split("\t")[0], 16)
        unicodeNames[line.split("\t")[1]] = hexval
    except:
        continue

maxWidth = -1.0
avgSpacing = 0.0
for char in baseWidthChars :
    bounds = mergedFont[char].boundingBox()
    maxWidth = max(maxWidth, bounds[2] - bounds[0])
    avgSpacing = avgSpacing + bounds[0] + mergedFont[char].width - bounds[2]

avgSpacing = avgSpacing / len(baseWidthChars) / 2

capitalLetterWidth = -1
capitalLetterScale = 1.0
for char in capitalWidthChars:
    bounds = mergedFont[char].boundingBox()
    capitalLetterScale = min(capitalLetterScale, (maxWidth - avgSpacing*2)/(bounds[2]-bounds[0]))
    capitalLetterWidth = max(capitalLetterWidth, bounds[2]-bounds[0])

capitalLetters = set()
for name in unicodeNames:
    findName = "LATIN CAPITAL LETTER "
    if name.find(findName) == 0:
        capitalLetters.add(unicodeNames[name])
    findName = "CYRILLIC CAPITAL LETTER "
    if name.find(findName) == 0:
        capitalLetters.add(unicodeNames[name])
    findName = "GREEK CAPITAL LETTER "
    if name.find(findName) == 0:
        capitalLetters.add(unicodeNames[name])
    findName = "ARMENIAN CAPITAL LETTER "
    if name.find(findName) == 0:
        capitalLetters.add(unicodeNames[name])

maxHeight = -1.0
for char in baseWidthChars:
    bounds = mergedFont[char].boundingBox()
    maxHeight = max(maxHeight, bounds[3] - bounds[1])

## allow 1.5 linespacing
maxHeight = maxHeight * 1.5 - avgSpacing*2

baseFontUnicodePoints = set()
for glyphName in baseFont:
    unicodePoint = baseFont[glyphName].unicode
    if unicodePoint > 0:
        baseFontUnicodePoints.add(unicodePoint)

for anchorClass in ["mark", "base", "ligature", "basemark", "entry", "exit"]:
    try:
        mergedFont.removeAnchorClass(anchorClass)
    except:
        pass

## something's fishy in Fontforge's width properties
widthDict = dict()
for glyphName in mergedFont:
    widthDict[glyphName] = mergedFont[glyphName].width

for glyphName in mergedFont:

    bounds = mergedFont[glyphName].boundingBox()
    origWidth = bounds[2] - bounds[0]
    glyphWidth = bounds[2] - bounds[0]

    if mergedFont[glyphName].unicode in capitalLetters :
        if glyphWidth < capitalLetterWidth:
            glyphWidth = capitalLetterWidth 

    if glyphWidth > maxWidth:
        try:
            mergedFont[glyphName].transform(psMat.scale((maxWidth - avgSpacing*2)/(glyphWidth),1))
            mergedFont[glyphName].transform(psMat.translate(avgSpacing+(glyphWidth-origWidth)/2.0,0.0))
        except:
            pass
    else:
        moveDistance = (maxWidth + avgSpacing*2 - widthDict[glyphName])/2.0
        mergedFont[glyphName].transform(psMat.translate(moveDistance,0.0))

    mergedFont[glyphName].width = maxWidth + avgSpacing*2
    bearing = (mergedFont[glyphName].left_side_bearing + mergedFont[glyphName].right_side_bearing)/2.0

## override some broken glyphs
#mergedFont['i'].clear()
#mergedFont['i'].importOutlines("orig/i_TeXLove.glif")
#mergedFont['i'].width = maxWidth + avgSpacing*2
#mergedFont['j'].clear()
#mergedFont['j'].importOutlines("orig/j_TeXLove.glif")
#mergedFont['j'].width = maxWidth + avgSpacing*2

## remove some ligatures, since these may show up in Microsoft's ttf renderer (eg. VS2012)
## this is problematic in a monospace font since it combines two or three chars into one,
## making the width harder to guess
try:
    mergedFont[0xfb00].clear() # ff
except:
    pass
try:
    mergedFont[0xfb01].clear() # fi
except:
    pass
try:
    mergedFont[0xfb02].clear() # fl
except:
    pass
try:
    mergedFont[0xfb03].clear() # ffi
except:
    pass
try:
    mergedFont[0xfb04].clear() # ffl
except:
    pass

## set name and values
mergedFont.fontname = fontName 
mergedFont.fullname = fontName 
mergedFont.familyname = fontName
#mergedFont.os2_vendor = vendorName
mergedFont.os2_panose = (2, 9, 5, 9, 0, 0, 0, 0, 0, 0) 
mergedFont.os2_fstype = 8

fontForgeOutput = fontName + "-Output.ttf"
ttfAutoHintOutput = "TTFAutoHint-Output.ttf"
finalOutput = fontName.replace(" ","-")+ "-Regular.ttf"

mergedFont.generate(fontForgeOutput)

## ttfautohint mangles our OS/2 table, containing vital Monospace bits, stash away...
subprocess.call(["ttftable", "-export", "OS/2=os2.fontforge", fontForgeOutput])
## ttfautohint outputs GDI ClearType hinting
subprocess.call(["ttfautohint", "-w", "G", fontForgeOutput, ttfAutoHintOutput])
## restore our saved OS/2 table
subprocess.call(["ttftable", "-import", "OS/2=os2.fontforge", ttfAutoHintOutput, finalOutput])
len(mergedFont)
exit(0)

