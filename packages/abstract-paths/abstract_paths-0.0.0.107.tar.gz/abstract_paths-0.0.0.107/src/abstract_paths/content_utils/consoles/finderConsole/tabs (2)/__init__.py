import os
from abstract_gui import getInitForAllTabs
ABS_PATH = os.path.abspath(__file__)
ABS_DIR = os.path.dirname(ABS_PATH)
getInitForAllTabs(ABS_DIR)
from .collectFilesTab import collectFilesTab
from .diffParserTab import diffParserTab
from .directoryMapTab import directoryMapTab
from .extractImportsTab import extractImportsTab
from .finderTab import finderTab
from .functionsTab import functionsTab
from .runnerTab import runnerTab
