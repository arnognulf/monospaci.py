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

nextArgIsNamesList = False
for arg in sys.argv:
    index = index + 1
    if nextArgIsNamesList :
        namesList = arg
        nextArgIsNamesList = False
        continue
    if arg == '-nameslist':
        nextArgIsNamesList = True
        continue

for arg in sys.argv:
    if len(arg) > 4:
        if arg[-4:] == '.ttf' or arg[-4:] == '.TTF' or arg[-4:] == '.otf' or arg[-4:] == '.OTF' or arg[-4:] == '.otf' or arg[-4:] == '.SFD' or arg[-4:] == '.sfd':
            fontList.append(arg)
        if arg[-5:] == '.glif' or arg[-5:] == '.GLIF':
            glifs.add(arg)
    index = index + 1
mergedFont = fontforge.open(fontList[0])
supplement = " Mono"
fontName = mergedFont.fontname + supplement

## use the following ASCII chars as baseWidthChars
## the baseWidth will determine the max width
baseWidthChars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y', 'z']

## scale all capital letters by at least the same factor as the following letters
capitalWidthChars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'X', 'Y', 'Z']

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

## preserve aspect correction for some chars
preserveAspectChars = set() 

for name in unicodeNames.keys():
    if name.find("CIRCLED") > 0:
        preserveAspectChars.add(unicodeNames[name])

    if name == "REGISTERED SIGN":
        preserveAspectChars.add(unicodeNames[name])

    if name == "COPYRIGHT SIGN":
        print name
        preserveAspectChars.add(unicodeNames[name])

#############################################################

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

mergedFontUnicodePoints = set()
for glyphName in mergedFont:
    unicodePoint = mergedFont[glyphName].unicode
    if unicodePoint > 0:
        mergedFontUnicodePoints.add(unicodePoint)

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
for glif in glifs :
    pos = os.path.basename(glif).find('_')
    if pos > 0:
        mergedFont[os.path.basename(glif)[0:pos]].clear()
        mergedFont[os.path.basename(glif)[0:pos]].importOutlines(glif)

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

