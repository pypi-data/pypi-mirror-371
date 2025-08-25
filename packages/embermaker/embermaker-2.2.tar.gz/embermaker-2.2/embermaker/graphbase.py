"""
Base for graph elements in EmberGraphs.
"""
from embermaker import helpers as hlp
from embermaker.drawinglib.helpers import mm
from embermaker.drawinglib.canvas_base import Color
import numpy as np
import sys

gettrace = getattr(sys, 'gettrace', None)


class EmberGraphBadRequest(Exception):
    """Raised when there is a request for anything that EmberMaker cannot do"""


class Axis:
    def __init__(self, name=None, shortname=None, description=None, bottom=0, top=5,
                 var_name_std=None, var_unit=None, minorticks=None, lines_num=5, lines_add: dict = None):
        """
        The properties of an axis: its name, range, etc., and grid lines properties
        :param name: The name of the axis
        :param shortname:
        :param description: The description of the axis (e.g. as obtained from the Embers database / CREE)
        :param bottom:
        :param top:
        :param var_name_std:
        :param var_unit:
        :param minorticks: If not None, include minor ticks. 0 means 'auto define', x means x minor ticks.
        :param lines_num: the preferred number of gris lines (further adjusted by software)
        :param lines_add: a list of custom lines. Each custom line is defined by a dict, using the following keys:
                'line': the hazard level where the line should be drawn (mandatory; all others are optional)
                'shade_end': hazard level for the end of an optional shaded area (between line and shade_end)
                'label': an alternative label for the line (defaults to the 'line' value + var_unit)
                'label_off': an optional offset for the label, along the axis (unit = fraction of font size)
                'color': the color of the line or shaded area (defaults to grey)
        """
        self.name = name
        self.shortname = shortname
        self.description = description
        self.d0 = bottom
        self.d1 = top
        self.d = self.d1 - self.d0
        self.var_name_std = var_name_std
        self.var_unit = var_unit
        self.minorticks = minorticks
        self.lines_num = lines_num
        self.lines_add = lines_add

    def add_lines_from_gp(self, gp):
        """
        Defines "lines_add" on the basis of the corresponding parameters in gp -- an older concept used in EmberFactory;
        lines_add is a list of user-defined grid lines or shaded areas; each line is defined by a dict of parameters
        (see Axis class for details)
        """
        if gp.lst('haz_grid_lines'):
            self.lines_add = []
            for idx, line in enumerate(gp.lst('haz_grid_lines')):
                lines = {"line": line}
                gp_lst_to_dict(gp, lines, "haz_grid_lines_ends", "shade_end", idx)
                gp_lst_to_dict(gp, lines, "haz_grid_lines_labels", "label", idx)
                gp_lst_to_dict(gp, lines, "haz_grid_lines_labels_off", "label_off", idx)
                gp_lst_to_dict(gp, lines, "haz_grid_lines_colors", "color", idx)
                self.lines_add.append(lines)


class CanPos:
    """
    Defines the position of an element on the canvas.
        b0 <m1> c0 <c> c1 <m2> b1 (<m1> and <m2> are margin lengths, <c> is the drawing area length)
        b0         <b>         b1 (b is the length of the bounding box)
    """

    def __init__(self, b0: float, m1: float, c: float, m2: float):
        """
    Defines the position of an element on the canvas.
        b0 <m1> c0 <c> c1 <m2> b1 (<m1> and <m2> are margin lengths, <c> is the drawing area length)
        b0         <b>         b1 (b is the length of the bounding box)
        :param b0: Origin of the (outer) bounding box on the canvas
        :param m1: Lenght of the margin before the inner area, on the canvas (between b0 and c0)
        :param c: Lenght of the plotting area on the canvas (between c0 and c1)
        :param m2: Lenght of the margin after the inner area, on the canvas (between c1 and b1)
        """
        self.b0 = b0
        self.c0 = b0 + m1
        self.c1 = self.c0 + c
        self.b1 = self.c1 + m2
        self.c = c
        self.b = self.b1 - self.b0
        self.m1 = m1
        self.m2 = m2

    def __str__(self):
        return f'CanPos: ({self.b0} [{self.c0}, {self.c1}] {self.b1})'

    def rebase(self, b0):
        """
        Adjusts the absolute position of the coordinate to a new value of the base position b0
        :param b0: the new base position
        """
        self.b0 = b0
        self.c0 = b0 + self.m1
        self.c1 = self.c0 + self.c
        self.b1 = self.c1 + self.m2


class Coord:
    """
        A 1-dimensional "coordinate system":
        provides information on the position of an element on the canvas,
        and conversion methods from data to canvas coordinates and vice-versa.
        Canvas position (cp): b0 <m1> c0 <c> c1 <m2> b1 (<m1> and <m2> are margin lengths, <c> is drawing area length)
                              b0         <b>         b1 (b is the length of the bounding box)
        Data coord. (ax)    : --  --  d0  d  d1  --  --
    Each element as a coord along the x-axis and one along the y-axis.
    Note: to view the bounding boxes of all elements, run in debug mode.
    :param cpos: a CanPos object, providing the position on the canvas.
    :param axis: an Axis object
    :param el: the parent element, for information / error reporting
    """

    def __init__(self, cpos=None, axis=None, el=None):
        self.cp = cpos
        self.ax = axis
        self.el = el

    @property
    def b1(self):
        return self.cp.b1

    @property
    def b0(self):
        return self.cp.b0

    @property
    def b(self):
        return self.cp.b

    @property
    def c0(self):
        return self.cp.c0

    @property
    def c1(self):
        return self.cp.c1

    @property
    def c(self):
        return self.cp.c

    @property
    def m1(self):
        return self.cp.m1

    @property
    def m2(self):
        return self.cp.m2

    @property
    def d0(self):
        if self.ax is None:
            self.noaxis()
        return self.ax.d0

    @property
    def d1(self):
        if self.ax is None:
            self.noaxis()
        return self.ax.d1

    @property
    def d(self):
        if self.ax is None:
            self.noaxis()
        return self.ax.d

    def noaxis(self):
        if self.el:
            dim = 'x' if self.el.cx == self else 'y'
            raise Exception(f"Undefined {dim}-axis for element {self.el}")
        else:
            raise Exception(f"Undefined axis, for unknown element")

    def tocan(self, data):
        """
        Calculates the position in canvas coordinate for a given data value.
        :param data: a value in data coordinate (e.g. hazard or probability)
        :return: the result of the scaling to the canevas coordinates
        """
        return self.c0 + self.c * (data - self.d0) / self.d

    def todata(self, canvalue):
        """
        Inverse of `tocan`. Provides the data coordinate corresponding to a y position on the canvas.
        :param canvalue: a 'physical' position on the y-axis, in canvas coordinates
        :return: the data value (hazard, probability...)
        """
        return ((canvalue - self.c0) * self.d / self.cp.c) + self.d0


class Element:
    """
    Base class for objects in diagrams. It could also be called Node.
    """
    _elementary = False  # By default, an element can be the parent for child elements (e.g. lines in a plot)
    parent_type = None
    __slots__ = ("logger", "type", "has_vaxis", "has_vaxis2", "has_vgrid", "has_vgrid2", "has_axis_name",
                 "has_axis2_name", "egr", "parent", "elements", "name", "cx", "cy")

    def __init__(self):
        self.logger = None
        self.type = type(self).__name__
        # Note: some of these declarations could be restricted to elements which may have an axis (= lines & groups) ?
        self.has_vaxis = False
        self.has_vaxis2 = False
        self.has_vgrid = False
        self.has_vgrid2 = False
        self.has_axis_name = False
        self.has_axis2_name = False
        self.egr = None
        self.parent = None  # There are many cases where simply referring to the parent appears easier.
        self.elements = []
        self.name = None
        self.cx = Coord(el=self)
        self.cy = Coord(el=self)

    def __len__(self):
        return len(self.elements)

    def __str__(self):
        if self.type == "EmberGraph":
            return "EmberGraph (master graphical object, not attached)"
        else:
            isatt = "" if self.egr else "NOT "
            return f'El. {self.type} ({self.name});{isatt} attached'

    def _check_child(self, el):
        if not issubclass(type(el), Element):
            raise EmberGraphBadRequest(f"Objects of type {type(el).__name__} cannot be added to an EmberGraph")
        if el.parent_type != self.type:
            raise EmberGraphBadRequest(f"Graphical object type {type(el).__name__} does not indicate "
                                       f"{self.type} as potential parent")

    def attach(self, egr=None):
        """
        Attaches graph elements to an EmberGraph => combines the data (elements) to the graph parameters (egr.gp)
        :param egr: the embergraph (=root element); defined when the element itself is not the root element.
        :return:
        """
        if egr:  # This (self) is not the root element
            if self.egr:
                raise EmberGraphBadRequest(
                    f"This {type(self).__name__} is already attached to the graph; use deepcopy if needed")
            self.egr = egr
        else:  # This is the root element (hence we do not define self.egr)
            egr = self
        # Attach nested elements to egr
        for el in self.elements:
            el.attach(egr=egr)
            el.parent = self

    def prop_cy(self, cy):
        """
        'Propagates' the y dimension of the coordinate system to child elements
        Note: this differs from set_cy, because set_cy may ask for the CanPos of child elements before setting
        the box/coord information for the requesting object (information flows from nested to parent elements).
        :param cy: the Coord object for the y-axis
        :return:
        """
        self.cy.cp = cy.cp
        if not self.cy.ax or self._elementary:  # If an axis already exist, it is only overwritten for embers and lines
            self.cy.ax = cy.ax
        for el in self.elements:
            el.prop_cy(self.cy)  # Propagate to each group a reference to the cy coordinate/box

    def relpos_x(self, b0=0):
        """
        Moves each x coordinate relatively to a new base position b0.
        This is currently used when the whole graphic needs to be centered after placing ('attaching') its elements.
        It might be a basis for a more separated treatment of size and position (=> more relative positionning).
        :param b0:
        """
        if self.cx:
            self.cx.cp.rebase(b0)
            elb0 = self.cx.c0
            for el in self.elements:
                if el.cx != self.cx:  # if the cx of the child is the same as the parent, it does not define placement
                    el.relpos_x(elb0)
                    elb0 = el.cx.b1

    @property
    def xaxis(self):
        return self.cx.ax

    @property
    def yaxis(self):
        return self.cy.ax

    def set_xaxis(self, *args, **qwargs):
        """Set the x-axis of this element; input parameters are either an Axis or parameters to build an Axis"""
        if args:
            self.cx.ax = args[0]
        elif qwargs:
            self.cx.ax = Axis(**qwargs)
        else:
            raise KeyError("set_xaxis() requires an Axis or the parameters to build an axis")

    def set_yaxis(self, *args, **qwargs):
        """Set the y-axis (hazard) for this element; parameters are either an Axis or parameters to build an Axis"""
        if args:
            self.cy.ax = args[0]
        elif qwargs:
            self.cy.ax = Axis(**qwargs)
        else:
            raise KeyError("set_yaxis() requires an Axis or the parameters to build an axis")

    def add(self, cel):
        """
        Adds one or more (if input is a list) child elements to this Element.
        :param cel: a child element or a list of child elements
        """
        if self._elementary:
            raise EmberGraphBadRequest(
                "Attempt at including elements in a drawing element that cannot host any (is elementary).")
        if type(cel) is list:
            for el in cel:
                self._check_child(el)
            self.elements += cel
        else:
            self._check_child(cel)
            self.elements.append(cel)

    def draw(self):
        """
        Draws the element and calls the draw method of any child element
        """
        for el in self.elements:
            el.draw()
        showboxes(self)


def draw_vaxis(el: Element):
    """
    Plots the (one or two) 'hazard' axis graduation values, tick marks and grid lines
    :param el: the graph element in which the left and/or right axis and/or grid has to be drawn
    """
    egr = el.egr
    cx = el.cx
    cy = el.cy
    ax = cy.ax
    # Set drawing properties (colour of the main horizontal lines)
    egr.c.set_stroke_width(0.35 * mm)

    # Define axis names
    axname = ax.name if el.has_axis_name else None
    ax2name = egr.gp['haz_axis2_name'] if el.has_axis2_name else None

    # Axis unit
    axunit = ax.var_unit if ax.name is None or ax.var_unit not in ax.name else ""  # do not show unit if in axis name

    # Set grid line options
    has_grid = egr.gp('haz_grid_show') == "all" and el.has_vgrid

    # Draw the line along vaxis
    has_vline = not (has_grid and ax.minorticks is None)  # if True, draw the line along vaxis2.
    # Note: drawaxis should be performed AFTER the custom grid-lines. However, this needs moving the call to nicelvels()
    #       outside drawaxis to get "leftlines" -or another solution to prevent overlaps between user and defined labels
    leftlines = drawaxis(egr, cx, cy, axname=axname, axunit=axunit, axside='left', has_vaxis=el.has_vaxis,
                         has_grid=has_grid, has_vline=has_vline, nmticks=ax.minorticks)

    # Draw secondary (right) axis and grid lines
    grid = egr.gp['haz_grid_show'] if hlp.isempty(egr.gp['haz_grid2_show']) else egr.gp['haz_grid2_show']
    has_grid = hlp.norm(grid) == "all" and el.has_vgrid2
    has_vline2 = el.has_vaxis2 and not (has_grid and egr.gp['haz_axis2_minorticks'] is None)
    axunit = egr.gp['haz_axis2_unit'] if egr.gp['haz_axis2_unit'] else egr.gp['haz_unit']
    drawaxis(egr, cx, cy, altaxfct=(egr.hx1to2, egr.hx2to1), has_vaxis=el.has_vaxis2, axname=ax2name,
             axunit=axunit, axside='right', has_grid=has_grid, has_vline=has_vline2,
             nmticks=egr.gp['haz_axis2_minorticks'])

    # Add any user-defined specific grid lines (might be delegated as done with drawaxis above, but more complex)
    llx = cx.c0 - egr.lxticks * has_vline  # left-end of lines or area
    lines_add = cy.ax.lines_add
    if lines_add:
        egr.c.set_stroke_width(0.35 * mm)
        for ic, li in enumerate(lines_add):
            if 'line' not in li:
                egr.logger.addwarn("{el.name}: An axis/grid line is incorrectly defined (missing 'line' key)")
                continue
            glcolor = li.get('color', 'lgrey')
            glhaz = li['line']
            try:
                yp = cy.tocan(float(glhaz))
            except ValueError:
                egr.logger.addwarn("Could not process data for a custom grid line")
                continue
            glend = li.get('shade_end', None)
            if glend:
                # Colored area (between the standard `grid-line` and `grid-line-ends`)
                sy = cy.tocan(glend) - yp
                egr.c.rect(llx, yp, cx.c + egr.lxticks * has_vline, sy,
                           stroke=None, fill=glcolor)
            else:
                # Grid-lines
                sy = 0.0
                egr.c.line(llx, yp, cx.c1, yp, stroke=glcolor)
            if el.has_vaxis:
                # Prepare for drawing label (for colored areas, the text is centered by using sy/2)
                gllabel = li.get('label', str(glhaz) + " " + axunit)
                sby = yp + sy / 2.0
                # Handle custom label offsetting (see documentation about haz_grid_lines_labels_off)
                if 'label_off' in li:
                    oby = sby
                    # Move the label
                    sby += li.get('label_off', 0) * egr.gp['fnt_size']
                    # Draw a small connecting line
                    xp = llx - egr.txspace * 0.8
                    obx = xp + egr.gp['be_int_x'] / 4.0 + egr.gp['fnt_size'] * 0.2
                    yp = sby + egr.gp['fnt_size'] * 0.05
                    egr.c.line(xp, yp, obx, oby, stroke='dgrey', stroke_width=0.3 * mm)
                # Add label
                if float(glhaz) not in leftlines or 'label_off' in li:
                    # Don't add a user defined label if there is already a main label, except if label_off is set
                    egr.c.paragraph(llx - egr.txspace, sby, gllabel, align='right', valign="center", color='dgrey',
                                    font=(None, egr.gp['fnt_size']))

    # Draw vertical axis line if needed (it can't be done before because it needs to be on top)
    if has_vline:
        egr.c.line(cx.c0, cy.c0, cx.c0, cy.c1)
    if has_vline2:
        egr.c.line(cx.c1, cy.c0, cx.c1, cy.c1)

    # if a tooltip is available for the axis, add it
    if ax.description and ax.description.strip():
        egr.c.rect(cx.b0+2, cy.c0-5, cx.m1, cy.c+10,
                   stroke="transparent", fill="transparent", stroke_width=2,
                   tooltip=ax.description.replace('"', '&#8242; ').replace('&', '&#38;'),
                   tooltip_dy=0)


def draw_xaxis(egr, cx, cy, name=None, withvgrid=False, has_vline=True, labels_par=None):
    """
    Horizontal axis drawing, for non-ember diagrams (currently x-y lineplots only)
    label parameters supported in labels_par:
        - rotate: rotates the label by the given angle (in degrees, counter-clockwise) wrt. horizontal (default = 0)
    :param egr:
    :param cx:
    :param cy:
    :param name:
    :param withvgrid:
    :param has_vline: if True, plot vertical lines extending the tick marks
    :param labels_par: a dict providing parameters for the labels
    :return:
    """
    c = egr.c
    labels_par = labels_par if labels_par else {}
    fsize = egr.gp['fnt_size']

    # Axis name
    if name:
        parlen = cx.c
        c.paragraph(cx.c0 + cx.c / 2.0, cy.c0 - egr.gp['be_bot_y'] * 0.8, name, width=parlen,
                    font=(egr.gp['fnt_name'], fsize), align='center')

    # Get nice looking levels for the ticks or lines
    nalevels = cx.ax.lines_num if cx.ax.lines_num else egr.gp['haz_grid_lines']
    glines, labfmt, mticks = hlp.nicelevels(cx.d0, cx.d1,
                                            nalevels=nalevels, enclose=False,
                                            nmticks=cx.ax.minorticks)

    # Define line start, line end, axis levels text position, and draw
    olb = cy.c0  # edge of the drawing area, where a line showing the axis could be drawn
    oll = olb - egr.lxticks * has_vline  # start of lines (= drawing area edge - tick mark)
    txe = oll - egr.txspace  # end of text strings
    orl = cx.c1

    if withvgrid:
        color = 'lgrey'
    else:
        # No grid, just ticks (adapt the length of lines)
        color = 'dgrey'
        orl = olb

    # Axis line
    if has_vline:
        c.line(cx.c0, olb, cx.c1, olb, stroke=color)

    # Main ticks or grid and their labels
    rotate = labels_par["rotate"] if "rotate" in labels_par else 0
    align = "center" if rotate == 0 else "right"
    valign = "top" if rotate == 0 else "center"
    for xv in glines:
        xp = cx.tocan(xv)
        c.line(xp, oll, xp, orl, stroke=color)
        gllabel = f"{xv:.{labfmt}}"
        c.paragraph(xp, txe, gllabel, align=align, valign=valign,
                    font=(None, fsize), rotate=rotate)
    # Minor ticks
    if mticks is not None:
        for xv in mticks:
            xp = cx.tocan(xv)
            c.line(xp, oll, xp, orl, stroke="lgrey")


def drawaxis(egr, cx, cy, altaxfct=None, axname='', axunit='', axside='left',
             nmticks=None, has_vaxis=True, has_grid=True, has_vline=True):
    """
    Generic *vertical* axis-drawing function, handling left and right axis as well as grid lines
    Note: there could be reasons to have the same code for horizontal & vertical, but horizontal axis
          are less complex so the benefit would be limited.
    :param egr: the embergraph
    :param cx: The x-coord object for the element to which v-axis will be added (in the margin)
    :param cy: The y-coord object for the element to which v-axis will be added (in the margin)
    :param altaxfct: if provided, works as 'functions' in matplotlib.axes.Axes.secondary_xaxis;
           must be a 2-tuple of functions which define the transform function and its inverse, that is
           (from the standard axis(1) to the defined axis(2), from the defined axis(2) to the standard(1))
    :param axname: axis name
    :param axunit: axis unit
    :param axside: the side of the drawing area: 'left' or 'right'
    :param nmticks: number of minor tick marks
    :param has_vaxis: if True, provide vaxis labels
    :param has_grid: if True, show the horizontal grid lines
    :param has_vline: if True, take space for the vertical line into account (but it is not drawn here)
    :return: grid line height, in 'hazard' coordinates (info to avoid user-defined duplicates)
    """
    if altaxfct is None:
        def ax1toax2(ax):
            return ax

        def ax2toax1(ax):
            return ax
    else:
        ax1toax2, ax2toax1 = altaxfct

    # Draw the name of the axis
    if axside == 'left':
        xnam = cx.b0 + egr.gp['haz_name_x'] * 0.5
    else:
        xnam = cx.c1 + max(5 * egr.gp['fnt_size'], cx.m2 * 0.7)
        # Somewhat arbitrary, by lack of a global dynamical placement for now (= define all sizes, then place Elements)

    if axname:
        parylen = cy.c + (cy.m1 + cy.m2) * 0.6
        # Warning: the 'reference frame' is rotated -> coordinates work differently
        egr.c.paragraph(xnam, cy.c0 + cy.c / 2.0, axname, width=parylen, nicewrap=True,
                        font=(egr.gp['fnt_name'], egr.gp['fnt_size']), align='center', rotate=90,
                        )

    # Get nice looking levels for the horizontal lines
    nalevels = cy.ax.lines_num if cy.ax.lines_num else egr.gp['haz_grid_lines']
    glines, labfmt, mticks = hlp.nicelevels(ax1toax2(cy.d0), ax1toax2(cy.d1),
                                            nalevels=nalevels, enclose=False, nmticks=nmticks)

    # Define line start, line end, axis levels text position
    olbx = cx.c0  # Left edge of the drawing area, where a line showing the axis could be drawn
    orbx = cx.c1  # Same for the right side
    if axside == 'right':
        ollx = olbx
        orlx = orbx + egr.lxticks * has_vline  # end of lines (= drawing area edge + tick mark)
        tbx = orlx + egr.txspace  # start of text strings
        talign = 'left'
    else:  # Left axis
        ollx = olbx - egr.lxticks * has_vline  # start of lines (= drawing area edge - tick mark)
        tbx = ollx - egr.txspace  # end of text strings
        orlx = orbx
        talign = 'right'

    color = 'lgrey'
    if has_grid:
        if axside == 'right':
            color = 'dgrey'
    else:
        # No grid, just ticks (adapt the length of lines)
        color = 'black'
        if axside == 'right':
            ollx = orbx
        else:
            orlx = olbx

    # Draw the main ticks or grid and their labels
    for haz in glines:
        yp = cy.tocan(ax2toax1(haz))
        egr.c.line(ollx, yp, orlx, yp, stroke=color)
        if has_vaxis:
            gllabel = f"{haz:.{labfmt}} {axunit}"
            egr.c.string(tbx, yp - egr.gp['fnt_size'] * 0.3, gllabel, align=talign,
                         font=(None, egr.gp['fnt_size']))

    # Minor ticks
    if mticks is not None:
        for haz in mticks:
            if axside == 'right':
                ollx = orbx
            else:
                orlx = olbx
            yp = cy.tocan(ax2toax1(haz))
            egr.c.line(ollx, yp, orlx, yp)

    return glines


def cbyinterp(rlev, cpal):
    """
    Provides a color by interpolating between the defined color levels associated to risk levels within embers.

    :param rlev: the risk level for which a color is requested
    :param cpal: the "colour palette" for the Ember diagrams; it contains
        csys: the name of the color system (currently CMYK or RGB)
        defs: the definition of the colors associated to risk levels, such that
         - cdefs[0] : a risk level index (1D numpy array of risk indexes)
         - cdefs[1:]: the color densities for each value of the risk index :
                    (1D numpy array of color densities for each risk index; e.g. in RGB, the first 1D array is Red)
    :return: the color associated to the risk level
    """
    cvals = [np.interp(rlev, cpal.cdefs[0], cpal.cdefs[1 + i]) for i in range(len(cpal.csys))]
    if cpal.csys in ["CMYK", "RGB"]:
        thecol = Color(cpal.csys, *cvals, 1.0)  # Alpha is always 1 (no transparency) for embers
    else:
        raise EmberGraphBadRequest("Undefined color system")
    return thecol


def showboxes(el: Element):
    """
    The purpose of showboxes is debugging. It shows the bounding box and drawing area for an element
    """
    if gettrace and gettrace():  # If debug
        cx = el.cx
        cy = el.cy
        c = el.c if not el.egr and hasattr(el, "c") else el.egr.c

        # Put out some debugging information
        if el.egr is not None:
            el.egr.logger.addinfo(f"Element: {el.type}, parent: {el.parent_type}, children: {len(el.elements)}")
        elif el.logger is not None:
            el.logger.addinfo(f"Element (not attached): "
                              f"{el.type}, parent: {el.parent_type}, children: {len(el.elements)}")
        if el.type == "EmberGraph":
            # Drawing area (inner frame)
            c.rect(cx.c0, cy.c0, cx.c, cy.c, stroke="grey", dash=[3, 3])
        elif el.type == "GraphLine":
            # Drawing area (inner frame)
            c.rect(cx.c0, cy.c0, cx.c, cy.c, stroke="blue", dash=[3, 3])
        else:
            # Bounding box (outer frame)
            c.rect(cx.b0, cy.b0, cx.b, cy.b, stroke="red")
            c.line(cx.b0, cy.b0, cx.b1, cy.b1, stroke="red", stroke_width=0.3)
            # Drawing area (inner frame)
            c.rect(cx.c0, cy.c0, cx.c, cy.c, stroke="green", dash=None)


def gp_lst_to_dict(gp, newdict, oldkey, newkey, index):
    """
    Inserts a parameter from the global parameters (gp) into a dictionary, if it exist,
    to facilitate the conversion from the EmberFactory 'old' haz_grid_lines to the EM add_lines
    """
    try:
        val = gp.lst(oldkey)[index]
        if val is not None:
            newdict[newkey] = val
    except IndexError:
        pass
