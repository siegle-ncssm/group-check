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


def print_report(conflicts: List[dict], proposed_groups: List[List[str]]) -> None:
    """
    Print a detailed report of conflicts.

    Args:
        conflicts: List of conflicts found
        proposed_groups: List of proposed groups
    """
    if not conflicts:
        print("✓ No conflicts found! All proposed groups have novel member combinations.")
        return

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

        # Check for conflicts
        checker = GroupChecker(previous_groups)
        conflicts = checker.check_proposed_groups(proposed_groups)

        # Output results
        if args.json:
            result = {
                'has_conflicts': len(conflicts) > 0,
                'num_conflicts': len(conflicts),
                'conflicts': conflicts
            }
            print(json.dumps(result, indent=2))
        else:
            print_report(conflicts, proposed_groups)

        # Exit with appropriate code
        sys.exit(1 if conflicts else 0)

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
