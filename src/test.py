import unittest
from .modules.utils import (
    extract_imported_package,
    extract_from_normal_chunk,
    extract_from_chunk_contains_comma,
    extract_from_chunk
)

class UtilitiesTest(unittest.TestCase):
    def test_extract_from_normal_chunk(self):
        self.assertEqual(extract_from_normal_chunk('x0'), 'x0')
        self.assertEqual(extract_from_normal_chunk('x0.y0'), 'x0')
        self.assertEqual(extract_from_normal_chunk('x0.y0.z0'), 'x0')

    def test_extract_from_chunk_contains_comma(self):
        self.assertEqual(extract_from_chunk_contains_comma('x0,x1'), {'x0', 'x1'})
        self.assertEqual(extract_from_chunk_contains_comma('x0,x1,x2,\\'), {'x0', 'x1', 'x2'})
        self.assertEqual(extract_from_chunk_contains_comma('x0,x1,x2,'), {'x0', 'x1', 'x2'})
        self.assertEqual(extract_from_chunk_contains_comma('x0,x1.y1,x2,\\'), {'x0', 'x1', 'x2'})

    def test_extract_from_chunk(self):
        self.assertEqual(extract_from_chunk('x0'), (False, {'x0'}))
        self.assertEqual(extract_from_chunk(','), (False, set()))
        self.assertEqual(extract_from_chunk('x0.y0'), (False, {'x0'}))
        self.assertEqual(extract_from_chunk('x0.y0,'), (False, {'x0'}))
        self.assertEqual(extract_from_chunk('x0.y0,\\'), (True, {'x0'}))

    def test_extract_imported_packages(self):
        self.assertEqual(extract_imported_package('import pandas as pd'), (False, {'pandas'}))
        self.assertEqual(extract_imported_package('import os, sys'), (False, {'sys', 'os'}))
        self.assertEqual(extract_imported_package('import re'), (False, {'re'}))
        self.assertEqual(extract_imported_package('#import plotly.graph_objs as go'), (False, set()))
        self.assertEqual(extract_imported_package('    import plotly.graph_objs as go'), (False, {'plotly'}))
        pass
        # self.assertEqual(extract_imported_package('from os import (O_EXXCL as excl, O_RDONLY as rdonly)'), {'os'})

    def test_extract_imported_functions(self):
        pass

if __name__ == '__main__':
    unittest.main()
