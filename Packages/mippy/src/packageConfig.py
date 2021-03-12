"""packageConfig
-------------

Basic information about the package, used by setup.py to populate package metadata.
"""

import os

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__) )

##DOC_DEFAULT_DIR
DOC_DEFAULT_DIR = os.path.join(PACKAGE_DIR, 'docs')
DOC_DIR = os.environ.get('DRQ_CONFIG_DIR', DOC_DEFAULT_DIR)
HOME = os.environ.get('HOME', PACKAGE_DIR)

VERSION_DEFAULT_DIR = os.path.join(HOME, '.src')
VERSION_DIR = os.environ.get('DRQ_VERSION_DIR', VERSION_DEFAULT_DIR)

__version__ = "00.01.01"
__versionComment__ = "Version %s" % __version__
__title__ = "mippy"
__description__ = "A python library supporting access to MIPs using CMIP style directory structure and file names" 
__uri__ = "https://github.com/cmip6dr/Cookbook/tree/master/Packages/mippy"
__author__ = "Martin Juckes"
__email__ = "martin.juckes@stfc.ac.uk"
__license__ = "BSD"
__copyright__ = "Copyright (c) 2015 Science & Technology Facilities Council (STFC)"

version = __version__
