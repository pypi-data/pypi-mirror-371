import os
from abstract_gui import get_for_all_tabs
CONSOLE_DIR_PATH = os.path.abspath(__file__)
CONSOLE_ABS_DIR = os.path.dirname(CONSOLE_DIR_PATH)
get_for_all_tabs(CONSOLE_ABS_DIR)
from .collectFilesTab import collectFilesTab
from .diffParserTab import diffParserTab
from .directoryMapTab import directoryMapTab
from .extractImportsTab import extractImportsTab
from .finderTab import finderTab
from .functionsTab import functionsTab
from .runnerTab import runnerTab
from .editTab import editTab
