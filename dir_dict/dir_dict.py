from functools import reduce

import os

class DirDict():
    __slots__ = ['_dir']

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
        with open(path, 'r') as f:
            return reduce(lambda a, b: a + b, f.readlines())

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
        return list(os.listdir(path=self._dir))
    
    def __contains__(self, key):
        return key in self.keys()

    def values(self):
        return [self[key] for key in self]

    def items(self):
        return list(zip(self.keys(), self.values()))

    def clear(self):
        for key in self.keys():
            os.remove(self._get_path(key))

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return str(default)

    def pop(self, key, default=None):
        if key not in self:
            return str(default)
        ret_val = self[key]
        del self[key]
        return ret_val

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self[key] = default
        return str(default)

    def update(self, other):
        for key, value in other:
            self[key] = value
