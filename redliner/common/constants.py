from PyQt6 import QtCore as qtc
import numpy as np
import re

from redliner.common.common import resource_path

PREVIEW_DPI = 10
PREVIEW_SIZE = qtc.QSize(128, 128)
GRAYSCALE_WEIGHTS = np.array([0.2989, 0.5870, 0.1140])
VERSION_PATTERN = re.compile(r'\[(\d+\.\d+\.\d+)\]')
REMOTE_CHANGELOG = r"https://raw.githubusercontent.com/isomatter-labs/Redliner/refs/heads/main/CHANGELOG.md"
REMOTE = r"https://github.com/isomatter-labs/Redliner"


with open (resource_path("diff.frag")) as f:
    DIFF_FRAG = f.read()

with open(resource_path("diff.vert")) as f:
    DIFF_VERT = f.read()

with open(resource_path("bg.frag")) as f:
    BG_FRAG = f.read()

with open(resource_path("bg.vert")) as f:
    BG_VERT = f.read()