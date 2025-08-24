from ..imports import *
from .initFuncs import initFuncs
from PyQt6.QtWidgets import (
    QVBoxLayout, QGridLayout, QLabel, QTextEdit, QPushButton,
    QWidget, QSplitter,QTreeWidget, QHeaderView
)
from PyQt6.QtCore import Qt

class diffParserTab(QWidget):
    def __init__(self, bus: SharedStateBus):
        super().__init__()

        # --- top-level layout
        root = QVBoxLayout()
        self.setLayout(root)

        # --- common inputs (your existing helper populates self.* fields)
        grid = QGridLayout()
        install_common_inputs(
            self, grid, bus=bus,
            default_dir_in='/home/computron/Documents/pythonTools/modules/abstract_paths/src/abstract_paths/content_utils/consoles/finderConsole/tabs/editTab',
            primary_btn=("Parse and Preview", self.preview_patch),
            secondary_btn=("Preview:", self.save_patch),
            default_allowed_exts_in=['py']
        )
            # right: preview
        # right: preview
        output = QWidget()
        root.addWidget(QLabel("Preview:"))
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        root.addWidget(self.output, stretch=1)
        
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
        # if install_common_inputs doesn't insert 'grid' itself, you can add:
        # root.addLayout(grid)
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

        # --- actions
        btn_save = QPushButton("Approve and Save")
        btn_save.clicked.connect(self.save_patch)
        root.addWidget(btn_save)

        btn_test = QPushButton("test")
        btn_test.clicked.connect(self.output_test)
        root.addWidget(btn_test)        
       
        # --- status line (ADD THIS)
        self.status_label = QLabel("Ready.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setStyleSheet("color: #4caf50; padding: 4px 0;")  # green
        root.addWidget(self.status_label)

        # --- log hookup (you already had these)

diffParserTab = initFuncs(diffParserTab)
