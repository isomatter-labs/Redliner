from PyQt6 import QtCore as qtc
import numpy as np
import re

PREVIEW_DPI = 10
PREVIEW_SIZE = qtc.QSize(128, 128)
GRAYSCALE_WEIGHTS = np.array([0.2989, 0.5870, 0.1140])
VERSION_PATTERN = re.compile(r'\[(\d+\.\d+\.\d+)\]')
REMOTE_CHANGELOG = r"https://raw.githubusercontent.com/CJett/Redliner/refs/heads/main/CHANGELOG.md"