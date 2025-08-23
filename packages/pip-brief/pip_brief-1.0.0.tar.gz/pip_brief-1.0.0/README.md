# pip-brief

A clean, human-readable wrapper for `pip install` that provides organized summaries of installation results.

## Features

- **Clean Output Format**: Organized summary with numbered sections
- **Comprehensive Tracking**: Shows installed packages, already satisfied requirements, warnings, errors, and dependencies
- **Duplicate Removal**: Eliminates repetitive messages for cleaner output
- **Verbose Mode**: Option to see full pip output when needed
- **Simple Interface**: Easy-to-use command structure

## Installation

```bash
pip install pip-brief
```

## Usage

### Install one or more packages with brief summary:
```bash
pip-brief install <package-name>
pip-brief install <package1> <package2> <package3>
```

### Install with verbose output (shows full pip output):
```bash
pip-brief install <package-name> --verbose
```

## Example Output

### Single Package:
```
**Summary of requests installation:**


1) Installed:
requests (2.31.0), urllib3 (2.0.4), certifi (2023.7.22)


2) Already Satisfied:
charset-normalizer, idna


3) Dependencies:
requests, urllib3, certifi, charset-normalizer, idna
```

### Multiple Packages:
```
**Summary of loguru installation:**


1) Installed:
loguru (0.7.3)


2) Dependencies:
loguru

==================================================

**Summary of emoji installation:**


1) Installed:
emoji (2.8.0)


2) Dependencies:
emoji
```

## Output Format

The summary is organized into up to 5 sections (only applicable sections are shown):

1. **Installed**: Packages that were newly installed
2. **Already Satisfied**: Packages that were already present and up-to-date
3. **Warnings**: Important warnings from pip (cleaned and deduplicated)
4. **Errors**: Any errors encountered (key messages only)
5. **Dependencies**: All packages that were collected/processed during installation

## Why pip-brief?

Standard `pip install` output can be verbose and hard to parse quickly. pip-brief provides:
- Clear separation of different types of information
- Elimination of redundant messages
- Easy-to-scan format
- Focus on what actually happened during installation

## Requirements

- Python 3.6+
- pip

## License

This project is licensed under the MIT License - see the LICENSE file for details.