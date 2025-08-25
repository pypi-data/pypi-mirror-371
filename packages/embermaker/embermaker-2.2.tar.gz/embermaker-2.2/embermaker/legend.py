# -*- coding: utf-8 -*-
"""
This module provide legends for the risk levels and for the confidence levels.
The functions (drawlegend()...) are used directly when the legends are in the right or bottom "margins" of the graph,
    the LegendBox class is only used when the legend is drawn as a block/group within the graph.
The first version of this module was created in 9/2023 from earlier code;
it works, but would benefit from improvement that would increase the consistency, especially wrt how the
'bounding box' of elements is defined and how the legend is drawn
(including by defining layout variables used at both stages, such as for vertical / horizontal legend blocs).
"""
import numpy as np
from embermaker.helpers import norm
from embermaker.drawinglib.helpers import cm, mm
from embermaker.ember import drawlinear
from embermaker.graphbase import Element, CanPos, cbyinterp


def drawlegend(egr, x0, y0, x, y, ishoriz=None):
    """
    Draws a legend (colour bar)
    """
    c = egr.c
    gp = egr.gp

    # horizontal or vertical type
    ishoriz = x > y if ishoriz is None else ishoriz

    # pseudo-ember used as legend
    # - - - - - - - - - - - - - -
    rlevels = egr.cpal.cdefs[0]
    # include each level twice to have color transition + uniform area:
    plotlevels = np.arange(len(rlevels) * 2, dtype=float)
    plotlevels = plotlevels / plotlevels[-1]  # normalize
    colorlevels = np.repeat(rlevels, 2)
    colorlevels = [cbyinterp(clev, egr.cpal) for clev in colorlevels]

    # Actual size of the legend area
    if ishoriz:
        ltot_y = gp['leg_bot_y'] + gp['leg_y'] + gp['leg_top_y']
        # Allow the text to extend up to 10% beyond the ember on each side when horizontal (not used for vertical)
        ltot_x = gp['leg_x']
    else:
        ltot_x = min(16 * gp('fnt_size'), x * 0.9)
        ltot_y = gp['leg_x']
    ltot_xtext = ltot_x * 0.2

    #  Position of the legend's burning ember (basis for the entire legend), in canvas coordinates:
    lmid_x = x0 + x / 2.0
    lmid_y = y0 + y / 2.0
    if ishoriz:
        # 1/2 expected width of confidence leg:
        conx = (gp('leg_pos') == "under" and gp['leg_conf'] is True) * 5 * gp['fnt_size']
        xmin = lmid_x - ltot_x / 2.0 - conx
        xmax = lmid_x + ltot_x / 2.0 - conx
        ymin = lmid_y - ltot_y / 2.0 + gp['leg_bot_y']
        ymax = ymin + gp['leg_y']
    else:  # vertical legend
        cony = ((gp('leg_pos') == "right" and gp['leg_conf'] is True) * 3 - 1) * gp['fnt_size']
        xmin = x0 + 0.1 * x
        xmax = xmin + gp['leg_y']
        ymin = lmid_y - ltot_y / 2.0 + cony
        ymax = lmid_y + ltot_y / 2.0 + cony

    # Draw the 'ember' (for a legend, all y ranges are identical : axis, ember, and valid range):
    drawlinear(egr, xmin, xmax, ymin, ymax, ymin, ymax, ymin, ymax, plotlevels, colorlevels)

    # Draw the text of the legend and connect text to colors with lines
    # -----------------------------------------------------------------
    # Styling parameters for this section:
    c.set_stroke_width(0.5 * mm)
    font_risk = (None, min(gp['fnt_size'], (55.0 / len(rlevels))))  # font family to None = default

    # Position of the lines (link between ember and risk level) relative to the 'ember'(halfway in the solid colors)
    xlines = (plotlevels[1::2] + plotlevels[:-1:2]) / 2.0 * egr.gp['leg_x']
    xwidth = (xlines[1] - xlines[0])*1.07
    # Draw the lines, name of risk levels, and title of legend
    if ishoriz:  # Horizontal ember (legend at bottom)
        for i, xline in enumerate(xlines):
            xb = xmin + xline
            yb = ymin - gp['leg_bot_y'] * 0.4
            c.line(xb, yb, xmin + xline, (ymin + ymax) / 2.0)
            risk_level = egr.cpal.risk_levels[i]
            c.paragraph(xmin + xline, ymin - gp['leg_bot_y'] * 0.4, risk_level["display_name"], align="center",
                        valign="top", font=font_risk, width=xwidth, breakwords=False)
            risk_def = risk_level["definition"]
            if risk_def:
                c.rect(xb-30, yb-14, 60, 54,
                       stroke="transparent", fill="transparent", stroke_width=2,
                       tooltip=risk_def, tooltip_dy=20, corner_radius=3)
        if gp['leg_title']:
            width = ltot_x + ltot_xtext
            c.paragraph(xmin - ltot_xtext / 2.0 + width / 2.0, ymax + gp['leg_top_y'] * 0.3,
                        gp['leg_title'], width=width, align="center", font=(None, gp['fnt_size']), breakwords=False)
    else:  # Vertical ember
        for i, xline in enumerate(xlines):
            xb = (xmin + xmax) / 2.0
            yb = ymin + xline
            c.line(xb, yb, xmax + gp['leg_bot_y'] * 0.5, ymin + xline)
            risk_level = egr.cpal.risk_levels[i]
            c.string(xmax + gp['leg_bot_y'] * 0.6, ymin + xline - 1 * mm, risk_level["display_name"])
            risk_def = risk_level["definition"]
            if risk_def:
                c.rect(xb - 20, yb - 15, 120, 30,
                       stroke="transparent", fill="transparent", stroke_width=2,
                       tooltip=risk_def, tooltip_dy=20, corner_radius=3)

        if gp['leg_title']:
            c.paragraph(xmin, ymax + gp['leg_x'] * 0.05, gp['leg_title'], width=ltot_x, align="left",
                        breakwords=False, font=(None, gp['fnt_size']))

    c.set_stroke_width(0.35 * mm)

    # Draw the legend for the confidence level marks. Placement is an issue that could be handled more broadly.
    if gp['leg_conf']:
        match norm(gp['leg_pos']):
            case 'under':
                drawconflegend(egr, xmax + 0.05 * ltot_x + 0.5 * cm, ymax + gp['leg_top_y'] * 0.85, vertical=False)
            case 'right':
                drawconflegend(egr, xmin, ymin - 0.5 * cm)
            case 'in-grid-horizontal':
                drawconflegend(egr, xmin, ymin - 1.2 * cm, vertical=False)
            case 'in-grid-vertical':
                drawconflegend(egr, xmax + 0.6 * ltot_x, ymax - 0.3 * ltot_y)


def drawconflegend(egr, xmin, ymin, vertical=True):
    """
    Draws a legend for the confidence level marks (e.g. * = low confidence).
    Use of this legend is currently limited in terms of layout. Improving the layout would require changes in
    EmberGraph.drawlegend(). To facilitate this, it might be useful to allow drawconflegend to run without drawing,
    only return the width/height of the area needed for drawing.

    For future dev: entirely revise positioning here and in drawlegend.

    :param egr:
    :param xmin:
    :param ymin:
    :param vertical: whether the legend for the risk is vertical or horizontal
    :return: the length of the confidence level's legend, on the horizontal axis
    """
    confidence = egr.cpal.confidence
    conf_levels = confidence["levels"]
    conf_levels_names = [lev["name"] for lev in conf_levels]
    cfnames = egr.gp.lst('conf_levels_file')
    cfsymbs = egr.gp.lst('conf_levels_graph')
    tfsize = egr.gp['fnt_size']
    sfsize = tfsize * egr.gp['conf_levels_graph']
    padding = tfsize * 0.6  # space around the legend's text
    xp = xmin + padding * (not vertical)  # Start of the text
    yp = ymin - egr.gp['leg_top_y'] * 0.42  # Temporary solution: **all lengths should be revised here + in drawlegend**
    xslen = 3.0 * tfsize  # Width of the column of conf symbols
    yslin = 1.25 * tfsize  # Height of a line
    egr.c.string(xp, yp, confidence["title"], font=('Helvetica', tfsize))
    yp -= yslin * 0.2  # larger space under the title
    xlen = 0
    for cfsymb, cfname in zip(cfsymbs, cfnames):
        cfname = cfname.lower()
        if cfname in conf_levels_names:
            cfname_disp = conf_levels[conf_levels_names.index(cfname)]["display_name"]
            yp -= yslin
            egr.c.string(xp, yp - (sfsize-tfsize)/3.0, cfsymb, font=('Helvetica', sfsize))
            namelen = egr.c.string(xp + xslen, yp, cfname_disp, font=('Helvetica', tfsize))
            xlen = max(xlen, namelen)

    egr.c.rect(xp-5, yp-5, xlen + xslen + padding * 2.0, 80,
               stroke="transparent", fill="transparent", stroke_width=2,
               tooltip=confidence["explanation"], tooltip_dy=20, corner_radius=3)

    xlen = xlen + xslen + 2.0 * padding
    return xlen


class LegendBox(Element):
    """
    The LegendBox class is only used when the legend is drawn as a block/group within the graph.
    """
    parent_type = "GraphLine"

    def __init__(self):
        super().__init__()
        self.name = "Embers legend"

    def attach(self, egr=None):
        super().attach(egr)

    def set_cx(self, base_x):
        if "horizontal" in self.egr.gp["leg_pos"]:
            size_x = 1.2 * self.egr.gp["leg_x"]
        else:
            size_x = self.egr.gp["leg_x"]  # Not consistent with how it is defined in `drawlegend` !  <=== TODO
        self.cx = CanPos(base_x, 0, size_x, 0)
        return self.cx.b1  # Right end of this element => left of the following one

    def draw(self):
        egr = self.egr
        drawlegend(egr, self.cx.b0, self.cy.c0, self.cx.b, self.cy.c, ishoriz="horizontal" in egr.gp["leg_pos"])
