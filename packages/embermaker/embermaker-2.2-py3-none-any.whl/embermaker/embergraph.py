# -*- coding: utf-8 -*-
"""
EmberGraphs stores the general information on a graphic containing embers.
"""
import numpy as np
from embermaker import helpers as hlp
from embermaker.helpers import norm, isempty
from embermaker.drawinglib import canvas
from embermaker.drawinglib.helpers import mm
from embermaker.graphbase import Element, CanPos, Axis, draw_vaxis
from embermaker.legend import LegendBox, drawlegend
from embermaker import __version__
import embermaker.parameters as param
from embermaker.ember import Ember
from embermaker.ember import getgroups
from os import path
import json


class EmberGraph(Element):
    """
    EmberGraphs stores the general information on a graphic containing embers,
    and provides methods for drawing such graphs (except for the embers themselves, which are dealt with
    in the Ember class)
    We have included the creation of the drawing canvas here because we want to perfom some intialisation
    before the main program can access the canvas. This sets the colour space to RGB or CMYK once and for all.
    """

    def __init__(self, outfile=None, cpal=None, gp=None, size=(1, 1), circular=False, grformat="PDF", logger=None):
        """
        :param outfile: the intended outfile path; defaults to None: use the graph for calculations, without drawing.
        :param cpal: a dict defining a color palette
        :param gp: a dict of graphic parameters
        :param circular: draws a 'circular' version of the embers; the distance to the center represents 'hazard',
                         and the coulor gradients remain identical to what they are in the 'straight ember' version;
                         this differs from a polar diagram, in which distance to the center may represent risk.
                         Circular diagrams remained at alpha dev. stage and are no longer functional (2024).
        :param grformat:
        :param logger:
        """
        super().__init__()
        self.logger = hlp.Logger() if logger is None else logger

        self.gp = gp if gp else param.ParamDict()  # Default graph parameters
        if cpal:
            self.cpal = cpal
        else:
            colfile = path.join(path.dirname(hlp.__file__), "defaults/colors.xlsx")
            self.cpal = ColourPalette(colfile, prefcsys="RGB", cpalname="", language=self.gp["language"])
        self.csys = cpal.csys if cpal else "RGB"

        self.circular = circular
        self.glen = 10  # Default number of embers in the current group; needed for circular diagrams.

        # Define the drawing canvas
        self.c = canvas.get_canvas(outfile, colorsys=self.csys, size=size, grformat=grformat)  # drawing canvas
        self.colors = self.c.colors
        self.meta = dict()

        # fixed graphic parameters
        self.txspace = min(0.05 * self.gp['scale_x'], 1*mm)  # Spacing between tick or grid line and text
        self.lxticks = min(0.1 * self.gp['scale_x'], 2*mm)   # Length of ticks

    def isdefined(self, gpname):
        """
        Returns True if gp (Graphical Parameter) gpname is defined AND is not empty (not an empty list, etc.)
        In particulars, returns False if the gp is a blank string (' '), but True for any number, including 0.
        :param gpname: the name of the gp to check.
        :return:
        """
        if gpname not in self.gp:
            return False
        else:
            return not isempty(self.gp[gpname])

    def hx1to2(self, haz1):
        """
        Experimental service fct for the secondary axis, TBD
        :param haz1:
        :return:
        """
        return self.gp['haz_axis2_factor'] * haz1 + self.gp['haz_axis2_shift']

    def hx2to1(self, haz2):
        """
        Experimental service fct for the secondary axis, TBD
        :param haz2:
        :return:
        """
        return (haz2 - self.gp['haz_axis2_shift']) / self.gp['haz_axis2_factor']

    def add(self, cel):
        """
        Add elements (= groups or xy-plots) to the embergraph (= egr, the root graph element).
        Elements are not directly added to egr: lines of elements are created, then elements are added to them.
        If embers are provided, these are automatically included in a new group, which is added.
        :param cel: a graph element (at this level, a group or plot) or list of graph elements.
        :return:
        """
        gp = self.gp
        if cel is None or cel == []:
            self.logger.addwarn("Received an empty object to add to the graph.")
            return

        if gp["max_gr_line"] < 1:
            raise Exception("max_gr_line must be > 0, as it is the max number of groups per line")

        if type(cel) is not list:  # Simplify the processing below by getting a list in all cases (even if one element)
            cel = [cel]
        if type(cel[0]) is Ember:  # Simplify usage by creating groups automatically if that is not done yet
            cel = getgroups(cel)

        iel: int = 0  # number of the first element that will be inserted now, within the list of received elements
        nuli = 1  # Number of the line within this graph
        gline = None  # The last graph line, up to now
        nf = 0
        while iel < len(cel):
            if len(self.elements) > 0:
                # There is at least one graphline; get the number 'free seats' in it
                gline = self.elements[-1]
                nf = gline.numfree()
            if nf < 1:
                # No graphline or no free seats => create a new graphline
                grl = GraphLine(max_gr_line=gp["max_gr_line"], name=f"Line #{nuli}")
                nuli += 1
                self.elements.append(grl)
                continue
            gline.add(cel[iel: iel+nf])
            iel += nf

    def set_metadata(self, **kwargs):
        """
        Sets some additional metadata; this is limited because PDFs are produced with ReportLab, which appears to limit
        metadata to a subset of what PDFs could theoretically contain (reading software may share this limitation).
        Use with care, this may be subject to change. Standard metadata are internally defined.
        As of 2025/08, this only allows the "identifier" key, ideally following http://purl.org/dc/terms/identifier
        :param key: the name of the metadata
        :param value: the value of the metadata
        """
        self.meta = kwargs

    def attach(self, egr=None):
        """
        All 'attach' methods 'propagate' the reference to egr to child elements (see graphbase.Element).
        In addition, when relevant,
        - bounding boxes and coordinates (graphbase.Coord) are defined for the element
        - some switches about the presence of axes, etc. may be defined to affect placement and drawing consistently
        The actions on coordinates & switches *possibly* move to specific methods, like set_cy, in the future.
        :param egr:
        :return:
        """
        super().attach()
        gp = self.gp
        mar_x1 = 0
        mar_x2 = 0
        mar_y1 = 0

        # Position the legend
        # The ember groups form a "grid". The legend can be
        # - centered at the right of the entire grid (leg_pos = right), and vertical
        # - centered under the entire grid (leg_pos = under), and horizontal
        # - inside the grid, as an additional ember group (leg_pos = in-grid-horizontal or in-grid-vertical)
        #   => this last case is delegated to the GraphLine, as it is part of it (as a "group")
        if gp('leg_pos') == "under":
            mar_y1 = gp['leg_bot_y'] + gp['leg_y'] + gp['leg_top_y']
        elif norm(gp['leg_pos']) == "right":
            mar_x2 = 16 * gp('fnt_size')  # Might be further improved; see also legend > drawlegend > ltot_x

        # Set the global y-axis if there is none
        if not self.cy.ax:
            self.cy.ax = Axis(bottom=gp['haz_axis_bottom'], top=gp['haz_axis_top'],
                              var_name_std=gp('haz_name_std', default=None), name=gp['haz_name'],
                              var_unit=gp['haz_unit'], minorticks=gp('haz_axis_minorticks', default=None),
                              lines_num=gp['haz_grid_lines'])
            # Define add_lines (user-defined grid lines), if the corresponding parameters are available in gp:
            self.cy.ax.add_lines_from_gp(gp)

        # Set the y-coordinate and bounding box for the lines within this EmberGraph
        cur_y = mar_y1
        max_x = 0
        for li in reversed(self.elements):  # Traverse lines from bottom to top, because bottom is (0,0)
            cur_y = li.set_cy(cur_y)  # Sets the coordinate for this line, and gets cur_y for the next one
            max_x = max(max_x, li.cx.b1)
        max_x += gp["gr_int_x"] / 2.0

        # If the legend is under the graph, take care that it has enough width (for small graphs):
        if gp('leg_pos') == "under":
            add_x = gp['leg_x'] * 1.2 - (mar_x1 + max_x + mar_x2)
            if add_x > 0:
                mar_x2 += add_x/2
                mar_x1 += add_x/2
        else:
            add_x = 0

        self.cx.cp = CanPos(0, mar_x1, max_x, mar_x2)
        self.cy.cp = CanPos(0, mar_y1, cur_y - mar_y1, 0)

        if gp('leg_pos') == "under" and add_x > 0:
            for li in self.elements:
                li.relpos_x(self.cx.c0)

        self.c.set_page_size((self.cx.b1, self.cy.b1))

    def draw(self):
        """
        The top-level draw function
        :return:
        """
        # Attach all graphical elements (in the list of elements) to this EmberGraph before drawing
        self.attach()
        super().draw()

        # Draw legend, if it is placed at the top (EmberGraph) level
        if self.gp('leg_pos') == "right":
            drawlegend(self, self.cx.c1, self.cy.b0, self.cx.m2, self.cy.b)
        elif self.gp('leg_pos') == "under":
            drawlegend(self, self.cx.b0, self.cy.b0, self.cx.b, self.cy.m1)

        # If there were severe errors, 'stamp' the *first* error message on the diagram
        if self.logger.getlog("error"):
            msg = "Critical issue! this diagram may be unreliable. Please investigate. " \
                  + self.logger.getlog("error")[0] + " (...)"
            pp = (2 * mm, self.cy.b1 - 22 * mm)
            self.c.rect(*pp, 72 * mm, 20 * mm, fill="ltransluscent", stroke=None)
            self.c.paragraph(pp[0], pp[1] + 20 * mm, msg, font=("Helvetica", 9),
                             color="red", width=70 * mm, valign="top")

        # Set metadata: keywords = warning messages
        if len(self.logger.getlog("warning")) == 0 and len(self.logger.getlog("error")) == 0:
            self.c.set_keywords(["No warning messages: perfect"])
        else:
            self.c.set_keywords(["Warnings: "] + self.logger.getlog("warning")
                                + [f"Palette: {self.cpal.name}"])

        # Set user-defined metadata
        if self.meta and "identifier" in self.meta:
            self.c.set_identifier(self.meta["identifier"])

        # Set other metadata
        self.c.set_creator(f"EmberMaker {__version__}")
        try:  # Inelegant way to get the group name of the first ember (until improvement of elements and groups?)
            self.c.set_title(self.elements[0].elements[0].elements[0].group[:100])
        except IndexError:
            pass
        outfile = self.c.save()

        return outfile


class GraphLine(Element):
    """
    A line of ember groups and possibly other types of diagrams.
    The graph line sets the y-coordinate for its elements.
    """
    parent_type = "EmberGraph"

    def __init__(self, max_gr_line=100, name=""):
        super().__init__()
        self.name = name
        self.maxgr = int(max_gr_line)

    def add(self, cel):
        super().add(cel)

    def numfree(self) -> int:
        """
        The number of "free seats" in the graphline
        :return: # free seats
        """
        return self.maxgr - len(self.elements)

    def attach(self, egr=None):
        super().attach(egr)
        self.has_axis2_name = egr.gp['haz_axis2'] in ["True", "Right"] and self.has_vaxis

        # Legend, when it is an element in the GraphLine
        # Note: this is only permitted if it makes senses, i.e. there is a graph line that is not entirely filled
        if "in-grid" in egr.gp['leg_pos']:
            if len(self.elements) < egr.gp["max_gr_line"]:
                lbox = LegendBox()
                super().add(lbox)
                lbox.attach(egr)

        # Vertical axis
        # If this line has no vaxis (to draw), then the first group within this line has a vaxis:
        # (this could be done within groups, but we should 'tell' them when they are 'first in line';
        #  as we are dealing with line elements (=groups) below anyway, we kept this code here)
        self.elements[0].has_vaxis = self.elements[0].has_vaxis or not self.has_vaxis
        self.elements[0].has_axis_name = self.elements[0].has_vaxis
        self.elements[-1].has_vaxis2 = (self.elements[-1].has_vaxis2
                                        or (egr.gp['haz_axis2'] in ["True", "Right"] and not self.has_vaxis))
        self.elements[-1].has_axis2_name = self.elements[-1].has_vaxis2

        # x-coordinates and bounding box, including for the elements (groups; y for the line is set by EmberGraph)
        marg1 = self.has_vaxis * (egr.gp["haz_name_x"] + egr.gp["scale_x"])
        cur_x = marg1

        multax = len({el.cy.ax for el in self.elements}) > 1
        isfirst = True
        for el in self.elements:  # Loop over groups in the line
            if isfirst:
                isfirst = False
                el.has_vaxis = True
            else:
                el.has_vaxis = multax
                el.has_axis_name = multax  # may remove has_axis_name if redundant (see Changelog.md)
            cur_x = el.set_cx(cur_x)  # Sets the coordinate for this group, and gets cur_x for the next one

        self.cx.cp = CanPos(0, marg1, cur_x - marg1, 0)

    def set_cy(self, base_y):
        gp = self.egr.gp
        self.cy.cp = CanPos(base_y, self.egr.gp['be_bot_y'], self.egr.gp['be_y'], gp['be_top_y'])
        if not self.cy.ax:
            self.cy.ax = self.egr.cy.ax
        for el in self.elements:
            el.prop_cy(self.cy)  # Propagate to each group a reference to the cy coordinate/box
        return self.cy.b1  # Top of this line => for use as bottom of next line above

    def draw(self):
        # Draw the vertical axis and grid lines, if it applies to the entire line
        if self.has_vaxis or self.has_vgrid:
            draw_vaxis(self)

        super().draw()


class ColourPalette:
    """
    Reads the color palette. Importantly, this also defines the "risk scale" (sequence of risk indexes & colours).
    The palette is defined by:
     - its color system (RGB, CMYK...): csys
     - names of risk levels associated to colors : cnames (see Excel sheet)
     - a risk level index: cdefs[0] (1D numpy array of risk indexes)
     - the color densities for each color corresponding and risk index :
         cdefs[c, r] where c is the colour value (line) and r is the risk (column)
     - the set of transitions that it defines: transnames_risk is a dict linking transition names to risk levels,
         such as {"high to very high": (2, 1)}, which means that this transition extends from risk index 2 to index 2+1
    Note about planned changes:
          in the context of the database, Palettes and risk levels should have a standard definition.
          This code is now very old: a new structure + input file parser is needed.
    """

    def __init__(self, wbcol, prefcsys=None, cpalname=None, cpalinfo=None, logger=None, language=None):
        """
        """
        if logger is None:
            logger = hlp.Logger()
        self.info = cpalinfo

        # Read the usual / old Excel sheet containing the colour palette:
        self.name, self.csys, self.cnames, self.cdefs = self.read_risk_xls(wbcol, cpalname, prefcsys, logger)
        # Read the new standard level definitions + translations:
        riskdefs = self.read_risk_levels(language, logger)

        # Confidence levels
        self.confidence = riskdefs["confidence"]

        # Risk levels (combination of any user provided xlsx ('old format') and internal defaults (translations)
        self.risk_levels = []
        std_levels = riskdefs["levels"]
        std_levels_names = [lev["name"] for lev in std_levels]
        # Note: codes using this currently assume that cnames and risk_levels are ordered and matching each other
        #       (this may no longer be required after refactoring but needs to be preserved for the time being)
        for il, cname in enumerate(self.cnames):
            levname = cname.lower()
            if levname in std_levels_names:
                level = std_levels[std_levels_names.index(levname)]
            else:
                level = {"name": levname, "display_name": levname.capitalize(), "definition": ""}
            level["color"] = self.cdefs[1:, il]
            level["index"] = self.cdefs[0, il]
            self.risk_levels.append(level)

        # Transitions
        # -----------
        # transnames_risk is a dict linking transition names to their (base risk level, risk level change),
        # such as {"high to very high": (2, 1)}, which means that this transition extends from index 2 to index 2+1
        self.transnames_risk = {}
        ridx = self.cdefs[0] if self.cdefs is not None else None
        for ibeg in range(len(self.cnames)-1):
            transname = norm(self.cnames[ibeg]) + " to " + norm(self.cnames[ibeg+1])
            self.transnames_risk[transname] = (ridx[ibeg], ridx[ibeg+1] - ridx[ibeg])

            # Downward risk transitions (including for increasing benefits <0 risk index)
            transname = norm(self.cnames[ibeg+1]) + " to " + norm(self.cnames[ibeg])
            self.transnames_risk[transname] = (ridx[ibeg+1], ridx[ibeg] - ridx[ibeg+1])

    @staticmethod
    def read_risk_xls(wbcol, cpalname, prefcsys, logger):
        """
        Reads an EmberFactory colour palette from an Excel workbook
        Note: this is an old approach; we plan to refactor ColourPalette entirely
        :param wbcol: an Excel workbook from openpyxl, OR the name of such an Excel workbook
        :param prefcsys: a colour system choice from the user, among (RGB, CMYK, *standard);
                        'RGB' or 'CMYK' will use *default* palettes defined below;
                        'standard' means that the user makes no choice in the UI;
    -                    When 'standard' is included, it will go through several steps to get a palette, using
                        1) cpalname if set (this should come from the parameter in the spreadsheet),
                        2) 'ACTIVE-P' if it is set; if is also unavailable,
                        3) revert to the internal default (RGB-SRCCL-C7).
                        ACTIVE-P is a legacy parameter which may be provided in the 'colour' spreadsheet (read here).
                        Note: this is cluttered due to legacy support; ACTIVE-P might be dropped in the future.
        :param cpalname: the name of the desired palette, used only if the color sheet does not set 'ACTIVE-P'
        :param prefcsys:
        :param logger:
        """
        if type(wbcol) is str:
            wbcol = hlp.secure_open_workbook(wbcol)
        read = False
        ctmp = []
        cnames = []
        cref = 1.0  # Reference (max) value of the color range (optional parameter)
        sht = wbcol["Color definitions"]
        # Default palette (if no palette defined in the color sheet or provided as cpalname
        if prefcsys == 'RGB':  # if prefcsys is set to RGB or CMYK, it gets the priority over any parameter
            cpalname = 'RGB-SRCCL-C7'
        elif prefcsys == 'CMYK':
            cpalname = 'CMYK-IPCC'
        elif not cpalname:
            # if prefcsys did not specify a colour system and cpalname is not set,
            # then we set a default here and will overwrite it below if 'ACTIVE-P' is found
            cpalname = 'RGB-SRCCL-C7'
        csys = None
        for row in sht.rows:
            key = hlp.stripped(row[0].value)
            name = hlp.stripped(row[1].value)
            inda = [acell.value for acell in row[2:]]  # input data
            if key == 'ACTIVE-P' and 'standard' in prefcsys:
                cpalname = name  # ACTIVE-P is a legacy parameter
            elif key == 'PALETTE' and cpalname == name:
                logger.addinfo('Will use color palette: ' + cpalname)
                read = True
            elif key == '' or key is None:
                read = False
            elif key == 'HEADERS' and read:
                if inda[1:4] == ['Red', 'Green', 'Blue']:
                    csys = 'RGB'
                elif inda[1:5] == ['Cyan', 'Magenta', 'Yellow', 'Black']:
                    csys = 'CMYK'
                else:
                    raise Exception("Unknown color system (see colors in sheet 'Color definitions').")
            elif key == 'DATA' and read:
                cnames.append(name)
                ctmp.append(inda[:1 + len(csys)])
            elif key == 'REFERENCE' and read:
                # The "reference" is an arbitrary number that is the maximum of colour values, typically 1, 100, or 255.
                # (default value is 1, see above)
                try:
                    cref = float(inda[0])
                except ValueError:
                    raise ValueError("REFERENCE value for the colors is wrong or misplaced "
                                     "(must be 3rd col in palette definition)")
        if len(cnames) < 2:
            raise Exception("Colour palette '{}' could not be found or was incorrectly defined.".format(cpalname))
        cdiv = [1.0] + ([cref] * (len(ctmp[0]) - 1))  # We need to divide each line by the ref, but not element 0
        cdefs = (np.array(ctmp) / cdiv).transpose()  # color definitions array
        del ctmp
        logger.addinfo(f"Palette risk levels and colors: {cdefs}")
        return cpalname, csys, cnames, cdefs

    @staticmethod
    def read_risk_levels(language="en", logger=None, riskdefs_file=None):
        """
        Read risk levels, with information and display names translated to the requested language
        :param language:
        :param logger:
        :param riskdefs_file: path to an external risk definition file, if needed (e.g. for additional languages)
        """
        if riskdefs_file:
            sfile = riskdefs_file
        else:
            sfile = path.join(path.dirname(hlp.__file__), f"defaults/riskdefs_{language}.json")
        try:
            with open(sfile, "r") as file:
                riskdefs = json.load(file)
        except FileNotFoundError:
            logger.addwarn(f"Could not find risk level definitions for language={language}")
            with open(path.join(path.dirname(hlp.__file__), f"defaults/riskdefs_en.json"), "r") as file:
                riskdefs = json.load(file)

        return riskdefs
