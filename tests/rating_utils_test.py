import unittest

from utils.rating_utils import *
from parameterized import parameterized

# Command to run: python3 -m unittest tests/rating_utils_test.py
class TestRatingUtils(unittest.TestCase):
    # Stars
    def test_rating_to_stars__outside_range__raises_error(self):
        with self.assertRaises(ValueError):
            rating_to_stars(10.0)

    @parameterized.expand([
        ["largest score", 9.9, 5],
        ["5 stars", 9.5, 5],
        ["4.5 stars", 9.0, 4.5],
        ["4 stars", 8.0, 4],
        ["3.5 stars", 7.0, 3.5],
        ["3 stars", 6.0, 3],
        ["2.5 stars", 5.0, 2.5],
        ["2 stars", 4.0, 2],
        ["1.5 stars", 3.0, 1.5],
        ["1 stars", 2.0, 1],
        ["0.5 stars", 1.0, 0.5],
        ["0 stars", 0.9, 0],
    ])
    def test_rating_to_stars__correct_mapping(self, name, rating, stars):
        self.assertEqual(rating_to_stars(rating), stars, name)

    # IMDb score
    def test_rating_to_imdb_score__outside_range__raises_error(self):
        with self.assertRaises(ValueError):
            rating_to_imdb_score(10.0)

    @parameterized.expand([
        ["largest score", 9.9, 10],
        ["10", 9.5, 10],
        ["9", 9.0, 9],
        ["8", 8.0, 8],
        ["7", 7.0, 7],
        ["6", 6.0, 6],
        ["5", 5.0, 5],
        ["4", 4.0, 4],
        ["3", 3.0, 3],
        ["2", 2.0, 2],
        ["1", 1.0, 1],
        ["0", 0.9, 0],
    ])
    def test_rating_to_imdb_score__correct_mapping(self, name, rating, imdb_score):
        self.assertEqual(rating_to_imdb_score(rating), imdb_score, name)

    # Tags
    def test_rating_to_tag__outside_range__raises_error(self):
        with self.assertRaises(ValueError):
            rating_to_tag(10.0)

    @parameterized.expand([
        ["largest score", 9.9, "Brilliant"],
        ["Brilliant", 9.7, "Brilliant"],
        ["Incredible", 9.5, "Incredible"],
        ["Great", 9.0, "Great"],
        ["Very Good", 8.5, "Very Good"],
        ["Good", 8.0, "Good"],
        ["Pretty Good", 7.0, "Pretty Good"],
        ["Decent", 6.0, "Decent"],
        ["Pretty Bad", 5.0, "Pretty Bad"],
        ["Bad", 4.0, "Bad"],
        ["Very Bad", 3.0, "Very Bad"],
        ["Terrible", 2.0, "Terrible"],
        ["Terrible", 1.0, "Terrible"],
        ["Terrible", 0.9, "Terrible"],
    ])
    def test_rating_to_tag__correct_mapping(self, name, rating, tag):
        self.assertEqual(rating_to_tag(rating), tag, name)

if __name__ == '__main__':
    unittest.main()