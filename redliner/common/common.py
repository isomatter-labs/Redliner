import sys
import os

def resource_path(relative_path, subdir=['res']):
    subdir = subdir or []
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, *subdir, relative_path)
    return os.path.abspath(os.path.join(*subdir, relative_path))
