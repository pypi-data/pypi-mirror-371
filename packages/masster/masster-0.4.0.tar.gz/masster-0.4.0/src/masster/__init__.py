"""
master - Mass Spectrometry Analysis Assistant

A comprehensive Python package for processing and analyzing untargeted metabolomics data,
supporting both DDA (Data-Dependent Acquisition) and DIA (Data-Independent Acquisition)
mass spectrometry workflows.
"""

from __future__ import annotations

from master._version import __version__

# from master._version import get_version
from master.chromatogram import Chromatogram
from master.lib import Lib
from master.sample.sample import Sample
from master.spectrum import Spectrum
from master.study.study import Study


__all__ = [
    "Chromatogram",
    "Lib",
    "Sample",
    "Spectrum",
    "Study",
    "__version__",
    #    "get_version",
]
