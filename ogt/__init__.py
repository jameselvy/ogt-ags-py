import os

####################################################
# Note this file is for variables only, no imports
# except standard libs where necessary
# as its imported for docs gen etc
####################################################

PROJECT_VERSION = "0.0.1"

PROJECT_SHORT = "ogt-ags-py"
PROJECT_LONG = "Open GeoTechnical AGS Tools"

PROJECT_DESCRIPTION = "Lib and tools for playing geotechnical stuff"
PROJECT_CONTACT = "ogt@daffodil.uk.com"

PROJECT_DOMAIN = "ogt.daffodil.uk.com"
PROJECT_WWW = "http://open-geotechnical.github.io/"
PROJECT_HOME = "https://github.com/open-geotechnical/ogt-ags-py"
PROJECT_ISSUES = "https://github.com/open-geotechnical/ogt-ags-py/issues"
PROJECT_API_DOCS = "http://open-geotechnical.github.io/ogt-ags-py"


def get_project_info():
    """
    :return: A `dict` with the project info
    """
    return dict(
        version = PROJECT_VERSION,
        short = PROJECT_SHORT,
        long = PROJECT_LONG,
        description = PROJECT_DESCRIPTION,
        contact = PROJECT_CONTACT,
        domain = PROJECT_DOMAIN,
        www = PROJECT_WWW,
        home = PROJECT_HOME,
        issues = PROJECT_ISSUES,
        api_docs = PROJECT_API_DOCS
    )



HERE_PATH =  os.path.abspath( os.path.dirname( __file__))

PROJECT_ROOT_PATH = os.path.abspath( os.path.join(HERE_PATH, ".."))
"""Root dir of this project"""

TEMP_WORKSPACE = os.path.join(PROJECT_ROOT_PATH, "temp_workspace")
"""Path to temporary directory"""

EXAMPLES_DIR = os.path.join(PROJECT_ROOT_PATH, "example_files")
"""Path to examples folder"""

USER_HOME = os.path.expanduser("~")
"""Path to users home dir"""

USER_TEMP = os.path.join(USER_HOME, "ogt-cache")
"""Path to open-getechnical cache directory"""




FORMATS = ["json", "js", "geojson", "yaml", "xlsx", "ags4"]
"""Formats allowed, depending on stuff installed"""





HAVE_YAML = False
"""`True` if :ref:`yaml` lib is installed"""
try:
    import yaml
    HAVE_YAML = True
except ImportError:
    pass

HAVE_EXCEL = False
"""`True` if :ref:`excel`  handling libs installed"""
try:
    import openpyxl
    HAVE_EXCEL = True
except ImportError as e:
    pass

HAVE_GEOJSON = False
"""`True` if :ref:`excel`  handling libs installed"""
try:
    import geojson
    HAVE_GEOJSON = True
except ImportError as e:
    pass

