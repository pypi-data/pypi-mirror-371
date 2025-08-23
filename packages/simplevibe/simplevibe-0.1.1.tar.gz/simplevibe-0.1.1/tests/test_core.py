"""
Tests for the simpleVibe package core module.
"""

import unittest
from simplevibe import core


class TestSimpleVibeCore(unittest.TestCase):
    """Test cases for SimpleVibe core functionality."""
    
    def testOddVibes(self):
        """Test the oddVibes function"""
        self.assertEqual(core.oddVibes(3), True)
        self.assertEqual(core.oddVibes(4), False)

if __name__ == "__main__":
    unittest.main()
