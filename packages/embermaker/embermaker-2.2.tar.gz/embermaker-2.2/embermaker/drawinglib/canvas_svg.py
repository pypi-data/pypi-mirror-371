# -*- coding: utf-8 -*-
"""
Interface to drawing libraries: SVG with svg-py (svg.py)
"""
from os import path
from embermaker.drawinglib import canvas_base
from embermaker.drawinglib.helpers import cm, getid, textwrapsub, defaultfont, stringwidth, detag
import svg
import re
from typing import Optional
from io import StringIO
import numpy as np
import colorsys


def subsuper(scriptlevel, fontsize, string):
    """
    :param scriptlevel: "sub" or "super"
    :param fontsize:
    :param string:
    :return:
    Provides a string with the tag needed for sub/superscripts, for use in textwrapsub
    :return: the processed string, with SVG tags.
    """
    return f'<tspan baseline-shift="{scriptlevel}" font-size="{fontsize}">{string}</tspan>'


class ToolTippedRect(svg.Rect):
    def __init__(self, *args, data_tooltip=None, data_tooltip_dy=None, **kwargs):
        # Add optional tooltip to the Rect class in svg
        # Note: this could possibly be replaced with <desc> for better compliance with SVG-XML.
        self.data_tooltip: Optional[str] = data_tooltip
        self.data_tooltip_dy: Optional[str] = str(data_tooltip_dy) if data_tooltip_dy is not None else None
        super().__init__(*args, **kwargs)


class CanvasSvg(canvas_base.CanvasBase):

    def __init__(self, outfile=None, colorsys="RGB", size: tuple[int, int] = (400, 800), use_css=False):
        """
        Creates an SVG canvas

        :param outfile: output file path; the file extension is not taken into account. If not provided, the image
                        will be saved to a "file-like" object (stringIO)
        :param colorsys: included for compatibility with other outputs; not needed, only "RGB" is allowed
        :param size: (width, height) of the canvas, in pixels
        """
        super().__init__(outfile, colorsys, size)
        self.filename = path.splitext(outfile)[0] + '.svg' if outfile is not None else None
        if colorsys != "RGB":
            raise ValueError(f"Colorspace '{colorsys}' is not supported with svg output.")
        self.can = svg.SVG()
        self.can.elements = []
        self.elements = self.can.elements
        self.can.viewBox = [0, 0, *size]
        self.clipstart = None
        self.clip_eid = None
        self.metadata = Metadata()
        self.css_classes = dict()
        self.use_css = use_css

    def rep_color(self, color, default=None, dark_mode=False):
        """
        The representation of the colour for svg files: RGB in 0-255 (here as hex) and A in 0-1
        :param color: a colour name or tuple
        :param default:
        :param dark_mode: whether to adapt the color to a dark background
        :return: a tuple = (str: colour that can be used in a svg file, float: alpha)
                Note: this may appear untidy but since it is mostly used through apply_color,
                      the tuple is a simple and easy way to provide the desired output.
        """
        if color == "inherit":
            return None, None
        if color is None:
            return "none", 1  # for SVG stroke or fill, "none" means don't have it
        usecolor = super().rep_color(color, default)  # Standard processing is done first
        if not usecolor:
            return "none", 1

        if not isinstance(usecolor, canvas_base.Color):
            raise TypeError(f"Unknown color data type or value: {usecolor}.")

        if usecolor.colorsystem() != "RGB":
            raise ValueError(f"Colorspace '{usecolor.colorsystem()}' is not supported with svg output.")

        # NOTE: For SVGs, it seems that some software(s) interpret colours with 4 values as CMYK instead of RBGA.
        #   Therefore, we return alpha separately.
        alpha = usecolor[3] if usecolor[3] < 1.0 else None

        def nli(x, f):
            return np.exp(np.log(x + 1E-10) * (1.0 - f))

        if dark_mode:
            # apply luminosity and saturation changes
            hh, ll, ss = colorsys.rgb_to_hls(*usecolor[:3])
            if ss > 0.01:  # coloured: increase lightness and saturation for more visibility against black
                light = 0.4
                sat = 0.5
                rgbcolor = colorsys.hls_to_rgb(hh, nli(ll, light), nli(ss, sat))
            else:  # grey level: roughly invert luminosity (black <-> white)
                rgbcolor = colorsys.hls_to_rgb(hh, nli(1.0 - ll, 0.45), ss)
        else:
            rgbcolor = usecolor[:3]

        return f'rgb({",".join([str(round(col * 255)) for col in rgbcolor])})', alpha

    def apply_color(self, stroke: str | None = "inherit", fill: str | None = "inherit", classes: iter = None):
        """
        Provides arguments to apply color to an element by either setting stroke and fill or a class name.
        The latter approach allows for css-based alternate colourings such as a dark mode.
        :param stroke: stroke color (or None for no stroke, or inherit to ignore stroke = take from parent)
        :param fill: fill color (...as for stroke)
        :param classes: optional css class names for other purposes; these will be included in the class_ parameter
        """
        attribs = dict()
        if self.use_css:
            classes = classes if classes else []
            if stroke is None:
                attribs["stroke"] = "none"
            elif stroke != "inherit":
                cls = f"s_{stroke}"
                classes.append(cls)
                self.css_classes[cls] = ("stroke", stroke)
            if fill is None:
                attribs["fill"] = "none"
            elif fill != "inherit":
                cls = f"f_{fill}"
                classes.append(cls)
                self.css_classes[cls] = ("fill", fill)
        else:
            if stroke != "inherit":
                attribs["stroke"], attribs["stroke_opacity"] = self.rep_color(stroke)
            if fill != "inherit":
                attribs["fill"], attribs["fill_opacity"] = self.rep_color(fill)
        if classes:
            attribs["class_"] = " ".join(classes)
        return attribs

    def set_page_size(self, size):
        self.can.viewBox = svg.ViewBoxSpec(0, 0, *size)

    def line(self, x1, y1, x2, y2, stroke=None, stroke_width=None, dash=None, markers=None, eid=None):
        super().line(x1, y1, x2, y2, stroke, stroke_width, dash, markers, eid)
        self.elements.append(svg.Line(
            x1=x1, x2=x2,
            y1=self.can.viewBox.height - y1, y2=self.can.viewBox.height - y2,
            stroke_width=stroke_width if stroke_width else self.stroke_width.default,
            stroke_dasharray=dash,
            **self.apply_color(stroke=stroke if stroke else "black")
        ))

    def polyline(self, points: list, stroke="inherit", stroke_width=None, fill=None,
                 dash=None, markers=None, eid=None):
        # Note: default filling is no filling at all ('none'), while the default stroke is 'not set' = inherit.
        super().polyline(points, stroke, stroke_width, dash, markers, eid)
        tps = [anum for pt in points for anum in (pt[0], self.can.viewBox.height - pt[1])]
        # ^^^ SVG wants list of numbers, no points
        self.elements.append(svg.Polyline(
            points=tps,
            **self.apply_color(stroke=stroke, fill=fill),
            stroke_width=stroke_width if stroke_width is not None else self.stroke_width.default,
            stroke_dasharray=dash,
        ))

    def rect(self, x, y, width, height, fill=None, stroke="inherit", stroke_width=None,
             dash=None, eid=None, tooltip=None, tooltip_dy=None, corner_radius=None):
        # Note: default filling is no filling at all ('none'), while the default stroke is 'not set' = inherit.
        self.elements.append(ToolTippedRect(
            x=x, y=self.can.viewBox.height - y - height,
            rx=corner_radius,
            width=width, height=height,
            **self.apply_color(stroke=stroke, fill=fill,
                               classes=["hastooltip"] if tooltip else None),
            stroke_width=stroke_width if stroke_width else self.stroke_width.default,
            stroke_dasharray=dash,
            data_tooltip=re.sub(r"<(.*?)>", r"&lt;\1&gt;", tooltip).replace("\n", " ") if tooltip else None,
            # ^^^ Todo: check escaping!
            data_tooltip_dy=tooltip_dy,  # Tooltip_dy is a basis to define the distance between the object and tooltip
            id=eid
        ))

    def circle(self, x, y, rad, fill=None, stroke=None):
        self.elements.append(svg.Circle(
            cx=x, cy=self.can.viewBox.height - y,
            r=rad,
            **self.apply_color(stroke=stroke if stroke else "black", fill=fill),
            stroke_width=self.stroke_width.default
        ))

    def lin_gradient_rect(self, cliprect: tuple, gradaxis: tuple, colorlevels: list, plotlevels: list, eid=None):
        """
        Draws a rectangle filled with a linear gradient
        :param cliprect:
        :param gradaxis: a tuple defining the axis on which the gradient's stops are defined, as (x0, y0, x1, y1)
        :param colorlevels:
        :param plotlevels:
        :param eid: element id
        :return:
        """
        # We absolutely need an id for this kind of stuf, so get one (id will not change if already available):
        eid = getid(eid)

        # Define the stops (color, fractional position pairs)
        stops = []
        for col, pos in zip(colorlevels, plotlevels):
            stops.append(
                svg.Stop(offset=pos, stop_color=self.rep_color(col)[0])
            )

        # Define the gradient
        grad_eid = f"Gradient-{eid}"
        self.elements.append(svg.LinearGradient(
            gradientUnits="userSpaceOnUse",
            x1=gradaxis[0],
            y1=self.can.viewBox.height - gradaxis[1],
            x2=gradaxis[2],
            y2=self.can.viewBox.height - gradaxis[3],
            elements=stops,
            id=grad_eid
        ))

        # Add the gradient to the canvas's elements.
        self.elements.append(svg.Rect(
            x=cliprect[0], y=self.can.viewBox.height - cliprect[1] - cliprect[3],
            width=cliprect[2], height=cliprect[3],
            fill=f"url(#{grad_eid})",
            stroke="none",
            id=eid
        ))

    def string(self, xx, yy, text, align='left', font=None, scale=1.0, color="black", altcolor="grey", eid=None):
        """
        Draws text with interpretation of
            '^' and '_' as symbols -> next character is a superscript (e.g. m^2) or subscript (CO_2).
            '~' next symbols should be colored according to 'altcolor'

        :param xx: x position
        :param yy: y position
        :param text: a string to draw on the canvas
        :param align: if set to 'right', behaves like drawRightString;
                      if set to 'center', behaves like drawCentredString; by default, aligns to the left
        :param scale: scales the text horizontally; scale < 1.0 produces condensed text.
        :param font: tuple (font name, font size)
        :param color: font color
        :param altcolor: an alternative font color, for use with characters or symbols prefixed with ~
        :param eid: element id
        :return: experimental: length
        """
        font = defaultfont(font)
        smallfont = font[1] * 0.7  # Font for the sub/superscripts
        # Do not allow html tags
        text = detag(text)
        # Split the string for processing any sub/superscript, keeping the _ or ^ for the next steps
        splitexp = text.replace('^', '¶^').replace('_', '¶_').replace('~', '¶~').split('¶')
        # Add tags for sub/superscripts, if needed
        otext = splitexp[0]
        if len(splitexp) > 1:
            for splitpart in splitexp[1:]:
                if splitpart[0] == '^':
                    otext += f'<tspan baseline-shift="super" font-size="{smallfont}">{splitpart[1]}</tspan>'
                elif splitpart[0] == '_':
                    otext += f'<tspan baseline-shift="sub" font-size="{smallfont}">{splitpart[1]}</tspan>'
                else:
                    otext += f'<tspan fill="{self.rep_color(altcolor)[0]}">{splitpart[1]}</tspan>'
                if len(splitpart) > 1:
                    otext += splitpart[2:]

        text_anchor = {"left": "start", "center": "middle", "right": "end"}[align]
        self.elements.append(svg.Text(
            x=xx, y=self.can.viewBox.height - yy,
            **self.apply_color(stroke=None, fill=color),
            text=otext,
            text_anchor=text_anchor,
            font_size=float(font[1]),
            font_family=font[0],
            textLength=f"{100 * scale}%" if scale and scale != 1.0 else None,
            pointer_events='none',  # This prevents text from interfering with areas used for tooltips (when on top)
            id=eid
        ))
        return stringwidth(text)

    def paragraph(self, xx, yy, text, width=5 * cm, align='left', valign='bottom', rotate=0,
                  font=None, scale=1.0, color="black", breakwords=True, eid=None, nicewrap=False):
        """
        Draws a paragraph within a box of max width = length, with interpretation of '^' and '_' as symbols
        to indicate that the next character is a superscript (e.g. m^2) or subscript (CO_2).

        :param xx: x position
        :param yy: y position
        :param text: a string to draw on the canvas
        :param width: the length of a box in which the paragraph will be placed
        :param align: if set to 'right', behaves like drawRightString;
                      if set to 'center', behaves like drawCentredString; by default, aligns to the left
        :param valign: vertical alignment
        :param rotate: rotation angle
        :param font: tuple (font name, font size)
        :param scale: scales the text horizontally; scale < 1.0 produces condensed text.
        :param color: font color
        :param breakwords: whether words can be broken at end of line
        :param eid: element id
        :param nicewrap: whether to try 'balancing' text across lines to avoid isolated words. Use for long strings only
        """
        font = defaultfont(font)
        normsize = float(font[1])
        text = detag(text)  # Eliminate potential tags
        lines = textwrapsub(text, width, normsize, font[0], breakwords, subsuper, nicewrap=nicewrap)

        # Construct the paragraph: create a <tspan> for each line, with line spacing (dy)
        textelems = []
        linespacing = normsize * 1.1
        for line in lines:
            textelems.append(svg.TSpan(
                x=xx,
                dy=linespacing,
                text=line[0],
                textLength=float(min(line[1], width)),
                lengthAdjust="spacingAndGlyphs"
            ))

        # Paragraph alignment
        xtrans, ytrans = super()._paralign(lines, linespacing, rotate, valign)

        text_anchor = dict(left="start", center="middle", right="end")[align]

        # Define optional rotation
        if not rotate:
            transform = None
        else:  # Rotation has a center at the origin of the text object => rotates around it
            transform = svg.Rotate(a=-rotate, x=xx, y=self.can.viewBox.height - yy)

        self.elements.append(svg.Text(
            x=xx - xtrans, y=self.can.viewBox.height - yy - ytrans,
            **self.apply_color(stroke=None, fill=color),
            elements=textelems,
            text_anchor=text_anchor,
            font_size=normsize,
            font_family=font[0] if font[0] else "Helvetica",
            transform=transform,
            id=eid
        ))
        return len(lines) * linespacing

    def clip(self, rect, eid=None):
        if rect is None and self.clipstart is not None and self.clipstart < len(self.elements):
            for el in self.elements[self.clipstart:]:
                el.clip_path = f"url(#{self.clip_eid})"
            self.clipstart = None
        else:
            # We need an id for this kind of stuf (eid will not change if already available):
            eid = getid(eid)
            # Define the clipPath
            self.clip_eid = f"Clip-{eid}"
            self.elements.append(svg.ClipPath(
                elements=[svg.Rect(x=rect[0], y=self.can.viewBox.height - rect[1] - rect[3],
                                   width=rect[2], height=rect[3])],
                id=self.clip_eid
            ))
            self.clipstart = len(self.elements)

    def set_creator(self, creator):
        self.metadata["creator"] = creator

    def set_title(self, title):
        self.metadata["title"] = title

    def set_subject(self, subject):
        self.metadata["subject"] = subject

    def set_identifier(self, identifier):
        self.metadata["identifier"] = identifier

    def set_keywords(self, keywords):
        self.metadata["description"] = "; ".join(keywords)

    @staticmethod
    def css_rule(cls: str, defs: dict):
        """
        Returns a css rule based on the provided class (to be used as selector) and definitions
        """
        return f".{cls}" + " {" + "; ".join((f"{df}: {defs[df]}" for df in defs)) + "} "

    def set_css(self):
        css_rules = list()
        css_rules_dark = list()
        for cls in self.css_classes:
            attr, color = self.css_classes[cls]

            rcol = self.rep_color(color)
            defs = {attr: rcol[0]}
            if rcol[1] is not None:  # if opacity is defined
                defs[f"{attr}-opacity"] = rcol[1]
            css_rules.append(self.css_rule(cls, defs))

            if color == "black":
                rcol = self.rep_color("vlgrey")  # For Embers, inverted black needs to be visible even on white...
            else:
                rcol = self.rep_color(color, dark_mode=True)
            defs = {attr: rcol[0]}
            r1 = rcol[1]
            if rcol[1] is not None:  # if opacity is defined
                defs[f"{attr}-opacity"] = 0 if rcol[1] == 0 else rcol[1] * 0.85 + 0.15
            css_rules_dark.append(self.css_rule(cls, defs))

        # The selector .show is used to "reveal" boxes surrounding 'reactive' areas (tooltip-like, showing descriptions)
        css_rules.append(self.css_rule("show", {"stroke-opacity": 0.8}))
        if self.use_css:
            css_rules_dark.append(self.css_rule("show", {"stroke": "white", "stroke-opacity": 0.8}))

        css_text = ' '.join(css_rules)
        if self.use_css:
            # Note: rules within .dark and @media are repetitive but it is the only way to provide both functionalities.
            css_text += ("".join(f" .dark {rl}" for rl in css_rules_dark)
                         + f"@media (prefers-color-scheme: dark) {{{' '.join(css_rules_dark)}}}")
        else:
            self.can.style = "stroke: black; fill: black;"  # Not sure that this is still useful
        self.elements.insert(0, svg.Style(text=f"<![CDATA[{css_text}]]>", type="text/css"))

    def save(self):
        self.set_css()
        self.elements.append(svg.Metadata(text=str(self.metadata)))
        if self.filename is not None:
            with open(self.filename, mode='w', encoding='utf8') as ofile:
                ofile.write(str(self.can))
            return self.filename
        else:
            return StringIO(str(self.can))


class Metadata:
    """
    Preliminary metadata for SVGs
    Note: keys should follow the "Dublin Core™ Metadata Initiative" terms.
    https://purl.org/dc/elements/1.1/
    However, these terms may not be the same as for PDFs, hence their use here may be somewhat odd
    (e.g. the description appears to contain what could possibly be associated to the 'valid' key)
    The result was validated on https://www.w3.org/RDF/Validator/rdfval
    """

    def __init__(self):
        self.elements = {}

    def __setitem__(self, key, value):
        self.elements[key] = value.replace('\n', ' ').replace('"', "'").replace('&', '&amp;')

    def __getitem__(self, item):
        return self.elements[item]

    def __repr__(self):
        description = ""
        for key in self.elements:
            description += f'<dc:{key}>{self.elements[key]}</dc:{key}> '
        meta_rdf = f'<rdf:Description rdf:about="">{description}</rdf:Description>'
        meta_inkscape = f'<cc:Work rdf:about="">{description}</cc:Work>'
        return ('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" ' +
                'xmlns:dc="http://purl.org/dc/elements/1.1/" ' +
                'xmlns:cc="http://creativecommons.org/ns#" >' +
                meta_rdf + meta_inkscape +
                '</rdf:RDF>')
