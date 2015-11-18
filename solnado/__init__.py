from __future__ import absolute_import

VERSION = (0, 9, 1)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

from .client import SolrClient
