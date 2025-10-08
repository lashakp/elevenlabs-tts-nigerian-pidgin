# tests/test_pidgin.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from utils.pidgin import stylize_pidgin

class TestPidginConverter(unittest.TestCase):
    def test_basic_replacement(self):
        text = "I cannot understand"
        expected = "I no fit understand"
        self.assertEqual(stylize_pidgin(text), expected)

    def test_case_insensitive(self):
        text = "I CANNOT UNDERSTAND good friend"
        expected = "I NO FIT UNDERSTAND beta padi"
        self.assertEqual(stylize_pidgin(text), expected)

    def test_custom_replacement(self):
        text = "hello world"
        custom = [("hello", "wetin dey")]
        expected = "wetin dey world"
        self.assertEqual(stylize_pidgin(text, custom), expected)

    def test_uppercase_replacement(self):
        text = "I CANNOT UNDERSTAND"
        expected = "I NO FIT UNDERSTAND"
        self.assertEqual(stylize_pidgin(text), expected)

if __name__ == "__main__":
    unittest.main()