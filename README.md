# group-check

A command-line tool to verify that proposed student groups have novel member combinations by checking against previous group assignments.

## Purpose

This utility helps educators and group coordinators ensure that students are paired with new teammates in each group assignment. It checks if any members of proposed student groups have previously been in a group together.

## Features

- Validates proposed group assignments against historical group data
- Identifies all conflicts where students have previously worked together
- Detects students from previous groups who are missing from proposed groups
- Supports flexible JSON input format
- Provides clear, human-readable output
- Optional JSON output for programmatic use
- Comprehensive error handling and validation
- Exit codes for easy integration with scripts

## Installation

No installation required! This is a standalone Python script that uses only standard library modules.

Requirements:
- Python 3.6 or higher

## Usage

### Basic Usage

```bash
python3 group_check.py <previous_groups_file> <proposed_groups_file>
```

### Command-Line Options

```
positional arguments:
  previous_groups       Path to JSON file containing previous student groups
  proposed_groups       Path to JSON file containing proposed student groups

optional arguments:
  -h, --help           show help message and exit
  -v, --verbose        Enable verbose output
  --json               Output results in JSON format
```

### Examples

Check proposed groups against previous groups:
```bash
python3 group_check.py examples/previous_groups.json examples/proposed_groups_no_conflicts.json
```

Verbose output:
```bash
python3 group_check.py -v examples/previous_groups.json examples/proposed_groups_with_conflicts.json
```

JSON output for programmatic use:
```bash
python3 group_check.py --json examples/previous_groups.json examples/proposed_groups_with_conflicts.json
```

## Input File Format

Both input files should be JSON files containing a list of groups, where each group is a list of student names (strings).

Example:
```json
[
  ["Alice", "Bob", "Charlie"],
  ["David", "Eve", "Frank"],
  ["Grace", "Henry", "Iris"]
]
```

### Important Notes

- Student names are case-sensitive ("Alice" and "alice" are considered different students)
- Each group can have any number of members (2 or more)
- Student names should be consistent across all files

## Output

### Human-Readable Output (Default)

When no conflicts are found and all students are included:
```
✓ No conflicts found! All proposed groups have novel member combinations.
✓ All students from previous groups are included in proposed groups.
```

When conflicts are found:
```
✗ Found conflicts in 2 proposed group(s):

Group 1: ['Alice', 'Bob', 'Henry']
  Conflicts:
    - Alice and Bob have previously been in a group together

Group 2: ['Charlie', 'David', 'Frank']
  Conflicts:
    - Charlie and David have previously been in a group together

⚠ Warning: 2 student(s) from previous groups are missing from proposed groups:

  - Jack
  - Kelly

```

When students are missing but no conflicts:
```
⚠ Warning: 6 student(s) from previous groups are missing from proposed groups:

  - Bob
  - Charlie
  - David
  - Eve
  - Jack
  - Kelly

```

### JSON Output

Use the `--json` flag to get machine-readable output:
```json
{
  "has_conflicts": true,
  "num_conflicts": 2,
  "conflicts": [
    {
      "group_index": 0,
      "group_members": ["Alice", "Bob", "Henry"],
      "conflicts": [
        {
          "students": ["Alice", "Bob"],
          "pair": ["Alice", "Bob"]
        }
      ]
    }
  ],
  "missing_students": ["Jack", "Kelly"],
  "num_missing": 2
}
```

## Exit Codes

- `0`: No conflicts found and all previous students are in proposed groups
- `1`: Conflicts found or students are missing from proposed groups
- `2`: Error occurred (invalid input, file not found, etc.)

This makes it easy to use the tool in scripts:
```bash
if python3 group_check.py previous.json proposed.json; then
    echo "Groups approved!"
else
    echo "Groups have conflicts - please revise"
fi
```

## Testing

Run the test suite:
```bash
python3 test_group_check.py
```

Run tests with verbose output:
```bash
python3 test_group_check.py -v
```

## Examples

The `examples/` directory contains sample input files:

- `previous_groups.json` - Example of previous group assignments
- `proposed_groups_no_conflicts.json` - Proposed groups with no conflicts and all students included
- `proposed_groups_with_conflicts.json` - Proposed groups with conflicts and some missing students
- `proposed_groups_missing_students.json` - Proposed groups with no conflicts but several missing students

Try them out:
```bash
# No conflicts, all students included
python3 group_check.py examples/previous_groups.json examples/proposed_groups_no_conflicts.json

# With conflicts and missing students
python3 group_check.py examples/previous_groups.json examples/proposed_groups_with_conflicts.json

# No conflicts but missing students
python3 group_check.py examples/previous_groups.json examples/proposed_groups_missing_students.json
```

## How It Works

1. The tool reads all previous group assignments
2. It builds a set of all student pairs that have previously worked together
3. It tracks all unique students from previous groups
4. For each proposed group, it checks all possible pairs of students
5. If any pair exists in the previous pairs set, a conflict is reported
6. It identifies students from previous groups who don't appear in any proposed group
7. All conflicts and missing students are reported with details

## License

See LICENSE file for details.
