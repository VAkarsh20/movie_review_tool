import unittest

from utils.date_utils import change_date_format, get_review_date

# Command to run: python3 -m unittest tests/date_utils_test.py
class TestDateUtils(unittest.TestCase):
    def test_get_review_date__returns_intended(self):
        month, day, year = get_review_date().split("/")

        self.assertEqual(len(month), 2)
        self.assertEqual(len(day), 2)
        self.assertEqual(len(year), 4)

    def test_change_date_format__correct_format__returns_intended(self):
        self.assertEqual(change_date_format("12/25/1985"), "1985-12-25")
        

if __name__ == '__main__':
    unittest.main()
