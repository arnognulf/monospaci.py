#!/usr/bin/python
#
# monospaci.py is copyright (C) 2012 
# by Thomas Eriksson.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
#   WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#   MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
#   EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
###############################################################################

import fontforge
import psMat
import subprocess
import sys
import os.path
namesList = "NamesList.txt"
fontList = list()
glifs = set()
index = 0
spaceFactor = 1.0
nextArgIsNamesList = False
nextArgIsSpaceFactor = False
nextArgIsName = False
name = ""
verbose = False
for arg in sys.argv:
    index = index + 1
    if nextArgIsNamesList :
        namesList = arg
        nextArgIsNamesList = False
        continue
    if nextArgIsSpaceFactor :
        nextArgIsSpaceFactor = False
        spaceFactor = float(arg)
        continue
    if nextArgIsName :
        nextArgIsName = False
        name = arg
        continue
    if arg == '-nameslist':
        nextArgIsNamesList = True
        continue
    if arg == '-spacefactor':
        nextArgIsSpaceFactor = True
        continue
    if arg == '-verbose':
        verbose = True
        continue
    if arg == '-name':
        nextArgIsName = True
        continue

baseFont = None
for arg in sys.argv:
    if len(arg) > 4:
        if arg[-4:] == '.ttf' or arg[-4:] == '.TTF' or arg[-4:] == '.otf' or arg[-4:] == '.OTF' or arg[-4:] == '.otf' or arg[-4:] == '.SFD' or arg[-4:] == '.sfd':
            font = fontforge.open(arg)
            if baseFont == None:
                baseFont = font
            else:
                fontList.append(font)
        if arg[-5:] == '.glif' or arg[-5:] == '.GLIF':
            glifs.add(arg)
    index = index + 1

mergedFont = baseFont 
supplement = " Mono"
fontName = mergedFont.fontname + supplement
if len(name) > 0:
    fontName = name 

## use the following ASCII chars as baseWidthChars
## the baseWidth will determine the max width
baseWidthChars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y', 'z']

## scale all capital letters by at least the same factor as the following letters
capitalWidthChars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'K', 'L', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'X', 'Y', 'Z']

unicodeNamesList = open(namesList)
lines = unicodeNamesList.readlines()
unicodeNamesList.close()

unicodeNames = dict()
for line in lines:
    if line[0] == '@':
        continue
    try:
        hexval = int(line.split()[0], 16)
        name = line[len(line.split("\t")[0]):-1].lstrip().rstrip()
        
        unicodeNames[name] = hexval
    except:
        continue

nameUnicodes = dict()
for name in unicodeNames.keys():
    nameUnicodes[unicodeNames[name]] = name

## preserve aspect correction for some chars
preserveAspectChars = set() 
for name in unicodeNames.keys():
    for name in ["REGISTERED SIGN", "COPYRIGHT SIGN", "COMMERCIAL AT"]:
        preserveAspectChars.add(unicodeNames[name])

#############################################################

maxWidth = -1.0
avgSpacing = 0.0
for char in baseWidthChars :
    bounds = mergedFont[char].boundingBox()
    maxWidth = max(maxWidth, bounds[2] - bounds[0])
    avgSpacing = avgSpacing + bounds[0] + mergedFont[char].width - bounds[2]

avgSpacing = spaceFactor * avgSpacing / len(baseWidthChars) / 2
if verbose :
    print sys.argv[0]+": avgSpacing " + str(avgSpacing)
capitalLetterWidths = 0 
for char in capitalWidthChars :
    bounds = mergedFont[char].boundingBox()
    unicodePoint = mergedFont[char].unicode
    capitalLetterWidths = capitalLetterWidths + bounds[2]-bounds[0]

avgCapitalLetterWidth = capitalLetterWidths / len(capitalWidthChars)

if verbose :
    print sys.argv[0]+": avgCapitalLetterWidth: " + str(avgCapitalLetterWidth)

mergedFontUnicodePoints = set()
for glyphName in mergedFont:
    unicodePoint = mergedFont[glyphName].unicode
    if unicodePoint > 0:
        mergedFontUnicodePoints.add(unicodePoint)

for complementFont in fontList :
    complementFontGlyphs = set()

    for glyphName in complementFont:
        unicodePoint = complementFont[glyphName].unicode
        if unicodePoint > 0:
            complementFontGlyphs.add(unicodePoint)

    successfulMergeUnicodePoints = set()

    for unicodePoint in complementFontGlyphs - mergedFontUnicodePoints :
        try:
            complementFont.selection.none()
            complementFont.selection.select(("unicode",),unicodePoint)
            complementFont.copy()
            try:
                mergedFont.selection.none()
                mergedFont.selection.select(("unicode",),unicodePoint)
                mergedFont.paste()
                successfulMergeUnicodePoints.add(unicodePoint)
                if verbose :
                    print sys.argv[0] + ": imported " + nameUnicodes[unicodePoint] + " from " + complementFont.fullname
            except:
                pass
        except:
            pass

    mergedFontUnicode =  successfulMergeUnicodePoints | mergedFontUnicodePoints

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

## something's fishy in Fontforge's width properties
widthDict = dict()
for glyphName in mergedFont:
    widthDict[glyphName] = mergedFont[glyphName].width

for glyphName in mergedFont:

    bounds = mergedFont[glyphName].boundingBox()
    origWidth = bounds[2] - bounds[0]
    glyphWidth = origWidth
    newMaxWidth = maxWidth
    unicodePoint = mergedFont[glyphName].unicode
    newBounds = mergedFont[glyphName].boundingBox()

    if unicodePoint in capitalLetters :
        if glyphWidth < avgCapitalLetterWidth :
            glyphWidth = avgCapitalLetterWidth

    #if unicodePoint >= 0x2E9D and unicodePoint <= 0x4DB5 :
    if unicodePoint >= 0x2E9D:
        if verbose:
            print sys.argv[0] + ": doubleWidth: " + unicodePoint
        mergedFont[glyphName].width = 2*(newMaxWidth + avgSpacing*2)
    elif glyphWidth > maxWidth:
        try:
            heightScale = 1.0
            widthScale = (maxWidth)/(glyphWidth)
            if unicodePoint in preserveAspectChars :
                heightScale = widthScale

            mergedFont[glyphName].transform(psMat.scale(widthScale,heightScale))
            horiz = avgSpacing-newBounds[0]+(glyphWidth-origWidth)/2.0
            vert = 0.0
            mergedFont[glyphName].transform(psMat.translate(horiz,vert))
            if verbose :
                print sys.argv[0] + ": " + nameUnicodes[unicodePoint] + " scale width=" + str(widthScale) + ", height=" + str(heightScale)
                print sys.argv[0] + ": " + str(nameUnicodes[unicodePoint]) + " translate horiz=" + str(widthScale) + ", vert=" + str(heightScale)
        except:
            pass
        mergedFont[glyphName].width = newMaxWidth + avgSpacing*2
    else:
        horiz = (maxWidth + avgSpacing*2 - widthDict[glyphName])/2.0
        vert = 0.0
        mergedFont[glyphName].transform(psMat.translate(horiz,vert))
        name = ""
        if unicodePoint in nameUnicodes :
            name = nameUnicodes[unicodePoint]
        if verbose :
            print sys.argv[0] + ": " + name + " translate horiz=" + str(widthScale) + ", vert=" + str(heightScale)
        mergedFont[glyphName].width = newMaxWidth + avgSpacing*2

    if verbose :
        name = ""
        if unicodePoint in nameUnicodes.keys():
            name = nameUnicodes[unicodePoint]
        else:
            name = str(unicodePoint)


        print sys.argv[0] + ": " + name + " width="+str(mergedFont[glyphName].width)
       

## override some broken glyphs
for glif in glifs :
    pos = os.path.basename(glif).find('_')
    if pos > 0:
        glyphIndex = os.path.basename(glif)[0:pos]
        mergedFont[glyphIndex].clear()
        mergedFont[glyphIndex].importOutlines(glif)
        mergedFont[glyphIndex].width = maxWidth + avgSpacing*2

## remove some ligatures, since these may show up in Microsoft's ttf renderer (eg. VS2012)
## this is problematic in a monospace font since it combines two or three chars into one,
## making the width harder to guess
try:
    mergedFont[unicodeNames["LATIN SMALL LIGATURE FF"]].clear()
except:
    pass
try:
    mergedFont[unicodeNames["LATIN SMALL LIGATURE FI"]].clear()
except:
    pass
try:
    mergedFont[unicodeNames["LATIN SMALL LIGATURE FL"]].clear()
except:
    pass
try:
    mergedFont[unicodeNames["LATIN SMALL LIGATURE FFI"]].clear()
except:
    pass
try:
    mergedFont[unicodeNames["LATIN SMALL LIGATURE FFL"]].clear()
except:
    pass

## set name and values
mergedFont.fontname = fontName.replace(" ","")
mergedFont.fullname = fontName.replace(" ","")
mergedFont.familyname = fontName.replace(" ","")

if mergedFont.fontlog == None:
   mergedFont.fontlog = ""
mergedFont.fontlog = mergedFont.fontlog + "Modified into monospace by monospaci.py (https://github.com/arnognulf/monospaci.py)\n"
mergedFont.os2_panose = (2, 9, 5, 9, 0, 0, 0, 0, 0, 0) 
mergedFont.os2_fstype = 8

fontForgeOutput = fontName + "-Output.ttf"
ttfAutoHintOutput = "TTFAutoHint-Output.ttf"
finalOutput = fontName.replace(" ","-")+ "-Regular.ttf"

mergedFont.generate(fontForgeOutput, flags=('PfEd-comments',))

## ttfautohint mangles our OS/2 table, containing vital Monospace bits, stash away...
subprocess.call(["ttftable", "-export", "OS/2=os2.fontforge", fontForgeOutput])
## ttfautohint outputs GDI ClearType hinting
subprocess.call(["ttfautohint", "-w", "G", fontForgeOutput, ttfAutoHintOutput])
## restore our saved OS/2 table
subprocess.call(["ttftable", "-import", "OS/2=os2.fontforge", ttfAutoHintOutput, finalOutput])
len(mergedFont)
exit(0)

