from collections.abc import MutableMapping
import os

class DirDict():
    __slots__ = '_dir'
    def __init__(self, dir):
        if not os.path.exists(dir):
            os.mkdir(dir)
        elif not os.path.isdir(dir):
            raise TypeError(f'{dir} is not a directory')
        self._dir = dir

    def _get_path(self, path):
        return os.path.join(self._dir, path)


    def __getitem__(self, key):
        path = self._get_path(key)
        if not os.path.exists(path):
            raise KeyError(path)
        with open('path', 'r') as f:
            return " ".join(f.readlines())

    def __setitem__(self, key, item):
        path = self._get_path(key)
        with open(path, "w") as f:
            f.write(str(item))

    def __delitem__(self, key):
        path = self._get_path(key)
        if not os.path.exists(path):
            raise KeyError(path)
        
        if not os.path.isfile(path):
            TypeError(f"{path} is not a file")
        
        os.remove(path)


    def __iter__(self):
        return (key for key in os.listdir(path=self._dir))


    def __len__(self):
        return len(os.listdir(path=self._dir))


    def keys(self):
        return list(filter(os.path.isfile, os.listdir(path=self._dir)))
    
    def __contains__(self, key):
        return key in self.keys()

    def items(self):
        return [self[key] for key in self]

    def clear(self):
        for key in self.keys:
            os.remove(key)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

