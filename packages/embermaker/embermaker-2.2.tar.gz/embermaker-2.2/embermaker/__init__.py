"""
EmberMaker is a scientific graphic library aimed at (re)producing "burning ember" diagrams
of the style used in IPCC (Intergovernmental Panel on Climate Change) reports.
"""
import importlib.metadata as meta
try:
    __version__ = meta.version('embermaker')
except meta.PackageNotFoundError:
    __version__ = 'development'
