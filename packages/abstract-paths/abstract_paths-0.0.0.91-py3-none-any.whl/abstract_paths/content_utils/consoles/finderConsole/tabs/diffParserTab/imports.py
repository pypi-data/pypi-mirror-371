from ..imports import *
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Union, Set
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt
import os
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)
