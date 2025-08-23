import subprocess
import re

# ANSI color codes for terminal formatting
class Colors:
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'  # Reset to default color

def run_pip_install(packages):
    """Run pip install command and capture output"""
    if isinstance(packages, str):
        packages = [packages]
    
    cmd = ["pip", "install"] + packages
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr

def parse_pip_output(output):
    """Parse pip install output into structured sections"""
    lines = output.splitlines()
    
    installed = []
    already_satisfied = []
    warnings = []
    errors = []
    dependencies = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Parse installed packages
        if "Successfully installed" in line:
            # Extract package names with versions from "Successfully installed package1-1.0.0 package2-2.0.0"
            match = re.search(r"Successfully installed (.+)", line)
            if match:
                packages_raw = match.group(1).split()
                for package in packages_raw:
                    # Convert package-version format to package (version) format
                    if '-' in package:
                        # Split by last dash to separate name and version
                        parts = package.rsplit('-', 1)
                        if len(parts) == 2:
                            name, version = parts
                            formatted_package = f"{name} ({version})"
                            installed.append(formatted_package)
                        else:
                            installed.append(package)
                    else:
                        installed.append(package)
        
        # Parse already satisfied packages
        elif "Requirement already satisfied:" in line:
            # Extract package name and version info
            # Example: "Requirement already satisfied: numpy in c:\path (2.2.3)"
            match = re.search(r"Requirement already satisfied:\s+([^\s]+).*?\(([^)]+)\)", line)
            if match:
                package_name = match.group(1)
                version = match.group(2)
                package_info = f"{package_name} ({version})"
                already_satisfied.append(package_info)
            else:
                # Fallback if version not found
                match = re.search(r"Requirement already satisfied:\s+([^\s]+)", line)
                if match:
                    package_info = match.group(1)
                    already_satisfied.append(package_info)
        
        # Parse warnings
        elif "WARNING:" in line:
            # Clean up warning message - remove WARNING: prefix and make it understandable
            warning = line.replace("WARNING:", "").strip()
            
            # Simplify common warning messages
            if "Ignoring invalid distribution" in warning:
                # Extract the distribution name and make it readable
                match = re.search(r"Ignoring invalid distribution ([^\s]+)", warning)
                if match:
                    dist_name = match.group(1)
                    simplified_warning = f"Corrupted package installation detected ({dist_name}) - consider cleaning pip cache"
                    if simplified_warning not in warnings:
                        warnings.append(simplified_warning)
            else:
                # For other warnings, just clean up and add
                warning = re.sub(r'\s+', ' ', warning)  # Normalize whitespace
                if warning and warning not in warnings:
                    warnings.append(warning)
        
        # Parse errors
        elif "ERROR:" in line:
            # Clean up error message - remove ERROR: prefix
            error = line.replace("ERROR:", "").strip()
            error = re.sub(r'\s+', ' ', error)  # Normalize whitespace
            if error and error not in errors:
                errors.append(error)
        
        # Parse dependencies (packages being collected/downloaded)
        elif "Collecting" in line:
            match = re.search(r"Collecting\s+([^\s\(]+)", line)
            if match:
                dep = match.group(1)
                if dep not in dependencies:
                    dependencies.append(dep)
    
    # Remove duplicates while preserving order
    def remove_duplicates(lst):
        seen = set()
        result = []
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    
    return {
        "installed": remove_duplicates(installed),
        "already_satisfied": remove_duplicates(already_satisfied),
        "warnings": remove_duplicates(warnings),
        "errors": remove_duplicates(errors),
        "dependencies": remove_duplicates(dependencies)
    }

def format_summary(data, package_name):
    """Format the final summary according to specified format"""
    lines = []
    
    # Determine if installation was successful or failed
    has_installed = len(data["installed"]) > 0
    has_already_satisfied = len(data["already_satisfied"]) > 0
    has_errors = len(data["errors"]) > 0
    
    # Choose appropriate title based on success/failure
    if has_errors and not has_installed and not has_already_satisfied:
        title = f"Summary of {package_name} attempt:"
    else:
        title = f"Summary of {package_name} installation:"
    
    # Add color formatting to the title
    colored_title = f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.END}"
    underline = "=" * len(title)  # Use original title length for underline
    
    lines.append(colored_title)
    lines.append(underline)
    lines.append("")  # Empty line after underline
    
    point_number = 1
    
    # 1) Installed
    if data["installed"]:
        lines.append(f"{point_number}) Installed:")
        lines.append(", ".join(data["installed"]))
        lines.append("")  # Empty line
        lines.append("")  # Second empty line
        point_number += 1
    
    # 2) Already Satisfied
    if data["already_satisfied"]:
        lines.append(f"{point_number}) Already Satisfied:")
        lines.append(", ".join(data["already_satisfied"]))
        lines.append("")  # Empty line
        lines.append("")  # Second empty line
        point_number += 1
    
    # 3) Warnings (only show if there was successful activity)
    if data["warnings"] and (has_installed or has_already_satisfied):
        lines.append(f"{point_number}) Warnings:")
        lines.append(", ".join(data["warnings"]))
        lines.append("")  # Empty line
        lines.append("")  # Second empty line
        point_number += 1
    
    # 4) Errors
    if data["errors"]:
        lines.append(f"{point_number}) Errors:")
        lines.append(", ".join(data["errors"]))
        lines.append("")  # Empty line
        lines.append("")  # Second empty line
        point_number += 1
    
    # 5) Dependencies
    if data["dependencies"]:
        lines.append(f"{point_number}) Dependencies:")
        lines.append(", ".join(data["dependencies"]))
    
    # Remove trailing empty lines
    while lines and lines[-1] == "":
        lines.pop()
    
    return "\n".join(lines)