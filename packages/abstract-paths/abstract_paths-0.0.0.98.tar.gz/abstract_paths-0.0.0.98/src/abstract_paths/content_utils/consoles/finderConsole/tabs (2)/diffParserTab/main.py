from ..imports import *
from .initFuncs import initFuncs
from PyQt6.QtWidgets import (
    QVBoxLayout, QGridLayout, QLabel, QTextEdit, QPushButton, QWidget,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QSplitter
)
from PyQt6.QtCore import Qt
 
class diffParserTab(QWidget):
    def __init__(self, bus: SharedStateBus):
        super().__init__()

        # top-level layout
        root = QVBoxLayout()
        self.setLayout(root)

        # common inputs (this will also add its CTA buttons wired to the callbacks you pass)
        grid = QGridLayout()
        install_common_inputs(
            self, grid, bus=bus,
            primary_btn=("Preview Diff", self.preview_patch),  # <-- method provided by initFuncs
            secondary_btn=("Save Diff", self.save_patch),      # <-- method provided by initFuncs
        )
        
        # discovered files (list above both panes)
        root.addWidget(QLabel("Files found:"))
        self.files_list = QTreeWidget()
        self.files_list.setColumnCount(3)
        self.files_list.setHeaderLabels(["File", "Apply", "Overwrite"])
        self.files_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.files_list.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.files_list.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.files_list.setRootIsDecorated(False)
        root.addWidget(self.files_list, stretch=1)

        # editors side-by-side via splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # left: diff editor
        left = QWidget()
        left_v = QVBoxLayout(left); left_v.setContentsMargins(0, 0, 0, 0)
        left_v.addWidget(QLabel("Diff:"))
        self.diff_text = QTextEdit()
        self.diff_text.setPlaceholderText("Paste the diff here...")
        left_v.addWidget(self.diff_text, stretch=1)

        # right: preview
        right = QWidget()
        right_v = QVBoxLayout(right); right_v.setContentsMargins(0, 0, 0, 0)
        right_v.addWidget(QLabel("Preview:"))
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        right_v.addWidget(self.preview, stretch=1)

        # add to splitter
        self.splitter.addWidget(left)
        self.splitter.addWidget(right)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        root.addWidget(self.splitter, stretch=3)

        # log hookup
        set_self_log(self)
        attach_functions(self, hot_reload=True)
        attach_textedit_to_logs(self.log, tail_file=get_log_file_path())

