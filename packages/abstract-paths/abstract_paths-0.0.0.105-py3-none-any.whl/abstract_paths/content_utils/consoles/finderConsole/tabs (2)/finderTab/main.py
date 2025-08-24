from ..imports import *
from .initFuncs import initFuncs
# New Tab: Directory Map
class finderTab(QWidget):
    def __init__(self, bus: SharedStateBus=None):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()
        self.bus = bus
        if self.bus:
            install_common_inputs(
                self, grid, bus=self.bus,
                primary_btn=("Run search", self.start_search),
                secondary_btn=("Open all hits", self.open_all_hits),
            )
        attach_functions(self, hot_reload=True)

