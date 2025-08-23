import argparse
import sys
from pip_brief.core import run_pip_install, parse_pip_output, format_summary

def main():
    parser = argparse.ArgumentParser(description="pip-brief: A clean summary for pip install")
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install packages with brief summary')
    install_parser.add_argument('packages', nargs='+', help='Package name(s) to install')
    install_parser.add_argument('--verbose', action='store_true', help='Show full pip output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'install':
        if args.verbose:
            # For verbose mode, install all packages together and show raw output
            raw_output = run_pip_install(args.packages)
            print(raw_output)
        else:
            # For brief mode, install each package separately and show individual summaries
            for i, package in enumerate(args.packages):
                raw_output = run_pip_install([package])
                parsed = parse_pip_output(raw_output)
                summary = format_summary(parsed, package)
                print(summary)
                
                # Add spacing between package summaries (except for the last one)
                if i < len(args.packages) - 1:
                    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()