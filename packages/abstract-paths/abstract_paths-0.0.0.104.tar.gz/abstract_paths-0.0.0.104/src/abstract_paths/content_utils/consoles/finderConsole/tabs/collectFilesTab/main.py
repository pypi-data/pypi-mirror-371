from ..imports import *
from .initFuncs import initFuncs
# New Tab: Directory Map
class collectFilesTab(QWidget):
    def __init__(self, bus: SharedStateBus):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()
        install_common_inputs(
            self, grid, bus=bus,
            primary_btn=("Collect Files", self.start_collect),
            secondary_btn=("Open all files in VS Code", self.open_all_hits),
        )

        # Layout form

        # Output area
  
        self.layout().addWidget(QLabel("Results"))
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.open_all_hits)
        self.layout().addWidget(self.list, stretch=3)
        self._last_results = []

collectFilesTab = initFuncs(collectFilesTab)
