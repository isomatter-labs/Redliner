
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'res', relative_path)
    return os.path.abspath(os.path.join("..", 'res', relative_path))
