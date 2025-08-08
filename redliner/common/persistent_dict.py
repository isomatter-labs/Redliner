import copy
import json
import logging
import os


class PersistentDict(dict):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, path: os.PathLike | str = ""):
        if not hasattr(self, '_initialized'):  # Prevent re-initialization
            self.defaults = {}
            self.path = path
            try:
                with open(self.path, 'r') as f:
                    loaded = json.loads(f.read())
            except:
                logging.warning("no existing settings, resetting")
                loaded = {}
            try:
                for k, v in loaded.items():
                    self.__setitem__(k, v, True)
            except:
                logging.warning("corrupted settings, resetting")
                self.clear()
            self._initialized = True

    def default(self, k: str, v):
        self.defaults[k] = v
        if k not in self:
            self[k] = v

    def set(self, k: str, v):
        self[k] = v

    def commit(self):
        os.makedirs(os.path.split(self.path)[0], exist_ok=True)
        with open(self.path, 'w') as f:
            f.write(json.dumps(self, indent=2))

    def reset(self, key:str|None=None):
        if key is None:
            self.update(self.defaults)
        else:
            self[key] = self.defaults[key]

    def clear(self):
        self.reset()

    def __setitem__(self, key, value, inhibit_commit=False):
        ret = super().__setitem__(key, copy.deepcopy(value))
        if not inhibit_commit:
            self.commit()
        return ret

    def update(self, other):
        for k, v in other.items():
            self.__setitem__(k, v, True)
        self.commit()
