import tempfile
import uuid
import os
import shutil

class TemporaryFileManager(tempfile.TemporaryDirectory):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        if not hasattr(self, '_initialized'):  # Prevent re-initialization
            self.files = {}
            self._initialized = True

    def load(self, src: bytes | str) -> str:
        fp = os.path.join(self.name, str(uuid.uuid4()))
        if isinstance(src, bytes):
            with open(fp, 'wb') as f:
                f.write(src)
        else:
            shutil.copy(src, fp)
        return fp

    def make_fp(self) -> str:
        return os.path.join(self.name, str(uuid.uuid4()))

    def get(self, fp: str) -> bytes:
        with open(fp, 'rb') as f:
            return f.read()

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc, value, tb):
        return super().__exit__(exc, value, tb)
