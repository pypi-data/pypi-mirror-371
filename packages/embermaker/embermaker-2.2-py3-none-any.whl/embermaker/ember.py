"""
The ember module defines IPCC-style 'burning embers' that can be inserted in ember diagrams (EmberGraph).
"""
import numpy as np
from embermaker import helpers as hlp
from embermaker.helpers import norm
from embermaker.drawinglib.helpers import mm, stringwidth
from embermaker.graphbase import Element, CanPos, draw_vaxis, cbyinterp
from embermaker.defaults.convert import get_var_converter
from embermaker.ember_utils import md_html


def get_skeygroup(sortlist=None):
    """
    Gets a sort key function to sort embers by groups.
    :param sortlist: the ordered list of groups; if None, embers will be sorted by database id or alphabetic order.
    :return: the sort key fct
    """

    def skeygroup(be):
        """
        Used for sorting embers by group. If sortlist is defined, tries to use the order defined in this list.
        :param be: an ember object
        :return: sort key value
        """
        if sortlist:
            try:
                pos = sortlist.index(be.group.lower())
            except ValueError:
                pos = -1
        else:  # sortlist is not defined: will sort by id or alphabetic order
            pos = be.id if be.id else be.name
        return pos

    skeygroup.haslist = sortlist is not None
    return skeygroup


def get_skeyname(sortlist=None):
    """
    Gets a sort key function to sort embers by name.
    :param sortlist: the ordered list of names; if None, embers will be sorted by alphabetic order.
    :return: the sort key fct
    """

    def skeyname(be):
        """
        Used for sorting embers by name. If sortlist is defined, tries to use the order defined in this list.
        :param be: an ember object
        :return: sort key value
        """
        if sortlist:
            try:
                pos = sortlist.index(be.name.lower())
            except ValueError:
                pos = -1
        else:  # sortlist is not defined: will sort by alphabetic order
            pos = be.name
        return pos

    skeyname.haslist = sortlist is not None
    return skeyname


def get_skeyrisk(sortrlev=None, sorthazl=None):
    """
    Gets a sort key based on risk or hazard levels
    :param sortrlev: the risk level for which hazard will be obtained, then used as sort criteria
    :param sorthazl: the hazard level for which risk will be obtained, then used as sort criteria
    :return:
    """

    def skeyrisk(be):
        """
        :param be: an ember object
        :return: sort key
        """
        try:
            hazl = be.levels_values("hazl")
            risk = be.levels_values("risk")
            if sortrlev is not None:
                if risk[-1] > sortrlev:
                    pos = np.interp(sortrlev, risk, hazl)
                else:
                    # Might be improved; idea is to keep a minimal sorting when the sort criteria cannot work...
                    pos = 5.0 + np.interp(sortrlev / 2.0, risk, hazl)
            elif sorthazl is not None:
                if hazl[-1] > sorthazl:
                    pos = np.interp(sorthazl, hazl, risk)
                else:
                    pos = risk[-1]
            else:
                raise Exception("Skeyrisk cannot generate a sort key because no sort level was provided.")
        except ValueError:
            pos = 999
        if be.getmeta("inclusion_level") == 0:  # Ignore embers with Inclusion Level = 0; could be improved?
            pos = -1  # ignore ember
        return pos

    skeyrisk.haslist = sortrlev is not None or sorthazl is not None
    return skeyrisk


def selecsort(lbes, fkey: callable, reverse=False):
    """
    Sorts embers in lbes but ignores those absent from sortlist (=> fkey(be) = -1 above)
    (no ready-made option to do that?).
    :param lbes: a list of BEs
    :param fkey: the sort-key function
    :param reverse: reverses sorting order
    :return: sorted and filtered list of BEs
    """
    # Filtering
    if fkey.haslist:
        # Filtering occurs only if a sort criteria is defined (no sorting => no filtering)
        lbes = [be for be in lbes if fkey(be) != -1]
    # Sorting
    lbes.sort(key=fkey, reverse=reverse)
    return lbes


def drawlinear(egr, xmin, xmax, yamin, yamax, ygmin, ygmax, yvmin, yvmax, plotlevels, colorlevels):
    """
    This method handles the drawing of a colour gradient in a box, to fulfill the common needs of
    drawing embers and drawing the legend.
    :param egr: An Embergraph object
    :param xmin: Main box limits on the canvas, in horizontal (x) direction
    :param xmax: "
    :param yamin: Main box limits on the canvas, in vertical (y) direction
    :param yamax: "
    :param ygmin: Gradient limits on the canvas (may extend beyond the valid area, corresponds to 0-1 in the stops)
    :param ygmax: "
    :param yvmin: Limits of the "valid area"
    :param yvmax: "
    :param plotlevels: Stops within the gardient (as fraction of the total gradient range)
    :param colorlevels: Color at each stop
    :return:
    """
    c = egr.c
    # Set the properties of the box around the ember:
    linewidth = 0.35 * mm
    c.set_stroke_width(linewidth)

    # Useful intermediary variable(s):
    xsiz = xmax - xmin

    # Draw the background grey area in case of 'missing data' (under the entire rectangle)
    c.rect(xmin, yamin, xsiz, yamax - yamin, stroke='black', fill='vlgrey')

    # Enclosing rectangle (= around the 'valid area')
    rect = (xmin, yvmin, xsiz, yvmax - yvmin)

    # Draw the color gradients
    if yamax - yamin > xmax - xmin:  # vertical (the criteria is based on the axis, regardless of the data)
        c.lin_gradient_rect(rect, (xmin, ygmin, xmin, ygmax), colorlevels, plotlevels)
    else:  # horizontal, for legend only (would not work for regular embers, as these are more complex)
        c.lin_gradient_rect(rect, (xmin, ygmin, xmax, ygmin), colorlevels, plotlevels)

    # Draw the surrounding box
    c.rect(xmin, yamin, xsiz, yamax - yamin, stroke='black')


class Level(dict):
    """
    A dictionary providing data about a level (phase, hazl), with additional specific features:
    - storing a reference to the parent transition
    - ability to respond to ['risk'] by calculating the risk index from phase and transition name
    Notes:
        phases are "steps" within transitions (see Transition below).
        'conf' has been moved to Transition.confidence
        methods within this class may be further revised to improve internal consistency (esp. 'phase_index').
    """

    @staticmethod
    def sortlevels(levels: list):
        levels.sort(key=lambda lv: lv.phase_index)

    @staticmethod
    def phase2risk(phasename: str):
        """
        Converts the received "phasename" to the value of the "risk index", relative to the bottom of the transition,
        as fraction of the transition.
        "Phase" refers to a risk level within a transition for which the hazard is assessed, that is, a transition is
        assessed in several "phases" (see Transition).
        :param phasename: name of the 'phase': as min, median, max, or p*
        :return: the risk index, as fraction of the full transition [0-1], relative to the start of the transition
        """
        phname = phasename
        if phname in Transition.phases_syn:
            phname = Transition.phases_syn[phname]

        if phname in Transition.phases_std:
            return Transition.phases_std[phname]
        elif phname[0] == 'p':
            try:
                return float(phname[1:]) / 100.0
            except ValueError:
                pass
        return None

    def __init__(self, trans, *args):
        """
        :param trans: the transition object within which this level resides
        :param args: at least this dictionnary: {"phase":phase, "hazl":hazl}
        """
        super(Level, self).__init__(*args)
        self.trans = trans

    def __getitem__(self, key: str) -> str or float or int:
        """
        Gets data about the level, given the key:
        - phase: the name of the phase within this level (min, max, median, p*)
        - hazl: the hazard level (float)
        - risk: the risk index (float), with the absolute scale that accounts for the transition and level
        :param key: the key for which a value is to be returned
        :return: the value for the given key
        """
        if key in self:
            return super(Level, self).__getitem__(key)
        elif key == "risk":
            if "phase" not in self:
                raise Exception("'risk' is undefined because phase is undefined")
            phasename = super(Level, self).__getitem__("phase")
            # Calculate the risk index from the transition and "phase":
            return self.trans.base_risk(0) + self.phase2risk(phasename) * self.trans.base_risk(1)
        else:
            raise KeyError(key)

    @property
    def phase_index(self):
        """
        The value of the "risk index", relative to the bottom of the transition, as fraction of the transition.
        "Phase" refers to a risk level within a transition for which the hazard is assessed, that is, a transition is
        assessed in several "phases" (see Transition).
        :return: the risk index for this level, as fraction of the full transition [0-1],
                 relative to the start of the transition
        """
        phase = self['phase']
        return self.phase2risk(phase)


class MetaMixin:
    meta: dict

    def getmeta(self, name, default=None, html=False):
        """
        Returns transition-related metadata (these differ from file- or ember- related metadata).
        :param name: the name of the parameter to be returned.
        :param default: a default value, for use when there is no metadata corresponding to this name
        :param html: process the value trough helper.htmlbreaks
        :return: the requested metadata, or None if the metadata is not defined.
        """
        try:
            value = self.meta[name]
            if value is not None and html:
                value = hlp.htmlbreaks(value)
        except KeyError:
            value = default
        if value is None and default is not None:
            value = default
        return value


class Transition(MetaMixin):
    """
    A transition is a fraction of an ember containing data about how risk changes from one level to the next.
    This concept was mostly absent from the first versions of EmberFactory because the risk changes were defined
    as unique, 'global' risk-hazard functions containing all changes.
    It is currently implemented as an addition to the initial framework with minimal interference with it:
    it will enable better documentation of transitions within the Ember class, but the existing EF code will continue
    to work without changes at least in a first step.
    A transition has a name and a list of levels.
    """

    # 'Synonyms', i.e. values which can be used but will be substituted at reading:
    names_syn = {'white to yellow': 'undetectable to moderate',
                 'yellow to red': 'moderate to high',
                 'red to purple': 'high to very high'}
    # Phases are "steps" within transitions; they also have synonyms:
    phases_std = {'min': 0.0, 'median': 0.5, 'max': 1.0, 'mode': 'mode'}
    # mode is not an actual 'phase', it is only used for elicitation
    # the value provided above is the 'percentile' within the transition

    phases_syn = {'begin': 'min', 'end': 'max', 'most likely': 'mode'}
    # A risk level is attributed to each (transition, phase) pair, knowing that
    # Undetectable is level 0, Moderate is level 1, high is level 2 and very high is level 3.
    # For example Undetectable to moderate = 0 -> 1, Moderate to high 1 -> 2...
    # *.5 = Median risk levels, and more generally *.# = percentile # within the transition, noted p#

    # Confidence index
    confidence_std = {'L': 1,
                      'LM': 1.5,
                      'M': 2,
                      'MH': 2.5,
                      'H': 3,
                      'HVH': 3.5,
                      'VH': 4,
                      'None': None}
    # Confidence level names: may be moved in the future
    confidence_names = {'L': 'low',
                        'LM': 'low-medium',
                        'M': 'medium',
                        'MH': 'medium-high',
                        'H': 'high',
                        'HVH': 'high-very high',
                        'VH': 'very high',
                        'None': None}

    def __init__(self, name=None, confidence: str | list[str] = None, tmin=None, tmax=None, tmedian=None,
                 meta: dict = None, **kwargs):
        """
        Creates a new transition (initialised with as much information as provided)
        Note: nested confidence range are supported through using a list as the confidence argument (not mandatory);
        """
        if name in self.names_syn:
            name = self.names_syn[name]
        self.name = name
        self.levels: list[Level] = []
        self.meta = meta if meta else {}  # Dictionary of transition-related metadata, as for embers
        # A mode may be attributed to transitions within the expert elicitation process;
        # in this context, the mode is the most likely value in a probability distribution.
        self.mode = None
        self.be = None  # Parent ember; set when the transition is added to an ember.
        self.confidence = confidence if type(confidence) is list else [confidence]

        dclevels = {'min': tmin, 'median': tmedian, 'max': tmax}
        for kw in kwargs:  # extract data about levels
            if kw[0] == "p" and kw[1:].isdigit():  # percentiles
                dclevels[kw] = kwargs[kw]
            else:
                raise TypeError(f"Transition got an unexpected argument: '{kw}'")

        for dclv in dclevels:
            if dclevels[dclv] is not None:
                self.append_level(dclv, dclevels[dclv])

        if len(self.levels) > 0:  # If zero, the levels were not added yet
            Level.sortlevels(self.levels)

    def __getitem__(self, phase: str) -> Level:
        """
        Returns the level object for the requested phase in this transition.
        :param phase:
        """
        foundlevel = None
        for level in self.levels:
            if level['phase'] == phase:
                foundlevel = level
                break
        return foundlevel

    def __str__(self):
        """
        So that Transitions can 'pretty-print' themselves
        """
        return self.name

    def append_level(self, phase, hazl):
        """
        Adds a level to this transition.
        :param str phase: the name of the phase (see Transition and Level)
        :param float hazl: the hazard level
        :return:
        """
        level = Level(self, {"phase": phase, "hazl": float(hazl)})
        self.levels.append(level)

    def base_risk(self, vid=0):
        """
        Returns risk indexes defining the range of risk within this transition
        :param vid: vid=0 => base risk index within the transition; vid=1 => range of risk indexes in the transition.
        :return:
        """
        if self.be is None or self.be.egr is None or self.be.egr.cpal is None:
            raise Exception(f"Transition '{self.name}' is not attached to an ember: "
                            f"base_risk cannot be provided because risk levels are not defined.")

        transnames_risk = self.be.egr.cpal.transnames_risk
        if self.name not in transnames_risk:
            raise Exception(f"Unknown transition named '{self.name}'")

        return transnames_risk[self.name][vid]

    def phases(self):
        """
        Return the name of the phases of the levels within this transition (e.g. 'min', 'median'...).
        :return:
        """
        return [level['phase'] for level in self.levels]

    @property
    def confidence_index(self, id=0) -> float | None:
        """
        The index corresponding to the (first) confidence level within the transition
        :param id: in rare cases where the transition has more than one confidence level, id is its index in the list.
        :return:
        """
        try:
            return self.confidence_std[self.confidence[id]]
        except (KeyError, IndexError):
            return None


class Ember(Element, MetaMixin):
    """
    An ember is one set of data in a 'burning embers' diagram.
    It contains references to the data for the 'risk transitions', as well as the 'draw' method to plot itself.
    """
    parent_type = "EmberGroup"
    _elementary = True

    def __init__(self, name=None, id=None, longname=None, group=None,
                 haz_valid=None, haz_name=None, haz_name_std=None, haz_unit=None, description=None,
                 keywords: str = None, meta: dict = None, **kwargs):
        """
        Initializes an ember, by creating standard attributes
        :param name: the name of this ember, typically as used in figures
        :param id: a unique id for this ember (optional)
        :param longname: an extended name for this ember, sufficient to make the ember distinguishable from others
        :param group: the name of a group in which this ember is placed
        :param haz_valid: Hazard range (min, max) for which this ember is assumed valid (= risk was assessed)
        :param haz_name: Name of the hazard variable (e.g. 'GMT')
        :param haz_name_std: Standard name of the hazard variable, used for checking consistency (e.g. with an Axis)
        :param haz_unit: Unit of the hazard variable (used for display)
        :param description:
        :param keywords: A list of keywords
        :param meta: specific information that does not fit in the other attributes
        :param kwargs: Data sources may provide additional information, such as (biblio) "references", as keywords
        """
        super().__init__()
        self.name = name if name else ''
        self.id = id if id else (name if name else None)  # id is optional
        self.longname = longname if longname else name
        self.group = group if group else ''
        self.haz_valid = haz_valid if haz_valid else [0, 0]
        self.haz_name_std = haz_name_std
        self.haz_name = haz_name if haz_name else haz_name_std
        self.haz_unit = haz_unit
        self.description = description
        self.keywords = keywords if keywords else ''
        self.meta = meta if meta else {}  # Dictionary of ember-related metadata
        # Transitions:
        self.trans: list[Transition] = []
        # Usage-specific 'external' data that may be attached to embers:
        self.ext = {}
        if kwargs:
            self.meta.update(kwargs)

    def __str__(self):
        """
        So that embers can 'pretty-print' themselves
        :return: Ember longname, if available, otherwise ember name.
        """
        return self.longname if not hlp.isempty(self.longname) else self.name

    def __repr__(self):
        """
        No known way to fully 'represent' embers so this gives a short preview of it
        :return: Ember name/group, 8 first characters
        """
        return f"Ember({self.name[0:8]}/{self.group[0:8]})"

    def __len__(self):
        """
        Returns the number of levels in this ember (total for all transitions)
        """
        # Note: it should be somewhat more efficient to just ask for len(hazl) when hazl is already available
        #       thus this might be useless
        return len(self.levels())

    def trans_append(self, trans):
        """
        Adds the given transition object to this ember, also referencing the ember within the transition
        :param trans:
        :return:
        """
        trans.be = self
        self.trans.append(trans)

    def trans_create(self, name=None, confidence=None, tmin=None, tmax=None, tmedian=None, **kwargs):
        """
        Creates a new transition within this ember
        :param name:
        :param confidence:
        :param tmin:
        :param tmax:
        :param tmedian:
        :param kwargs: may include additional levels defined through percentiles in the form of pXX (e.g. p80)
        :return:
        """
        trans = Transition(name=name, confidence=confidence, tmin=tmin, tmax=tmax, tmedian=tmedian, **kwargs)
        self.trans_append(trans)

    def levels(self):
        """
        Returns a flat list of levels
        :return:
        """
        # List comprehension can be applied successively: a loop is first done on .trans, then on levels it contains
        return [lv for tr in self.trans for lv in tr.levels]

    def levels_values(self, dname):
        """
        Returns a flat list or np array containing one of the data associated to the levels
        :param dname: the name of that data, that is 'risk' (risk index) or 'hazl' (hazard level))
        :return:
        """
        if dname in ('risk', 'hazl'):
            # Same method as for levels, but we apply it directly so that there is only one loop
            return np.array([lv[dname] for tr in self.trans for lv in tr.levels])
        else:
            raise ValueError(dname)

    def draw(self):
        """
        Draws an ember, using parameters from egr.
        Note: there was an experimental option for "circular", pie-shaped embers;
        it is no longer supported at the moment (05/2023)
        """
        egr = self.egr
        c = egr.c

        # Check and convert unit so that the ember data is consistent with its axis
        if self.haz_name_std is not None and self.yaxis.var_name_std is not None:
            self.convert_haz(target=self.yaxis.var_name_std)
        # If both the ember and the axis have no haz_name_std, it is not an error because old files are in that case
        elif not (self.haz_name_std is None and self.yaxis.var_name_std is None):
            self.egr.logger.addfail(f"Ember: '{self.name}' may be inconsistent because the "
                                    f"{'axis' if self.haz_name_std else 'ember'} has no defined haz_ or var_ name_std")

        plotlevels = []
        colorlevels = []

        xmin = self.cx.c0
        xmax = self.cx.c1
        yamin = self.cy.c0
        yamax = self.cy.c1

        self.egr.logger.addinfo(f"Ember: {self.name}", mestype='subtitle')

        # Check that the data is consistent, reporting any issues with the logger
        self.check()

        # Get risk and related hazard levels data
        risk = self.levels_values('risk')
        hazl = self.levels_values('hazl')

        if len(risk) == 0:
            return

        # Canvas range occupied by the gradients:
        ygmin = min(self.cy.tocan(np.min(hazl)), yamin)  # (also ok with inverted axis)
        ygmax = max(self.cy.tocan(np.max(hazl)), yamax)
        # Canvas range for the "valid" area (intersection of the valid range and axis):
        yvmin = max(self.cy.c0, self.cy.tocan(self.haz_valid[0]))  # (ok with inverted axis, if haz_valid unchanged)
        yvmax = min(self.cy.c1, self.cy.tocan(self.haz_valid[1]))
        if yvmin == yvmax:
            egr.logger.addfail(f"Critical error: no valid range for this ember.")

        # To ensure full consistency, all hazard values are converted to canvas coordinates, and divided
        # by the range of each gradient in these coordinates (ygmax - ygmin) when plotting a gradient.
        # 'stops' are position within a gradient; they are defined as % of the whole range of the gradient.
        stops = [(self.cy.tocan(ahl) - ygmin) / (ygmax - ygmin) for ahl in hazl]
        axdir = 1 if self.cy.d > 0 else -1  # To care for situations of inverted axis (normal = 1, inverted = -1)

        # Remove any transition overlaps within the ember colours (do not change levels used to illustrate transitions)
        #   and also prevent potential software issues with "abrupt transitions" where two stops are identical
        for ilev in np.arange(len(stops) - 1):
            if (stops[ilev + 1] - stops[ilev]) * axdir < 0:  # Overlapping transitions; colours cannot overlap!
                stops[ilev] = (stops[ilev + 1] + stops[ilev]) / 2.0
                stops[ilev + 1] = stops[ilev]
            elif stops[ilev] == stops[ilev + 1] and risk[ilev] != risk[ilev + 1]:  # Two stops are equal: abrupt trans.
                # =>Prevent potential rendering issues which may occur in display software, by moving the stop by -0.01%
                stops[ilev] -= 0.0001 * axdir  # *axdir because inverted axis => stops in decreasing order

        # Generate the lists of colour change positions (= 'stops', here 'plotlevels') and colours (colorlevels):
        ihaz_list = range(len(risk)) if axdir > 0 else reversed(range(len(risk)))
        for ihaz in ihaz_list:
            # Fractional position within a gradient of each colour change
            plotlevels.append(stops[ihaz])
            # Associated colour
            color = cbyinterp(risk[ihaz], egr.cpal)
            colorlevels.append(color)
        # Copy the start and end colors at both ends of the plot range
        # (= extend the last colour beyond the last transition):
        if plotlevels[-1] != 1.0:  # Should avoid introducing duplicates (Python inequality does it right)
            plotlevels.append(1.0)
            colorlevels.append(colorlevels[-1])
        if plotlevels[0] != 0.0:
            plotlevels.insert(0, 0.0)
            colorlevels.insert(0, colorlevels[0])

        egr.logger.addinfo(f"Hazard range of the gradient: "
                           f"{self.cy.todata(ygmin):.2f} - {self.cy.todata(ygmax):.2f} ")
        egr.logger.addinfo("Position as % of gradient range: " + ", ".join([f"{lv:.5f}" for lv in plotlevels]))
        egr.logger.addinfo(f"Colors: " + ", ".join([str(col) for col in colorlevels]))

        drawlinear(egr, xmin, xmax, yamin, yamax, ygmin, ygmax, yvmin, yvmax, plotlevels, colorlevels)

        # Add the name of the BE
        # - - - - - - - - - - -
        if egr.gp['be_name_rotate'] > 0:
            align = 'right'
            # rough estimate of the available length (could be improved if used)
            namlen = np.sqrt((egr.gp['be_x'] + egr.gp['be_int_x']) ** 2 + egr.gp['be_bot_y'] ** 2)
        else:
            align = 'center'
            namlen = egr.gp['be_x'] + egr.gp['be_int_x']
        namheight = c.paragraph(xmin + egr.gp['be_x'] / 2.0, yamin - egr.gp['fnt_size'] * 0.15, self.name,
                                width=namlen, align=align, rotate=egr.gp['be_name_rotate'],
                                valign='top', font=(egr.gp['fnt_name'], egr.gp['fnt_size']))

        # Annotation / Tooltip
        # - - - - - - - - - -
        if self.description and self.description.strip():
            ys = namheight + egr.gp['fnt_size'] * 0.8
            yb = yamin - ys
            xs = egr.gp['be_x'] + egr.gp['be_int_x'] * 1.1
            xb = (xmin + xmax) / 2.0 - xs / 2.0
            c.rect(xb, yb, xs, ys,
                   stroke="transparent", fill="transparent", stroke_width=2,
                   tooltip=self.description.replace('"', '&#8242; ').replace('&', '&#38;'),
                   tooltip_dy=0, corner_radius=3)

            self.addtranstips(egr, xmin, yamin)

        # Add lines and marks indicating the confidence levels :
        # - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.drawconf(egr, xmin)

    def drawconf(self, egr, xbas):
        """
        Draws lines and marks indicating the confidence levels.
        :param egr: the EmberGraph object in which this ember is drawn.
        :param xbas: the left of the current ember (embers only have a y-axis, hence the need for an x start position).
        """
        c = egr.c
        hazl = self.levels_values('hazl')
        if hlp.isempty(hazl) or len(hazl) == 0:
            return
        color = 'black'

        if norm(egr.gp['show_confidence']) not in ('false', ''):
            # Set the font type and size for the symbols;
            # a scaling factor may be provided as attribute of conf_levels_graph
            fsize = egr.gp['fnt_size'] * egr.gp['conf_levels_graph']
            fname = (egr.gp('conf_fnt_name', default=egr.gp['fnt_name'], norm=False)).strip()  # use specific font
            c.set_stroke_width(0.3 * mm)
            # Get confidence level names and symbols:
            cffile = norm(egr.gp.lst('conf_levels_file'))
            cfgraph = egr.gp.lst('conf_levels_graph')

            # Define the 'gap' between confidence lines which make sures that they are not contiguous:
            if egr.gp['conf_lines_ends'] in ('bar', 'datum'):  # New types of transition/confidence marking
                ygap = 0
            else:
                ygap = self.cy.c * 0.005

            maxychi = hazl[0]  # Top of uncertainty range lines so far, to detect overlaps (initial val for ember)
            midychi = hazl[0]  # Middle of uncertainty range lines so far, to detect large overlaps
            lconflen = 0  # Stores the length of the last uncertainty range mark, to help further staggering

            # Basis position of conf levels marks on the horizontal axis
            # (xconfstep is also used to stagger the lines showing uncertainty ranges)
            if norm(egr.gp['show_confidence']) == 'on top':
                xconfstep = min(0.1 * egr.gp['be_x'], 4 * mm)
                xconf = xbas + xconfstep
                otop = True
            else:
                xconfstep = min(0.1 * egr.gp['be_int_x'], 2 * mm)
                xconf = xbas + egr.gp['be_x'] + xconfstep
                otop = False

            # Plot the confidence markings
            # . . . . . . . . . . . . . . .
            # Confidence markings may be conceptually complex; a technical information note explains the rules.
            overlapstag = 0
            for tran in self.trans:
                plevels = tran.levels

                for ic, conf in enumerate(tran.confidence):
                    if hlp.isempty(conf):
                        continue
                    if 2 * (ic + 1) > len(plevels):
                        egr.logger.addwarn(f"Could not define a 'transition range' for {self.name}, {tran.name}")
                        break  # There is no range (of levels, within tran) to apply this confidence statement to.
                    # For example ic = 1 (2nd conf statement) is applicable if len (plevels) is at least 4
                    # ... unless we build a way to convey confidence about the median (then it would be at least 3).
                    levlo = plevels[ic]
                    levhi = plevels[- ic - 1]

                    # Calculate limits of the colour transitions along the hazard axis
                    # Lower limit of the transition 'line' in canvas coordinate:
                    yclo = self.cy.tocan(levlo['hazl'])
                    if yclo >= self.cy.c1:  # Skip any transition that would be entirely outside the plot range
                        egr.logger.addinfo('A transition is above the top of the hazard axis => skipped')
                    else:
                        # Avoid extension of the shown line above the upper end of the graph (axis):
                        if self.cy.tocan(levhi['hazl']) > self.cy.c1:
                            ysym = False  # 'error bar'-like lines shall be 'open' = with no symbol on upper edge
                            ychi = self.cy.c1
                        else:
                            ysym = True
                            ychi = self.cy.tocan(levhi['hazl'])
                        yconf = (yclo + ychi) / 2.0 - fsize / 2.8  # Centering of the font inside the line is rough!

                        # Move the line and conf label to the right if there is an overlap:
                        # (1) only the lower end of the line has an overlap
                        if yclo < maxychi:
                            overlapstag += xconfstep / 2.0
                        else:
                            overlapstag = 0
                        # (2) even the confidence level text mark has an overlap - further move to the right:
                        if yclo < midychi:
                            overlapstag += lconflen * fsize / 2.0

                        # Updates to detect overlaps in the upcoming uncertainty ranges
                        maxychi = max(maxychi, ychi)
                        midychi = max(midychi, yconf)

                        # If 'on top' of ember, set confidence levels colour to ensure visibility:
                        if otop:
                            backcol = cbyinterp((levlo['risk'] + levhi['risk']) / 2, egr.cpal)
                            if backcol.luminance() > 0.5:  # Bright background
                                color = 'black'
                            else:
                                color = 'white'
                        # Convert the confidence level name to the symbol from the graph parameters
                        try:
                            sconf = cfgraph[cffile.index(conf)]
                        except ValueError:
                            if conf.lower() != 'undefined':
                                egr.logger.addwarn(
                                    'Confidence level from file could not be converted to graph symbol: ' + conf)
                            sconf = ""
                        # Main line highlighting the transition
                        xc = xconf + overlapstag
                        c.line(xc, yclo + ygap, xc, ychi - ygap * ysym, stroke=color)  # ysym = 0 means no symbol
                        # Show transition range limits (new options: historical default is have a white 'gap' instead)
                        if egr.gp['conf_lines_ends'] == 'bar':
                            xc0 = xc - self.cy.c * 0.008  # Edges bar width
                            xc1 = xc + self.cy.c * 0.008
                            c.line(xc0, yclo, xc1, yclo, stroke=color)
                            if ysym:
                                c.line(xc0, ychi, xc1, ychi, stroke=color)
                        elif egr.gp['conf_lines_ends'] in ('datum', 'arrow'):  # Triangles or arrows at both ends
                            xc0 = xc - self.cy.c * 0.01  # Edges width
                            xc1 = xc + self.cy.c * 0.01
                            yc = self.cy.c * 0.012  # length
                            if egr.gp['conf_lines_ends'] == 'datum':  # Triangle with base at edge
                                c.polyline([(xc, yclo + yc), (xc0, yclo), (xc1, yclo), (xc, yclo + yc)],
                                           fill=color, stroke_width=0)  # no stroke => ends precisely at interv. limits
                                if ysym:
                                    c.polyline([(xc, ychi - yc), (xc0, ychi), (xc1, ychi), (xc, ychi - yc)],
                                               fill=color, stroke_width=0)
                            else:  # usual arrow
                                c.polyline(
                                    [(xc, yclo + yc), (xc1, yclo + yc), (xc, yclo), (xc0, yclo + yc), (xc, yclo + yc)],
                                    fill=color, stroke_width=0)
                                if ysym:
                                    c.polyline([(xc, ychi - yc), (xc1, ychi - yc), (xc, ychi),
                                                (xc0, ychi - yc), (xc, ychi - yc)],
                                               fill=color, stroke_width=0)

                        # Confidence marking
                        c.string(xconf + fsize / 8 + overlapstag, yconf, sconf, font=(fname, fsize), color=color,
                                 altcolor='grey')
                        # Handle the staggering of the next line, if needed
                        lconflen = len(sconf)

    def addtranstips(self, egr, xbas, yember=None):
        """
        Adds a tooltip to each transition, if explanation_short is available
        :param egr: the EmberGraph object in which this ember is drawn.
        :param xbas: the left of the current ember (embers only have a y-axis, hence the need for an x start position).
        :param yember: y position of the ember, as reference for the tooltip
        """
        c = egr.c
        hazl = self.levels_values('hazl')
        if hlp.isempty(hazl) or len(hazl) == 0:
            return

        for tran in self.trans:
            plevels = tran.levels
            expl = tran.getmeta("explanation_short")
            if not expl or not expl.strip():
                expl = "Explanatory text not available yet."

            expl = md_html(expl)
            yclo = self.cy.tocan(plevels[0]['hazl'])
            ychi = self.cy.tocan(plevels[-1]['hazl'])
            siz = egr.gp['be_x'] + egr.gp['be_int_x'] + 8

            c.rect(xbas - egr.gp['be_int_x'] / 2.0, yclo, siz, ychi - yclo,
                   stroke="transparent", fill="transparent", stroke_width=2,
                   tooltip=expl.replace('"', '&#8242; ').replace('&', '&#38;'),
                   tooltip_dy=ychi - yember, corner_radius=3 )

    def set_cx(self, base_x):
        self.cx.cp = CanPos(base_x, self.egr.gp["be_int_x"] / 2.0, self.egr.gp["be_x"], self.egr.gp["be_int_x"] / 2.0)
        return self.cx.b1  # Right end of this element => left of the following one

    def check(self):
        """
        Checks consistency of the ember's data.
        :return:
        """
        hazl = self.levels_values('hazl')
        risk = self.levels_values('risk')
        if len(self.trans) == 0 or len(self.trans[0].levels) < 2:
            self.egr.logger.addwarn(f"No data or insufficient data for an ember: '{self.name}'", severe=True)
        else:
            for ilev in np.arange(len(hazl) - 1):
                rdir = 1 if (risk[-1] >= risk[0]) else -1
                if ((hazl[ilev + 1] - hazl[ilev]) * rdir) < 0:
                    # While it might be that some risk decreases with hazard, this is unusual => issue warning
                    self.egr.logger.addwarn(f"Risk does not increase with hazard or a transition ends above the start "
                                            f"of the next one [{hazl[ilev]} then {hazl[ilev + 1]}] "
                                            f"for ember: '{self.name}'")

            r0 = min(risk)
            r1 = max(risk)
            for irisk in self.egr.cpal.cdefs[0]:  # For all risk levels that are associated to a colour...
                # Catch any risk level that is within the range of this ember but not defined in this ember:
                if r0 <= irisk <= r1 and irisk not in risk:
                    self.egr.logger.addwarn(
                        "An intermediate risk level appears undefined; this will likely result in an abnormal "
                        f"colour transition for ember: '{self.name}'", severe=True)

        for tr in self.trans:
            # for each 'phase' within this transition, get the risk index
            # (relative to the base of the transition: we want to look for min/max within the transition)
            slevs = sorted(tr.levels, key=lambda lv: lv.phase_index)
            if slevs[0].phase_index != 0.0:
                self.egr.logger.addwarn(f"The start (min) is not defined for transition '{tr.name}' in '{self.name}'")
            if slevs[-1].phase_index != 1.0:
                self.egr.logger.addwarn(f"The end (max) is not defined for transition '{tr.name}' in '{self.name}'")
            if len(slevs) > 2:
                grow = slevs[-1]["hazl"] - slevs[0]["hazl"]
                for il in range(len(slevs)-1):
                    if (slevs[il+1]["hazl"]-slevs[il]["hazl"]) * grow < 0:
                        self.egr.logger.addwarn(
                            f"Hazard changes are not monotonic in transition '{tr.name}' in '{self.name}'", severe=True)

            # trs = tr.levels.sort(key = lambda lv : [Level.phase2risk(lv['phase']) for lv in tr.levels])

    def convert_haz(self, target: str = 'GMT', logger=None):
        """
        Convert the hazard levels to a common variable/unit, usually GMT (formerly named GMST),
        following a linear transformation provided in defaults/convert.py
        :param target: name of the target unit
        :param logger: optional logger (from `helpers.py`)
        :return:
        """
        if logger is None:
            logger = hlp.Logger()

        if self.haz_name_std.upper() == target.upper():
            return  # unit already matches the target

        fconv = get_var_converter(self.haz_name_std, target=target)
        for level in self.levels():
            level['hazl'] = fconv(level['hazl'])
        logger.addinfo(f"Variable conversion: '{self.haz_name_std}' to '{target}' for {self.name}")
        self.haz_valid = [fconv(self.haz_valid[0]), fconv(self.haz_valid[1])]
        self.haz_name_std = target

    def gethazl(self, itrans, phase: str):
        """
        Returns the hazard level for a given transition and phase
        :param itrans: # or name of transition in the ember
        :param phase:  name of the transition phase (min, max, median...)
        """
        trans = self.trans[itrans] if type(itrans) is int else self.transbyname(itrans)
        return trans[phase]["hazl"]

    def transnames(self):
        return [trans.name for trans in self.trans]

    def transbyname(self, name):
        try:
            itrans = self.transnames().index(name)
        except KeyError:
            return None
        return self.trans[itrans]


class EmberGroup(Element):
    """
    A group of embers, as element in an EmberGraph
    """
    parent_type = "GraphLine"

    def __init__(self, name=None, embers=None):
        super().__init__()
        self.name = name
        if embers is not None:
            self.add(cel=embers)

    def attach(self, egr=None):
        super().attach(egr)
        self.has_vgrid = True
        self.has_vaxis2 = self.has_vaxis and egr.gp['haz_axis2'] in ["True", "Right"]
        self.has_vgrid2 = self.has_vgrid and egr.gp['haz_axis2'] in ["True", "Right"]

    def set_cx(self, base_x):
        # left margin (may include an axis)
        mar_1 = self.has_vaxis * (self.has_axis_name * self.egr.gp["haz_name_x"] + self.egr.gp["scale_x"])
        # right margin
        mar_2 = (self.egr.gp["gr_int_x"] + self.has_vaxis2 *
                 (self.has_axis2_name * self.egr.gp["haz_name_x"] + 3 * self.egr.gp['fnt_size']
                  + stringwidth(self.egr.gp['haz_axis2_unit'], fontsize=self.egr.gp['fnt_size'])))
        # ^^^ rough calculation because there is no specific "scale_x" for axis2
        in_0 = base_x + mar_1
        in_x = in_0
        for el in self.elements:
            in_x = el.set_cx(in_x)  # Asks the ember to set its coordinate, starting at in_x, and get in_x for the next
        self.cx.cp = CanPos(base_x, mar_1, in_x - in_0, mar_2)
        return self.cx.b1  # Right end of this element => left of the following one

    def show_changes(self):
        """
        Draws the lines showing the changes between embers
        :return:
        """
        egr = self.egr
        gp = egr.gp

        # Prepare data for each ember
        bexs = []
        ahlevs = []
        for be in self.elements:
            hazl = be.levels_values('hazl')
            risk = be.levels_values('risk')
            rlevs = gp.lst('show_changes')
            hlevs = np.interp(rlevs, risk, hazl, left=np.nan, right=np.nan)
            # ^When a rlev is outside the range of defined risk values, don't get a hlev (= set it to NaN)
            bexs.append(be.cx.c0 + be.cx.c / 2.0)
            ahlevs.append(hlevs)
            # ^[a]ll [h]azard-[lev]els = for all requested risk levels and all embers in the group

        # Plot the connecting lines
        markers = "o" if "markers" in norm(gp['show_changes']) else None
        ahlevs = np.transpose(ahlevs)
        for shlevs in ahlevs:  # for one curve = for a [s]ingle of the requested risk-levels
            beys = [self.cy.tocan(shlev) for shlev in shlevs]  # scale to Canvas coordinates
            ymax = self.cy.tocan(gp['haz_axis_top'])  # Do not draw line from or to levels above the axis
            for ibe in range(len(beys) - 1):  # Draw, by line segment
                if beys[ibe] <= ymax and beys[ibe + 1] <= ymax:
                    # Dashed line: # 3 unit on, 2 unit off (not done with polyline because gaps may occur)
                    egr.c.line(bexs[ibe], beys[ibe], bexs[ibe + 1], beys[ibe + 1], stroke="tgrey",
                               dash=(3, 2), markers=markers)
            egr.logger.addinfo("Mean hazard / requested risk level: {:.3}".format(np.mean(shlevs)))

    def draw(self):
        egr = self.egr
        gp = egr.gp

        # 'Mapping' as requested by the haz_map_factor and/or haz_map_shift
        self.haz_mapping()
        if self.yaxis.var_name_std is None:
            self.egr.logger.addinfo(f"Embergroup: {self.name} does not have a defined axis var_name_std (=> no check)")

        # Vertical axis and grid lines, if it applies to this group
        if self.has_vaxis or self.has_vgrid:
            draw_vaxis(self)

        # Group title
        # Position in x starts at the left of the first ember colour bar (old design choice),
        # except for groups containing a single ember, which need more space (this is a hack, which might be improved)
        if len(self.elements) == 1:
            width = self.cx.c + gp['scale_x'] + gp['gr_int_x']
            x0 = self.cx.c0 - gp['scale_x']
            align = 'left'
        else:
            x0 = self.cx.c0 + gp['be_int_x'] / 2.0
            width = self.cx.c + gp['gr_int_x'] / 3.0
            align = 'left'
        self.egr.c.paragraph(x0, self.cy.c1 + gp['gr_fnt_size'] / 1.5, self.name, valign='bottom',
                             align=align, width=width, font=('Helvetica', gp['gr_fnt_size']))

        # Draw embers
        super().draw()
        # Show changes between embers (a task of the EmberGroup)
        if norm(gp['show_changes']) in ["true", "lines", "lines+markers"]:
            self.show_changes()

    def haz_mapping(self):
        """
        Optional mapping to a different hazard unit or hazard reference level:
        processing haz_map_factor and haz_map_shift.
        Using these parameters is an old approach that may be replaced by Ember.convert_haz.
        The parameters are applied 'globally' to all embers, with one warning message for each group (= why it is here)
        :return:
        """
        gp = self.egr.gp
        logger = self.egr.logger

        if gp['haz_map_factor'] is None and gp['haz_map_shift'] is None:
            return

        for be in self.elements:
            if be.haz_name_std and "mapped" in be.meta:
                logger.addfail("Internal error: embers would have their hazard axis scaled or shifted twice")
                return
            be.haz_name_std = None  # As the mapping is arbitrary, it results in an unknown std variable.
            be.meta['mapped'] = True

        if gp['haz_map_factor'] is not None:
            logger.addwarn(f"A scaling of the vertical (hazard) axis is requested in the input file (change in unit);"
                           f" haz_map_factor= {gp['haz_map_factor']}")
            for be in self.elements:
                for level in be.levels():
                    level['hazl'] = level['hazl'] * gp['haz_map_factor']

        if gp['haz_map_shift'] is not None:
            logger.addwarn(
                f"A change in the reference level for the vertical axis (hazard) was requested in the input file;"
                f" haz_map_shift= {gp['haz_map_shift']}")
            for be in self.elements:
                for level in be.levels():
                    level['hazl'] = level['hazl'] + gp['haz_map_shift']


def gpsort(embers: list[Ember], gp, logger=None):
    if logger is None:
        logger = hlp.Logger()

    # Sort the embers, if requested (option)
    # --------------------------------------
    # There are two sorting levels. The sorting needs to be done on the second criteria first.
    # Second sorting level
    if gp('sort_2nd_by') == 'name':
        sortlist = gp.lst_norm('sort_2nd_by')
        # Standard Python sorting by f=skeyname + delete embers not in sortlist:
        embers = selecsort(embers, get_skeyname(sortlist))
        logger.addinfo(f"Secondary sorting by name; values: {sortlist}")
    if gp('sort_2nd_by') == 'group':
        sortlist = gp.lst_norm('sort_2nd_by')
        embers = selecsort(embers, get_skeygroup(sortlist))
        logger.addinfo(f"Secondary sorting by group; values: {sortlist}")

    # The first level may swap the role of ember group and name: this allows grouping by names (becoming 'groups')
    if gp('sort_first_by') in ['name', 'group']:
        # Allow sorting according to an order set by a list in the Excel sheet:
        sortlist = gp.lst_norm('sort_first_by')
        logger.addinfo(
            f"Primary sorting by: {gp['sort_first_by']}; values: {sortlist}")
        # Allow grouping by name instead of group, by swapping groups and names:
        if gp('sort_first_by') == 'name':
            for be in embers:
                be.name, be.group = be.group, be.name
        # Sort
        embers = selecsort(embers, get_skeygroup(sortlist))
    return embers


def getgroups(embers: list[Ember]):
    """
    Create groups of embers given the group names provided in each ember (be.group), populate them with the embers,
    and returns the list of group objects.
    :param embers: a list of burning ember
    :return: the list of groups containing the grouped embers
    """
    gbe = None
    gbes = []
    for be in embers:
        if gbe is None or gbe.name != be.group:
            gbe = EmberGroup(name=be.group)
            gbes.append(gbe)
        gbe.elements.append(be)
    return gbes
