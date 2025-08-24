# attach_from_path.py
from __future__ import annotations
# functions_console.py
from .imports import QWidget,pyqtSignal,attach_functions,attach_from_neighborhood
from importlib.util import spec_from_file_location, module_from_spec
import os, sys, inspect
from .initFuncs import initFuncs

# --- Console ---------------------------------------------------------------
class functionsTab(QWidget):
    functionSelected = pyqtSignal(str)
    scanRequested = pyqtSignal(str)  # scope string ("all" | "reachable")
    def __init__(self, parent=None, use_flow=True):
        super().__init__(parent)
        self.func_map = {}
        self.fn_filter_mode = "io"
        self.current_fn = None
        # EITHER: a single file next to main.py

functionsTab = initFuncs(functionsTab)
