from __future__ import absolute_import

VERSION = (0, 8, 6)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

from .client import SolrClient
