# -*- coding: utf-8 -*-
import uuid
import re
from typing import Callable
from reportlab.pdfbase import pdfmetrics
# Units assume 72 DPI
cm = 72.0 / 2.54  # length in 1/72 of an inch
mm = 72.0 / 25.4
units = {"cm": cm, "mm": mm}


def getid(iid):
    return '_' + (str(iid).replace(" ", "") if iid else str(uuid.uuid1()))


def defaultfont(font):
    if font is None:
        return "Helvetica", 10
    elif font[0] is None:
        return "Helvetica", font[1]
    return font


def detag(text: str):
    """
    Remove tags from the text, if any, and escape the < and > characters
    :param text:
    :return: safer text
    """
    return re.sub("<.*?>", "", text).replace(">", "&lt").replace(">", "&gt")  # Eliminate potential tags


def stringwidth(text, fontname="Helvetica", fontsize=10.0):
    return pdfmetrics.stringWidth(text, fontname, fontsize)


def textwrapsub(text, width, fontsize, fontname, breakwords, subsuper: Callable, nicewrap=False) -> []:
    """
    Wraps text to form paragraphs with a certain max. width + process sub/superscript marks (_ and ^)
    :param text: the text of a paragraph
    :param width: the maximum width
    :param fontsize:
    :param fontname:
    :param breakwords:
    :param subsuper: a function with arguments {sub} or {super}, size and the characters to be sub/susper-scripted,
                     and returning a string using the syntax needed for the output format
    :param nicewrap: if True, adjust the width of the text box to "balance" text between the lines
                     (experimental, use with care!)
    :return: a list of tuples: (line, line_width)
    """
    smallsize = fontsize * 0.7  # Font for the sub/superscripts
    wrapwidth = width - fontsize * 0.2  # Changed in v 2.1: with at which wrap absolutely needs to be done.
    if nicewrap:
        sw = 1.10 * stringwidth(text, fontsize=fontsize)
        wrapwidth = min(width, sw / (int(sw / wrapwidth) + 1) + 4 * fontsize)
    lines: list[tuple[str, float]] = []
    line = ""
    curwidth = 0.0  # The current width of the line during processing
    scriptlev = None
    scriptstr = ""
    breakafter = " ,.-"
    breakbefore = "bcdghjklmnqrstvwxz"
    text = text.replace('\r\n', '\n')
    for word in list(text.replace(" ", "¶ ").split("¶")):
        wordwidth = stringwidth(word, fontsize=fontsize)
        lw = len(word) - 1
        for ichar, char in enumerate(word):
            # Omit blank at start of new line (this may be the blank after a period)
            if char in " \n" and curwidth == 0.0:
                continue
            # Sub/superscript - processing of the special characters
            pscriptlev = scriptlev
            if char == "^":
                scriptlev = "super"
                continue
            elif char == "_":
                scriptlev = "sub"
                continue
            elif char in ' )]}."' and scriptlev:
                scriptlev = None
            # Introduction of the sub/superscript in the line (there cannot be a line break within it)
            if scriptlev:
                scriptstr += char
                curwidth += stringwidth(char, fontsize=smallsize)
                if ichar < lw:
                    continue
                else:
                    char = ""
            if pscriptlev:
                line += subsuper(pscriptlev, smallsize, scriptstr)
                scriptstr = ""
            # Line wrapping
            curwidth += stringwidth(char, fontsize=fontsize)
            # Main criteria: don't break too early or too late in word (better use space), may do it before a consonant.
            # Note: breaknow = True only when breaking is really needed - characters might be compressed to fit
            breaknow = (ichar > 3 and curwidth > wrapwidth and ichar + 3 < len(word))  \
                and char in breakbefore and breakwords
            if (curwidth + min(wordwidth, 5*fontsize) > wrapwidth and (char in breakafter or breaknow)) or char == "\n":
                if char in breakafter:
                    if char == " ":  # Avoid white spaces at the end of lines (they would mess up right alignment)
                        curwidth -= stringwidth(" ", fontsize=fontsize)
                    else:
                        line += char
                elif char not in " \n":  # Reached when it is a "breakbefore" (a consonant)
                    line += "-"
                    curwidth += stringwidth("-", fontsize=fontsize) - stringwidth(char, fontsize=fontsize)
                else:
                    curwidth -= stringwidth(char, fontsize=fontsize)  # This char is ignored, hence not in width
                lines.append((line, curwidth))
                curwidth = 0.0
                # Prepare for the next line:
                if char in breakafter or char == "\n":
                    line = ""
                else:
                    line = char
                    curwidth += stringwidth(char, fontsize=fontsize)
                continue
            # Add the character, if it did not need any specific processing above
            line += char

    # Add the last line
    lines.append((line, curwidth))

    return lines
