import unittest

from utils.text_utils import get_filename

# Command to run: python3 -m unittest tests/text_utils_test.py
class TestTextUtils(unittest.TestCase):
    def test_get_filename__returns_intended(self):
        self.assertEqual(get_filename("Te?st/Mov:ie", 1985), "Test Movie (1985).textproto")

if __name__ == '__main__':
    unittest.main()