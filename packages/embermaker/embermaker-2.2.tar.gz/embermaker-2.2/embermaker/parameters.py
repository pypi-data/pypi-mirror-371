# -*- coding: utf-8 -*-
from embermaker import helpers as hlp
from embermaker.drawinglib.helpers import cm, mm, units
from os.path import join
import re

"""
        gp[key] => 'main' part of the value
        gp.lst(key) => 'list' part of the value
"""

# Deprecated parameters. These are deprecated for several years now (end 2023), with no changes.
# handling of these parameters could be entirely removed in future versions.
default_deprecated = {'haz_top_value': (('haz_axis_top', 'haz_valid_top'), None),
                      'haz_bottom_value': (('haz_axis_bottom', 'haz_valid_bottom'), None)}


class ParamDict(dict):
    """
    ParamDict is meant to store Graphic Parameters. It is a substantially modified type of dictionnary, because
    - there is a mechanism to handle deprecated parameters, by copying them to new names and possibly issuing a message
    - parameters values are made of 3 parts: value = [main, list, type]
    The main part is a single value; the list part is a list containing additional information;
        the type is a single character: S for string type, F for float, L for length on the canvas (a float),
        B for boolean.
    paramdict[key] will return the 'main' value;
    paramdict.list[key] will return the additional list, if any.
    NB: this could be done with a parameter class having all 3 'parts' has attributes instead of a list.
    It would be slightly slower, but that would most likely not be significant.
    That would probably make the code more readable (e.g. value[Ø] would become parameter.main); but is it useful?
    """

    def __init__(self, *args, logger=None, **kw):
        super(ParamDict, self).__init__(*args, **kw)
        self._deprecated = default_deprecated
        self.logger = logger if logger else hlp.Logger()

        # Get parameter names, types, and default values:
        self.readmdfile(join(hlp.getpath_defaults(), "paramdefs.md"))

    def __setitem__(self, key, data):
        """ Updates paramdict[key] by setting its
                'list part'=data if data is a list, otherwise its
                'main part'=data,
            handling deprecated parameters and rejecting unknown parameters
        """
        key = key.strip()
        isdeprec = self._handle_deprecated(key, data)
        if isdeprec:
            self.logger.addinfo(f'Deprecated parameter was substituted: {key}')
        else:
            if key not in self:
                self.logger.addwarn(f'Unknown parameter: {key}')
                pass
            else:
                value = self.getvalue(key)
                if isinstance(data, list):
                    # The input was a list => set it as list part of the parameter (value[1])
                    value[1] = data
                elif value[2] in ('F', 'L', 'B'):
                    data = data.strip() if isinstance(data, str) else data
                    # The input was not a list, and the parameter is not defined as a string
                    if data in ['', '-']:
                        # The input was empty
                        value[0] = None
                    elif value[2] == 'B':  # The parameter is defined as boolean
                        if isinstance(data, str) and data.lower() == 'false' or data == 0:
                            value[0] = False
                        elif isinstance(data, str) and data.lower() == 'true' or data == 1:
                            value[0] = True
                        else:
                            self.logger.addwarn('Ignored parameter "{}" because its value ({}) could not be'
                                                'converted to a logical value (boolean)'.format(key, data))
                    else:  # A number is expected
                        try:
                            if data is not None:
                                value[0] = float(data)
                        except (ValueError, TypeError):
                            self.logger.addwarn('Ignored parameter "{}" because its value ({}) '
                                                'could not be converted to a number'.format(str(key), str(data)))
                else:
                    # The parameter type is string and the input is not a list => string
                    value[0] = str(data)
                super(ParamDict, self).__setitem__(key, value)

    def __getitem__(self, key):
        return self.getvalue(key)[0]

    def __str__(self, *args, **kwargs):
        """Provides a human-readable string representing itself"""
        out = ''
        for key in list(self):
            val = super(ParamDict, self).__getitem__(key)
            if len(val) > 1 and val[0]:
                out += ";\n  " if out != '' else ''
                out += f"{key}: {val[0]}"
                if val[1]:
                    out += f" {val[1]}"
        return out

    def __call__(self, key, norm=True, **kwargs):
        """
        Simplifies the syntax by replacing calls of the form norm(gp[key]) with gp(key)
        ! Note the parenthesis: it is the syntax of a function, hence gp(key, default =...) is permitted.
        May replace get() calls.
        :param key:
        :param default:
        :return:
        """
        main = self.getvalue(key)[0]
        if (main is not None and main != '') or 'default' not in kwargs:  # if no default, keep as is, including ''.
            if norm:
                return hlp.norm(main)
            else:
                return main
        else:
            return kwargs['default']

    def get(self, key, default=None, norm=False):
        self.__call__(key, norm=norm, default=default)

    def setnew(self, key, value):
        """ Sets a new parameter key/value[main,list,type], handling deprecated parameters"""
        key = key.strip(' \t')  # Get rid trailing white spaces and/or tabs
        isdeprec = self._handle_deprecated(key, value)
        if not isdeprec:
            super(ParamDict, self).__setitem__(key, value)

    def getvalue(self, key: str) -> list:
        try:
            val = super(ParamDict, self).__getitem__(key)
        except KeyError:
            self.logger.addwarn('Internal error - requested parameter is not defined: {}'.format(key))
            # For consistency with __setitem__, return None as the main value (= no value)
            val = [None, None, '']
        if not isinstance(val, list):
            self.logger.addwarn('Malformed parameter: {}:{}'.format(key, val))
            val = [None, None, '']
        return val

    def lst(self, key) -> list:
        """
        Gets the list part of the parameter. If the list part is not defined yet, returns an empty list
        (possible future change: 'list part = None' may be replaced with empty list already within the
        stored parameter, if that does not cause incompatibilities; moreover, the 'list concept' may be simplified)
        :param key:
        :return:
        """
        tlst = self.getvalue(key)[1]
        if type(tlst) is not list:
            tlst = list()
        return tlst

    def lst_norm(self, key):
        """
        Gets the list part of the parameter, after "normalisation"; any string becomes lower case
        :param key:
        :return:
        """
        return hlp.norm(self.getvalue(key)[1])

    def set_lst_at(self, key: str, idx: int, data: int | float | str):
        """
        Within parameter `key`, defines the `idx`-element of the list part to `data`.
        This function enables arbitrary idx (< 51); if needed, it fills the list with None elements up to idx.
        """
        lst = self.lst(key)
        try:
            lst[idx] = data
        except IndexError:
            for _ in range(idx - len(lst)):
                lst.append(None)
            lst.append(data)
        self.__setitem__(key, lst)

    def update(self, adict=None, **kwargs):
        """ Updates self with adict, handling deprecated parameters (nothing done for other cases)
            use of ParamDict.update(dict) is not recommended but was tested on a simple case."""
        if type(adict) is not dict:
            adict = dict(adict)
        for key in adict.keys():
            isdeprec = self._handle_deprecated(key.strip(), adict[key])
            if isdeprec:
                del adict[key]
            else:
                self.__setitem__(key, adict[key])

    def _handle_deprecated(self, key, value):
        """
        Process the passed key,value pair according to what is set in self._deprecated, when needed.
        :param key:
        :param value:
        :return: isdeprecated: True if key is in the list of deprecated parameters
        """
        if key in list(self._deprecated):
            # the new parameter and the msg to use for this deprecated parameter [key]:
            newpars, msg = self._deprecated[key]
            if newpars is not None:
                for npa in newpars:
                    self[npa] = value
            if msg is not None:
                self.logger.addwarn("Deprecated parameter: {}. {}".format(key, msg))
            return True
        return False

    def setdeprecated(self, deprecated):
        """
        Sets a dict of deprecated parameters including information on how to handle them.

        :param deprecated: a dict of deprecated parameters:
               {name_of_old_parameter: ((new_param_1, new_param_2 if any, ...), str warning_message or None)}
               new_params can be in a list or tuple, but if tuple, remember that ('newpar1')
               would not make a tuple, only ('newpar1',) would make one.
        :return:
        """
        self._deprecated = deprecated

    def readmdfile(self, filepath):
        """
        Generates a dictionnary of parameters (ParamDict) from a standard file providing parameter names, defaults, etc.
        :param filepath:
        :return:
        """
        with open(filepath, encoding="utf8") as fi:
            waittable = True
            for iline, line in enumerate(fi):
                line = line.rstrip('\n').strip(' \t|')  # cleanup: start after any |, get rid of end-of-line
                # Lines which are not in a table are not read and imply a status of 'waiting for table data':
                if line == '':
                    waittable = True
                    continue
                if waittable:
                    if "-------" in line:
                        waittable = False
                    continue
                # We reach this point when the line is in a table
                # lines containing certain html tags are only for the documentation, => pass
                if re.search('<.+?>', line) \
                        and any(tagf in line for tagf in ['<h2', '<h3>', '<h4>', '<section', '</section']):
                    continue
                cells = [cl.strip() for cl in line.split('|')]
                if "<del>" in cells[0]:  # Deprecated parameter - pass
                    continue
                if len(cells) != 3:
                    self.logger.addwarn(
                        "Internal problem in the list of parameters (no description?): |{}|".format(line))
                    continue
                key, c1, c2 = cells
                # Get additional data, if any
                if '[' in c1 and ']' in c1:  # There is additional data
                    stdat = c1.find('[')
                    lst = c1[stdat + 1: c1.find(']')]
                    lst = None if lst == '' else lst.split(';')
                    main = c1[:stdat].rstrip()
                else:
                    main = c1
                    lst = None
                main = main if main != '-' else ''  # '-' or '' are equivalent and mean 'No value'
                # Get type of data and process value when needed:
                if "(number)" in c2:
                    dtype = 'F'
                    main = None if main == '' else float(main)
                elif "(length)" in c2:
                    dtype = 'L'
                    # Process units of length, if any
                    if ' cm' in main:
                        main = float(main.replace(' cm', '')) * cm
                    elif ' mm' in main:
                        main = float(main.replace(' mm', '')) * mm
                    else:
                        main = None if main == '' else float(main)
                elif "(logical)" in c2:
                    dtype = 'B'  # Boolean
                    main = None if main == '' else main.lower() != 'false'
                else:  # Default type is string
                    dtype = 'S'
                self.setnew(key, [main, lst, dtype])
        return

    def readparams(self, wbook):
        if "Graph parameters" in wbook.sheetnames:
            sht = wbook["Graph parameters"]
            for row in sht.rows:
                if isinstance(row[0].value, str):
                    key = row[0].value.strip()
                    # Find the position of the last non-empty cell + 1, or 1 if there is none:
                    # next() gets the first value of the iterator, which is what we want; the list is read from its end
                    rowlen = next(i for i in range(len(row), 0, -1) if row[i - 1].value or i == 1)
                    # Main part of the parameteter : empty str will leave the default value untouched, '-' would delete:
                    main = row[1].value
                    isunit = rowlen > 2 and row[2].value in units
                    if isunit:
                        main *= units[row[2].value]
                    if not hlp.isempty(main):
                        self[key] = main
                    # The user provided a list of values -> store this as list part of the parameter:
                    if rowlen > 2 and not isunit:
                        self[key] = [c.value for c in row[2:rowlen]]
