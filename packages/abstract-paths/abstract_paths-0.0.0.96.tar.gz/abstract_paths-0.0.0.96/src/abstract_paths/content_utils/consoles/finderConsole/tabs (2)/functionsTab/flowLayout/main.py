# functions_console.py
from ..imports import QLayout,attach_functions
from .initFuncs import initFuncs
# --- FlowLayout (chips that wrap) -------------------------------------------
class flowLayout(QLayout):
    def __init__(self, parent=None, margin=0, hspacing=8, vspacing=6):
        QLayout.__init__(self, parent)
        self._items = []
        self._h = hspacing
        self._v = vspacing
        self.setContentsMargins(margin, margin, margin, margin)
        attach_functions(self,base_pkg=__package__,  hot_reload=True)
flowLayout = initFuncs(flowLayout)
