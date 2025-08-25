from ..imports import *
from .initFuncs import initFuncs
# New Tab: Directory Map
class editTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()
        install_common_inputs(
            self, grid, bus=None,
            primary_btn=("Run search", self.start_search),
            secondary_btn=("Open all hits", self.open_all_hits),
        )



        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.open_one)
        self.layout().addWidget(self.list, stretch=3)
        self._last_results = []
editTab = initFuncs(editTab)
