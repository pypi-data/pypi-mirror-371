# -*- coding: utf-8 -*-
"""
Interface to drawing libraries: starting point
"""
import embermaker.drawinglib.canvas_svg as can_svg
import embermaker.drawinglib.canvas_pdf as can_pdf

def get_canvas(outfile, colorsys="RGB", size=(1,1), grformat="PDF"):
    """
    Gets a draw canva
    colorsys = RGB or CMJN
    size = (width, height)
    grformat = PDF | SVG | SVG-C; the latter defines colors trough classes instead of styles, and provides a dark mode
    """
    grformat = grformat.upper()
    if grformat == "PDF":
        return can_pdf.CanvasPdf(outfile, colorsys, size)
    elif "SVG" in grformat:
        return can_svg.CanvasSvg(outfile, colorsys, size, use_css= "-C" in grformat)
    else:
        raise ValueError (f"Unknown file/canvas format: {grformat}")