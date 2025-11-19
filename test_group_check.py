#!/usr/bin/env python3
"""
Unit tests for the Student Group Conflict Checker
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from group_check import GroupChecker, load_groups_from_file


class TestGroupChecker(unittest.TestCase):
    """Test cases for the GroupChecker class."""

    def test_no_conflicts(self):
        """Test case where there are no conflicts."""
        previous_groups = [
            ["Alice", "Bob", "Charlie"],
            ["David", "Eve", "Frank"]
        ]
        proposed_groups = [
            ["Alice", "David", "Grace"],
            ["Bob", "Eve", "Henry"]
        ]

        checker = GroupChecker(previous_groups)
        conflicts = checker.check_proposed_groups(proposed_groups)

        self.assertEqual(len(conflicts), 0)

    def test_single_conflict(self):
        """Test case with a single conflict."""
        previous_groups = [
            ["Alice", "Bob", "Charlie"]
        ]
        proposed_groups = [
            ["Alice", "Bob", "David"]
        ]

        checker = GroupChecker(previous_groups)
        conflicts = checker.check_proposed_groups(proposed_groups)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]['group_index'], 0)
        self.assertEqual(len(conflicts[0]['conflicts']), 1)
        self.assertIn('Alice', conflicts[0]['conflicts'][0]['students'])
        self.assertIn('Bob', conflicts[0]['conflicts'][0]['students'])

    def test_multiple_conflicts_in_one_group(self):
        """Test case with multiple conflicts in a single proposed group."""
        previous_groups = [
            ["Alice", "Bob", "Charlie"],
            ["Alice", "David", "Eve"]
        ]
        proposed_groups = [
            ["Alice", "Bob", "David"]  # Alice-Bob and Alice-David both conflict
        ]

        checker = GroupChecker(previous_groups)
        conflicts = checker.check_proposed_groups(proposed_groups)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(len(conflicts[0]['conflicts']), 2)

    def test_multiple_groups_with_conflicts(self):
        """Test case with conflicts in multiple proposed groups."""
        previous_groups = [
            ["Alice", "Bob"],
            ["Charlie", "David"]
        ]
        proposed_groups = [
            ["Alice", "Bob", "Eve"],
            ["Charlie", "David", "Frank"]
        ]

        checker = GroupChecker(previous_groups)
        conflicts = checker.check_proposed_groups(proposed_groups)

        self.assertEqual(len(conflicts), 2)

    def test_case_sensitive_names(self):
        """Test that student names are case-sensitive."""
        previous_groups = [
            ["Alice", "Bob"]
        ]
        proposed_groups = [
            ["alice", "bob"]  # Different case, should not conflict
        ]

        checker = GroupChecker(previous_groups)
        conflicts = checker.check_proposed_groups(proposed_groups)

        self.assertEqual(len(conflicts), 0)

    def test_empty_previous_groups(self):
        """Test with no previous groups."""
        previous_groups = []
        proposed_groups = [
            ["Alice", "Bob", "Charlie"]
        ]

        checker = GroupChecker(previous_groups)
        conflicts = checker.check_proposed_groups(proposed_groups)

        self.assertEqual(len(conflicts), 0)

    def test_empty_proposed_groups(self):
        """Test with no proposed groups."""
        previous_groups = [
            ["Alice", "Bob", "Charlie"]
        ]
        proposed_groups = []

        checker = GroupChecker(previous_groups)
        conflicts = checker.check_proposed_groups(proposed_groups)

        self.assertEqual(len(conflicts), 0)

    def test_large_groups(self):
        """Test with larger groups."""
        previous_groups = [
            ["Alice", "Bob", "Charlie", "David", "Eve"]
        ]
        proposed_groups = [
            ["Alice", "Frank", "Grace"],  # No conflict
            ["Bob", "Charlie", "Henry"]   # Conflict: Bob-Charlie
        ]

        checker = GroupChecker(previous_groups)
        conflicts = checker.check_proposed_groups(proposed_groups)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]['group_index'], 1)

    def test_pair_normalization(self):
        """Test that pairs are normalized (order doesn't matter)."""
        previous_groups = [
            ["Alice", "Bob"]
        ]
        proposed_groups = [
            ["Bob", "Alice"]  # Same pair, different order
        ]

        checker = GroupChecker(previous_groups)
        conflicts = checker.check_proposed_groups(proposed_groups)

        self.assertEqual(len(conflicts), 1)


class TestLoadGroupsFromFile(unittest.TestCase):
    """Test cases for loading groups from JSON files."""

    def setUp(self):
        """Create a temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        for file in Path(self.temp_dir).glob('*'):
            file.unlink()
        os.rmdir(self.temp_dir)

    def test_load_valid_file(self):
        """Test loading a valid JSON file."""
        data = [
            ["Alice", "Bob", "Charlie"],
            ["David", "Eve", "Frank"]
        ]
        filepath = os.path.join(self.temp_dir, 'test.json')

        with open(filepath, 'w') as f:
            json.dump(data, f)

        groups = load_groups_from_file(filepath)
        self.assertEqual(groups, data)

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        filepath = os.path.join(self.temp_dir, 'nonexistent.json')

        with self.assertRaises(FileNotFoundError):
            load_groups_from_file(filepath)

    def test_load_invalid_json(self):
        """Test loading a file with invalid JSON."""
        filepath = os.path.join(self.temp_dir, 'invalid.json')

        with open(filepath, 'w') as f:
            f.write("{ invalid json }")

        with self.assertRaises(json.JSONDecodeError):
            load_groups_from_file(filepath)

    def test_load_wrong_structure_not_list(self):
        """Test loading a file with wrong structure (not a list)."""
        data = {"groups": [["Alice", "Bob"]]}
        filepath = os.path.join(self.temp_dir, 'wrong.json')

        with open(filepath, 'w') as f:
            json.dump(data, f)

        with self.assertRaises(ValueError):
            load_groups_from_file(filepath)

    def test_load_wrong_structure_group_not_list(self):
        """Test loading a file where a group is not a list."""
        data = [
            ["Alice", "Bob"],
            "Invalid Group"
        ]
        filepath = os.path.join(self.temp_dir, 'wrong.json')

        with open(filepath, 'w') as f:
            json.dump(data, f)

        with self.assertRaises(ValueError):
            load_groups_from_file(filepath)

    def test_load_wrong_structure_non_string_members(self):
        """Test loading a file with non-string group members."""
        data = [
            ["Alice", "Bob"],
            [1, 2, 3]  # Numbers instead of strings
        ]
        filepath = os.path.join(self.temp_dir, 'wrong.json')

        with open(filepath, 'w') as f:
            json.dump(data, f)

        with self.assertRaises(ValueError):
            load_groups_from_file(filepath)


class TestMissingStudents(unittest.TestCase):
    """Test cases for finding missing students."""

    def test_no_missing_students(self):
        """Test when all previous students are in proposed groups."""
        previous_groups = [
            ["Alice", "Bob", "Charlie"]
        ]
        proposed_groups = [
            ["Alice", "David"],
            ["Bob", "Eve"],
            ["Charlie", "Frank"]
        ]

        checker = GroupChecker(previous_groups)
        missing = checker.find_missing_students(proposed_groups)

        self.assertEqual(len(missing), 0)

    def test_some_missing_students(self):
        """Test when some students are missing."""
        previous_groups = [
            ["Alice", "Bob", "Charlie"],
            ["David", "Eve", "Frank"]
        ]
        proposed_groups = [
            ["Alice", "Grace"],
            ["David", "Henry"]
        ]

        checker = GroupChecker(previous_groups)
        missing = checker.find_missing_students(proposed_groups)

        self.assertEqual(len(missing), 4)
        self.assertIn("Bob", missing)
        self.assertIn("Charlie", missing)
        self.assertIn("Eve", missing)
        self.assertIn("Frank", missing)

    def test_all_students_missing(self):
        """Test when all previous students are missing."""
        previous_groups = [
            ["Alice", "Bob", "Charlie"]
        ]
        proposed_groups = [
            ["David", "Eve", "Frank"]
        ]

        checker = GroupChecker(previous_groups)
        missing = checker.find_missing_students(proposed_groups)

        self.assertEqual(len(missing), 3)
        self.assertIn("Alice", missing)
        self.assertIn("Bob", missing)
        self.assertIn("Charlie", missing)

    def test_missing_students_sorted(self):
        """Test that missing students are returned sorted."""
        previous_groups = [
            ["Zoe", "Alice", "Mike"]
        ]
        proposed_groups = [
            ["David", "Eve"]
        ]

        checker = GroupChecker(previous_groups)
        missing = checker.find_missing_students(proposed_groups)

        self.assertEqual(missing, ["Alice", "Mike", "Zoe"])

    def test_empty_proposed_groups_all_missing(self):
        """Test with empty proposed groups."""
        previous_groups = [
            ["Alice", "Bob"]
        ]
        proposed_groups = []

        checker = GroupChecker(previous_groups)
        missing = checker.find_missing_students(proposed_groups)

        self.assertEqual(len(missing), 2)

    def test_case_sensitive_missing(self):
        """Test that case sensitivity applies to missing students."""
        previous_groups = [
            ["Alice", "Bob"]
        ]
        proposed_groups = [
            ["alice", "bob"]  # Different case
        ]

        checker = GroupChecker(previous_groups)
        missing = checker.find_missing_students(proposed_groups)

        # Alice and Bob should be missing because alice and bob are different
        self.assertEqual(len(missing), 2)
        self.assertIn("Alice", missing)
        self.assertIn("Bob", missing)


if __name__ == '__main__':
    unittest.main()
