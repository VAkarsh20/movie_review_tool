import unittest
from utils.proofread_utils import *

# Command to run: python3 -m unittest tests/proofread_utils_test.py
class TestProofreadUtils(unittest.TestCase):
    # wait
    def test_wait__below_limit__return_false(self):
        self.assertFalse(wait(counter = 14, request_batch = 1))
    
    def test_wait__at_limit__return_false(self):
        self.assertFalse(wait(counter = 30, request_batch = 2))

    def test_wait__above_limit__return_true(self):
        self.assertTrue(wait(counter = 31, request_batch = 2, sleep_time = 0))

    # proofread_comments
    def test_proofread_comments__correctly_proofreads(self):
        model = create_model()
        comments = "There is a doog; caats r smool; I are funny"

        comments = proofread_comments(comments, model)
        self.assertEqual(comments.count(';'), 2)
        self.assertTrue(comments[-1].isalnum())


if __name__ == '__main__':
    unittest.main()