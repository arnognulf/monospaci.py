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
finalWidthScale = 1.0
nextArgIsNamesList = False
nextArgIsWidthScale = False
nextArgIsPSName = False
nextArgIsFullName = False
nextArgIsCopyright = False
nextArgIsXAdjust = False
nextArgIsLeadingScale = False
nextArgIsFamilyName = False
nextArgIsNoScaleChar = False

copyright = ""
psName = ""
fullName = ""
verbose = False
xadjust = 0
leadingScale = 0.0
familyName = ""
index = 0
firstArg = True
noScaleChars = list()
baseFont = None
for arg in sys.argv:
    index = index + 1
    if firstArg:
        firstArg = False
        continue
    if nextArgIsXAdjust :
        xadjust = arg
        nextArgIsXAdjust = False
        continue
    if nextArgIsCopyright :
        nextArgIsCopyright = False
        copyright = arg
        continue
    if nextArgIsNamesList :
        namesList = arg
        nextArgIsNamesList = False
        continue
    if nextArgIsWidthScale :
        nextArgIsSpaceFactor = False
        finalWidthScale = float(arg)
        continue
    if nextArgIsPSName :
        nextArgIsPSName = False
        psName = arg
        continue
    if nextArgIsFamilyName :
        nextArgIsFamilyName = False
        familyName = arg
        continue
    if nextArgIsFullName :
        nextArgIsFullName = False
        fullName = arg
        continue
    if nextArgIsLeadingScale:
        nextArgIsLeadingScale = False
        leadingScale = float(arg)
        continue
    if nextArgIsNoScaleChar:
        nextArgIsNoScaleChar = False
        noScaleChars.append(arg)
        continue
    if arg == '-nameslist':
        nextArgIsNamesList = True
        continue
    if arg == '-widthscale':
        nextArgIsWidthScale = True
        continue
    if arg == '-verbose':
        verbose = True
        continue
    if arg == '-psname':
        nextArgIsPSName = True
        continue
    if arg == '-fullname':
        nextArgIsFullName = True
        continue
    if arg == '-copyright':
        nextArgIsCopyright = True
        continue
    if arg == '-xadjust':
        nextArgIsXAdjust = True
        continue
    if arg == '-leadingscale':
        nextArgIsLeadingScale = True
        continue
    if arg == '-familyname':
        nextArgIsFamilyName = True
        continue
    if arg == '-noscalechar':
        nextArgIsNoScaleChar = True
        continue
    print 'opening ' + arg
    font = fontforge.open(arg)

    if baseFont == None:
        baseFont = font
    else:
        fontList.append(font)
    if arg[-5:] == '.glif' or arg[-5:] == '.GLIF':
        glifs.add(arg)

if baseFont == None:
    print "could not open font"
    exit(42)

mergedFont = baseFont 
#mergedFont.encoding = 'UnicodeBmp'
supplement = " Mono"
oldname = "UnnamedFont"
if mergedFont.fontname != None:
    oldname = mergedFont.fontname

mergedFont.sfnt_names = ()
fontName = oldname + supplement
if len(psName) > 0:
    fontName = psName 

## set name and values
mergedFont.fontname = fontName
#mergedFont.fontname = fontName.replace(" ","")
if len(fullName) > 0:
    mergedFont.fullname = fullName
else:
    mergedFont.fullname = fontName.replace(" ","_")
if len(familyName) > 0:
    mergedFont.familyname = familyName
else:
    mergedFont.fullname = fontName

if mergedFont.fontlog == None:
   mergedFont.fontlog = ""
mergedFont.fontlog = mergedFont.fontlog + "Modified into monospace by monospaci.py (https://github.com/arnognulf/monospaci.py)\n"
mergedFont.os2_panose = (2, 9, 5, 9, 0, 0, 0, 0, 0, 0) 
mergedFont.os2_fstype = 8
mergedFont.copyright = copyright

## use the following ASCII chars as baseWidthChars
## the baseWidth will determine the max width
baseWidthChars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y', 'z']

## scale all capital letters by at least the same factor as the following letters
capitalWidthChars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'K', 'L', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'X', 'Y', 'Z']

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

    newUnicodeRanges = ( mergedFont.os2_unicoderanges[0] | complementFont.os2_unicoderanges[0], mergedFont.os2_unicoderanges[1] | complementFont.os2_unicoderanges[1], mergedFont.os2_unicoderanges[2] | complementFont.os2_unicoderanges[2], mergedFont.os2_unicoderanges[3] | complementFont.os2_unicoderanges[3] )
    mergedFont.os2_unicoderanges = newUnicodeRanges
    newCodepages = ( mergedFont.os2_codepages[0] | complementFont.os2_codepages[0], mergedFont.os2_codepages[1] | complementFont.os2_codepages[1])
    mergedFont.os2_codepages = newCodepages
    mergedFontUnicode =  successfulMergeUnicodePoints | mergedFontUnicodePoints


maxWidth = -1.0
avgSpacing = 0.0
for char in baseWidthChars :
    bounds = mergedFont[char].boundingBox()
    maxWidth = max(maxWidth, bounds[2] - bounds[0])
    avgSpacing = avgSpacing + bounds[0] + mergedFont[char].width - bounds[2]

avgSpacing = avgSpacing / len(baseWidthChars) / 2
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

## remove all references to other glyphs, since these may distort some glyphs when scaling
for glyphName in mergedFont:
    mergedFont[glyphName].unlinkRef()

for glyphName in mergedFont:
    bounds = mergedFont[glyphName].boundingBox()

    unicodePoint = mergedFont[glyphName].unicode
    newBounds = mergedFont[glyphName].boundingBox()
    origWidth = newBounds[2] - newBounds[0]
    glyphWidth = origWidth

    ## handle the tail in uppercase Q gracefully
    ## this is espcially important in Garamond, but may be the case in other
    ## other fonts as well.
    #if unicodePoint in [ unicodeNames["LATIN CAPITAL LETTER Q"]]:
    #    newBounds = mergedFont[unicodeNames["LATIN CAPITAL LETTER O"]].boundingBox()
    #    origWidth = newBounds[2] - newBounds[0]
    #    glyphWidth = avgCapitalLetterWidth
    #
    #elif unicodePoint in capitalLetters :
    if unicodePoint in capitalLetters :
        ## make sure I and J also get scaled, otherwise their stems may 
        ## become overly thicker than other capital letters
        if glyphWidth < avgCapitalLetterWidth :
            glyphWidth = avgCapitalLetterWidth

    ## TODO: this value is bogus and may not be valid for non-CJK/latin fonts
    if unicodePoint >= 0x2E9D:
        if verbose:
            print sys.argv[0] + ": doubleWidth: " + unicodePoint
    elif glyphWidth > maxWidth :
        try:
            heightScale = 1.0
            if glyphName in noScaleChars :
                widthScale = 1.0
            else:
                widthScale = (maxWidth)/(glyphWidth)

            #widthScale = (glyphWidth)/(maxWidth)
            if unicodePoint in preserveAspectChars :
                heightScale = widthScale
        
            horiz = xadjust + avgSpacing - newBounds[0] + (glyphWidth-origWidth)/2.0

            mergedFont[glyphName].transform(psMat.scale(widthScale,heightScale))
            vert = 0.0
            mergedFont[glyphName].transform(psMat.translate(horiz,vert))
            if verbose :
                print sys.argv[0] + ": " + nameUnicodes[unicodePoint] + " scale width=" + str(widthScale) + ", height=" + str(heightScale)
                print sys.argv[0] + ": " + str(nameUnicodes[unicodePoint]) + " translate horiz=" + str(widthScale) + ", vert=" + str(heightScale)
        except:
            pass
    else:
        horiz = xadjust + (maxWidth + avgSpacing*2 - widthDict[glyphName])/2.0
        vert = 0.0
        mergedFont[glyphName].transform(psMat.translate(horiz,vert))
        name = ""
        if unicodePoint in nameUnicodes :
            name = nameUnicodes[unicodePoint]
        if verbose :
            print sys.argv[0] + ": " + name + " translate horiz=" + str(widthScale) + ", vert=" + str(heightScale)

    mergedFont[glyphName].width = finalWidthScale * (maxWidth + avgSpacing*2)
    if verbose :
        name = ""
        if unicodePoint in nameUnicodes.keys():
            name = nameUnicodes[unicodePoint]
        else:
            name = str(unicodePoint)


        print sys.argv[0] + ": " + name + " width="+str(mergedFont[glyphName].width)
       

## override some broken glyphs
if len(glifs) > 0:
    for glif in glifs :
        pos = os.path.basename(glif).find('_')
        if pos > 0:
            glyphIndex = os.path.basename(glif)[0:pos]
            try:
                mergedFont[glyphIndex].clear()
                mergedFont[glyphIndex].importOutlines(glif)
                mergedFont[glyphIndex].width = maxWidth + avgSpacing*2
            except:
                pass

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

## trial-and-error estimation of linespacing in css
if leadingScale != 0.0:
    capHeight = mergedFont.capHeight
    mergedFont.hhea_ascent_add = 0
    mergedFont.hhea_descent_add = 0
    mergedFont.hhea_linegap = 0
    mergedFont.os2_winascent_add = 1
    mergedFont.os2_windescent_add = 1
    mergedFont.os2_typoascent_add = 1
    mergedFont.os2_typodescent_add = 1
    mergedFont.os2_typoascent = 0 
    mergedFont.os2_typodescent = 0
    mergedFont.hhea_linegap = 0

    leadPadding = (float(capHeight) * leadingScale - (capHeight)) / 2.0
    mergedFont.hhea_ascent = capHeight + capHeight*0.10 + leadPadding
    mergedFont.hhea_descent = -1 * leadPadding - capHeight*0.40

    ## doesn't make a difference in linux, untested in windows
    mergedFont.os2_winascent = mergedFont.hhea_ascent
    mergedFont.os2_windescent = mergedFont.hhea_descent

ttfAutoHintInput = "TTFAutoHint-Input.ttf"
finalOutput = fontName.replace(" ","-")+ ".ttf"

mergedFont.generate(ttfAutoHintInput, flags=('PfEd-comments',))

## ttfautohint outputs GDI ClearType hinting
subprocess.call(["ttfautohint", "-w", "G", ttfAutoHintInput, finalOutput])
exit(0)

