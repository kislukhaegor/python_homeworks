import os
from unittest import TestCase
from dir_dict import DirDict
from functools import reduce

class DirDictTests(TestCase):
    def setUp(self):
        self.dir = "./tmp"
        self.dir_dict = DirDict(self.dir)

    def tearDown(self):
        for file in os.listdir(path=self.dir):
            os.remove(os.path.join(self.dir, file))

    def get_path(self, path):
        return os.path.join(self.dir, path)

    def test_set_item(self):
        self.dir_dict['file'] = 'Python\n'
        with open(self.get_path('file'), 'r') as f:
            lines = reduce(lambda a, b: a + b, f.readlines())
        self.assertEqual(lines, 'Python\n')

    def test_set_item_advanced(self):
        self.dir_dict['file'] = None
        with open(self.get_path('file'), 'r') as f:
            lines = reduce(lambda a, b: a + b, f.readlines())
        self.assertEqual(lines, str(None))

    def get_item_base(self):
        self.dir_dict['file'] = 'hello\n'
        self.assertEqual('hello\n', self.dir_dict['file'])

    def get_item_advanced(self):
        self.dir_dict['file'] = 'hello\n'
        with open(self.get_path('file'), 'a') as f:
            f.write('qwe\n')
        self.assertEqual('hello\nqwe\n', self.dir_dict['file'])
        with self.asserRaises(KeyError):
            a = self.dir_dict['qwe']
    
    def test_contain(self):
        self.dir_dict['file'] = None
        self.assertTrue('file' in self.dir_dict)
        self.assertFalse('file1' in self.dir_dict)

    def test_del_item(self):
        self.dir_dict['file1'] = None
        self.dir_dict['file2'] = None
        del self.dir_dict['file2']
        self.assertFalse(os.path.exists(self.get_path('file2')))

    def test_del_item_advanced(self):
        self.dir_dict['file1'] = None
        self.dir_dict['file2'] = None
        os.remove(self.get_path('file2'))
        with self.assertRaises(KeyError):
            del self.dir_dict['file2']

    def test_len(self):
        self.dir_dict['file'] = "qweqw"
        self.dir_dict['qwq'] = 'alsd'
        self.dir_dict['wwww'] = 'czx'
        self.assertEqual(len(self.dir_dict), 3)
        del self.dir_dict['file']
        self.assertEqual(len(self.dir_dict), 2)
        os.remove(self.get_path('qwq'))
        self.assertEqual(len(self.dir_dict), 1)

    def test_clear(self):
        self.dir_dict['file1'] = None
        self.dir_dict['file2'] = None
        self.dir_dict['file3'] = 'qw'
        self.dir_dict.clear()
        self.assertEqual(len(self.dir_dict), 0)

    def test_keys_base(self):
        self.dir_dict['file1'] = 'a'
        self.dir_dict['file2'] = 'b'
        self.dir_dict['file3'] = 'c'
        self.assertEqual({'file1', 'file2', 'file3'}, set(self.dir_dict.keys()))

    def test_keys_advanced(self):
        with open(self.get_path('file1'), 'w') as f:
            f.write('a')
        with open(self.get_path('file2'), 'w') as f:
            f.write('b')
        with open(self.get_path('file3'), 'w') as f:
            f.write('c')
        self.assertEqual({'file1', 'file2', 'file3'}, set(self.dir_dict.keys()))

    def test_values_base(self):
        self.dir_dict['file1'] = 'a'
        self.dir_dict['file2'] = 'b'
        self.dir_dict['file3'] = 'c'
        self.assertEqual({'a', 'b', 'c'}, set(self.dir_dict.values()))

    def test_values_advanced(self):
        with open(self.get_path('file1'), 'w') as f:
            f.write('a')
        with open(self.get_path('file2'), 'w') as f:
            f.write('b')
        with open(self.get_path('file3'), 'w') as f:
            f.write('c')
        self.assertEqual({'a', 'b', 'c'}, set(self.dir_dict.values()))

    def test_items_base(self):
        self.dir_dict['file1'] = 'a'
        self.dir_dict['file2'] = 'b'
        self.dir_dict['file3'] = 'c'
        self.assertEqual({('file1', 'a'), ('file2', 'b'), ('file3', 'c')}, set(self.dir_dict.items()))

    def test_items_advanced(self):
        with open(self.get_path('file1'), 'w') as f:
            f.write('a')
        with open(self.get_path('file2'), 'w') as f:
            f.write('b')
        with open(self.get_path('file3'), 'w') as f:
            f.write('c')
        self.assertEqual({('file1', 'a'), ('file2', 'b'), ('file3', 'c')}, set(self.dir_dict.items()))

    def test_get(self):
        self.assertEqual(None, self.dir_dict.get('file1'))
        self.dir_dict['file1'] = 'qwe'
        self.assertEqual('qwe', self.dir_dict.get('file1'))

    def popTest(self):
        self.assertEqual(str(None), self.dir_dict.pop('file'))
        self.dir_dict['file'] = 'qwe'
        self.assertEqual('qwe', self.dir_dict.pop('file'))
        self.assertFalse('file' in self.dir_dict)

    def test_setdefault(self):
        self.assertEqual(None, self.dir_dict.setdefault('file'))
        self.dir_dict['file'] = 'qwe'
        self.assertEqual('qwe', self.dir_dict.pop('file'))
