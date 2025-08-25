# This file contains 'conversion' rules for variables (units), and code to get a converter function.

# Conversion rules:
# - the key is the source (original) variable; the rules defines its conversion to a standard variable
# - there is only one standard variable for each source, hence each source is found in one and only one rule.
conv_haz = {
    # 'from': ('to', mult, add) => to = from * mult + add
    'GMSST': ('GMT', 1.44, 0),
    'GM-SST': ('GMT', 1.44, 0),
    'SST': ('GMT', 1.44, 0),
    'GMT_AR5': ('GMT', 1.0, 0.08),
    'GMT': ('GMT', 1.0, 0.0), # Would be used if the request is to change from GMT to something else.
    'GMST': ('GMT', 1.0, 0.0)  # GMST = GMT for the embers in AR6 special reports, but it might be defined differently.
}

def get_var_converter(source, target='GMT') -> callable:
    """
    Returns a function which performs the conversion from the source unit to the optional target unit (default: 'GMT')
    :param source: a source unit
    :param target: a target unit, default is GMT
    :return: a function which converts its argument from source to target variable.
    """
    if source.upper() == target.upper():
        return lambda dat: dat

    try:
        newvar, fact, shift = conv_haz[source.upper()]
    except KeyError:
        raise KeyError(f"Unknown source variable: {source}")
    if newvar != target:
        try:
            stdvar, stdfact, stdshift = conv_haz[target.upper()]
        except KeyError:
            raise KeyError(f"Unknown target variable: '{target}'")
        shift = shift - stdshift
    else:
        stdfact = 1.0
        stdvar = newvar
    if newvar != stdvar:
        raise LookupError(f"Cannot convert '{source}' to '{target}'")
    converter = lambda dat: (dat * fact + shift) / stdfact
    return converter

def conv_std(source):
    """For a given source variable name, get the standard variable name according to the conversion rules, if any"""
    try:
        return conv_haz[source.upper()][0]
    except KeyError:
        return source
