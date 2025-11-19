#!/usr/bin/env python3
"""
Student Group Conflict Checker

This utility checks if any members of proposed student groups have previously
been in a group together, which may violate group formation rules.
"""

import json
import sys
from itertools import combinations
from typing import List, Set, Tuple
from pathlib import Path
import argparse


class GroupChecker:
    """Handles checking for conflicts between previous and proposed student groups."""

    def __init__(self, previous_groups: List[List[str]]):
        """
        Initialize the group checker with previous groups.

        Args:
            previous_groups: List of previous groups, where each group is a list of student names
        """
        self.previous_groups = previous_groups
        self.previous_pairs = self._build_pair_set(previous_groups)
        self.previous_students = self._get_all_students(previous_groups)

    def _build_pair_set(self, groups: List[List[str]]) -> Set[Tuple[str, str]]:
        """
        Build a set of all student pairs from groups.

        Args:
            groups: List of groups

        Returns:
            Set of tuples representing student pairs (normalized to alphabetical order)
        """
        pairs = set()
        for group in groups:
            # Generate all pairs of students in this group
            for student1, student2 in combinations(group, 2):
                # Normalize pair order (alphabetically) for consistent comparison
                pair = tuple(sorted([student1, student2]))
                pairs.add(pair)
        return pairs

    def _get_all_students(self, groups: List[List[str]]) -> Set[str]:
        """
        Get all unique student names from groups.

        Args:
            groups: List of groups

        Returns:
            Set of all unique student names
        """
        students = set()
        for group in groups:
            students.update(group)
        return students

    def check_proposed_groups(self, proposed_groups: List[List[str]]) -> List[dict]:
        """
        Check proposed groups for conflicts with previous groups.

        Args:
            proposed_groups: List of proposed groups to check

        Returns:
            List of conflict dictionaries containing group index and conflicting pairs
        """
        conflicts = []

        for group_idx, group in enumerate(proposed_groups):
            group_conflicts = []

            # Check all pairs in this proposed group
            for student1, student2 in combinations(group, 2):
                pair = tuple(sorted([student1, student2]))
                if pair in self.previous_pairs:
                    group_conflicts.append({
                        'students': [student1, student2],
                        'pair': pair
                    })

            if group_conflicts:
                conflicts.append({
                    'group_index': group_idx,
                    'group_members': group,
                    'conflicts': group_conflicts
                })

        return conflicts

    def find_missing_students(self, proposed_groups: List[List[str]]) -> List[str]:
        """
        Find students from previous groups who are not in any proposed group.

        Args:
            proposed_groups: List of proposed groups to check

        Returns:
            Sorted list of student names that appear in previous but not proposed groups
        """
        proposed_students = self._get_all_students(proposed_groups)
        missing = self.previous_students - proposed_students
        return sorted(missing)


def load_groups_from_file(filepath: str) -> List[List[str]]:
    """
    Load groups from a JSON file.

    Args:
        filepath: Path to the JSON file containing groups

    Returns:
        List of groups

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
        ValueError: If the JSON structure is invalid
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(path, 'r') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Expected a list of groups in {filepath}")

    for i, group in enumerate(data):
        if not isinstance(group, list):
            raise ValueError(f"Group {i} in {filepath} is not a list")
        if not all(isinstance(member, str) for member in group):
            raise ValueError(f"All group members in {filepath} must be strings")

    return data


def print_report(conflicts: List[dict], missing_students: List[str]) -> None:
    """
    Print a detailed report of conflicts and missing students.

    Args:
        conflicts: List of conflicts found
        missing_students: List of students from previous groups not in proposed groups
    """
    has_issues = conflicts or missing_students

    if not has_issues:
        print("✓ No conflicts found! All proposed groups have novel member combinations.")
        print("✓ All students from previous groups are included in proposed groups.")
        return

    if conflicts:
        print(f"✗ Found conflicts in {len(conflicts)} proposed group(s):\n")

        for conflict in conflicts:
            group_idx = conflict['group_index']
            group_members = conflict['group_members']

            print(f"Group {group_idx + 1}: {group_members}")
            print(f"  Conflicts:")

            for conf in conflict['conflicts']:
                student1, student2 = conf['students']
                print(f"    - {student1} and {student2} have previously been in a group together")

            print()

    if missing_students:
        print(f"⚠ Warning: {len(missing_students)} student(s) from previous groups are missing from proposed groups:\n")
        for student in missing_students:
            print(f"  - {student}")
        print()


def main():
    """Main entry point for the CLI utility."""
    parser = argparse.ArgumentParser(
        description='Check if proposed student groups contain members who have previously worked together.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s previous_groups.json proposed_groups.json
  %(prog)s -v data/previous.json data/proposed.json

Input file format (JSON):
  [
    ["Alice", "Bob", "Charlie"],
    ["David", "Eve", "Frank"],
    ...
  ]
        """
    )

    parser.add_argument(
        'previous_groups',
        help='Path to JSON file containing previous student groups'
    )

    parser.add_argument(
        'proposed_groups',
        help='Path to JSON file containing proposed student groups'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )

    args = parser.parse_args()

    try:
        # Load groups from files
        if args.verbose:
            print(f"Loading previous groups from: {args.previous_groups}")
        previous_groups = load_groups_from_file(args.previous_groups)

        if args.verbose:
            print(f"Loading proposed groups from: {args.proposed_groups}")
        proposed_groups = load_groups_from_file(args.proposed_groups)

        if args.verbose:
            print(f"Loaded {len(previous_groups)} previous group(s)")
            print(f"Loaded {len(proposed_groups)} proposed group(s)")
            print()

        # Check for conflicts and missing students
        checker = GroupChecker(previous_groups)
        conflicts = checker.check_proposed_groups(proposed_groups)
        missing_students = checker.find_missing_students(proposed_groups)

        # Output results
        if args.json:
            result = {
                'has_conflicts': len(conflicts) > 0,
                'num_conflicts': len(conflicts),
                'conflicts': conflicts,
                'missing_students': missing_students,
                'num_missing': len(missing_students)
            }
            print(json.dumps(result, indent=2))
        else:
            print_report(conflicts, missing_students)

        # Exit with appropriate code
        sys.exit(1 if (conflicts or missing_students) else 0)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file - {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
