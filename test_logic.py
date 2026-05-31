
import unittest
from app import validate_seasons

class TestSeriesLogic(unittest.TestCase):
    def test_valid_seasons(self):
        self.assertTrue(validate_seasons(5))
        self.assertTrue(validate_seasons(0))

    def test_invalid_seasons(self):
        self.assertFalse(validate_seasons(-1))
        self.assertFalse(validate_seasons("abc"))

if __name__ == '__main__':
    unittest.main()