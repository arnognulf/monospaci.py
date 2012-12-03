Monospaci.Py
============

monospaci.py is a Python script utilizing [Fontforge](http://fontforge.org), [ttftable](http://search.cpan.org/~mhosken/Font-TTF-Scripts-1.03/scripts/ttftable), and [ttfautohint] (http://www.freetype.org/ttfautohint/) to scale ordinary variable-width fonts to fixed-width suitable for programming in IDE:s, text editors or terminal emulators.

Motivation
---
Originally this script was created due to the authors favour of Serif:ed fonts and the general lack of such high quality Serif:ed fonts (there are like three of them[1]), and a bazillion of Monospace Sans fonts[2].
Thus this script became a biproduct of trying to making the venerable Computer Modern fit into a Terminal.

How
---
Lowercase letters are kept as-is (with the exceptions of m and w).
Uppercase letters are re-scaled in width to fit the lower case ones.
The re-scaling works somewhat, due to most text being lowercase, and most lowercase letters having the same width (with the notable exception of i,j,w, and m).

Drawbacks
---------
The kerning may get slightly off, but I haven't been bothered by this much, also uppercase letters can get quite badly scaled (note 'Q' in Garamond below, 'M', and 'W' may in some cases get too thin lines.

Examples
--------
Some examples below, do note that the depicted fonts aren't available from here, but easily re-created from the linked Original sources:

![C with JUnicode Mono](https://github.com/arnognulf/monospaci.py/raw/master/images/junicode_c.png)

JUnicode, excellent for studying old languages. ([Original](http://junicode.sourceforge.net/))

![.vimrc with Sniglet Mono](https://github.com/arnognulf/monospaci.py/raw/master/images/sniglet_ftw.png)

Sniglet Mono, when your vim needs more kittens. ([Original](https://github.com/theleagueof/sniglet))

![C++ with EB Garamond Mono](https://github.com/arnognulf/monospaci.py/raw/master/images/garamond_cpp.png))

EB Garamond Mono, when your C++ isn't classy enough ([Original](http://www.georgduffner.at/ebgaramond/))

![Python with Fifth Leg Mono](https://github.com/arnognulf/monospaci.py/raw/master/images/squared_python.png))

Fifth Leg Mono, thinking inside the box with Python ([Original](http://gitorious.org/opensuse/art/trees/master/00assets/fonts))

![Java with Comic Sans MS Mono](https://github.com/arnognulf/monospaci.py/raw/master/images/java_fun.png)

Comic Sans MS Mono, really makes your Java pop!

![JavaScript with Papyrus Mono](https://github.com/arnognulf/monospaci.py/raw/master/images/classy_javascript.png)

Papyrus Mono, give your JavaScript that antique look!

[1]: "Courier, Century SchoolBook Mono BT, and Verily Serif"
[2]: "Too many to mention"
