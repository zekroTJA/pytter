import os
import urllib
import mimetypes


class FileInfo:
    handler        = None
    size: int      = None
    mime_type: str = None
    file_name: str = None
    full_path: str = None
    from_url: bool = False

    def __init__(self, file_handler, full_media_path: str):
        self.handler = file_handler

        if full_media_path.startswith('http'):
            self.from_url = True
            self.full_path = urllib.parse.urlparse(full_media_path).path
        else:
            self.full_path = full_media_path
        self.file_name = os.path.basename(self.full_path)

        file_handler.seek(0, 2)
        self.size = file_handler.tell()
        try:
            file_handler.seek(0)
        except:
            pass

        self.mime_type = mimetypes.guess_type(self.file_name)[0]

    def close(self):
        self.handler.close()


class FileChunk:
    size: int = 0
    data = []
    index: int = 0

    def __init__(self, size: int, index: int, data):
        self.size = size
        self.index = index
        self.data = data


class Megabyte:
    _n: float = 0

    def __init__(self, n: float):
        self._n = n

    def __str__(self):
        return str(self._n)

    @property
    def n_bytes(self) -> int:
        return self._n * 1024 * 1024