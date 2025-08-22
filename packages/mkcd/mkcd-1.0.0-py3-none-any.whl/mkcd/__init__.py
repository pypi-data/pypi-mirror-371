"""
MKCD - Linux utilities for Windows without WSL

This package provides common Linux command-line utilities (ls, cat, grep, etc.) 
as native Windows executables, making them available in any Windows shell.
"""

import os
import sys
from pathlib import Path
import subprocess

# Import Windows-specific modules only on Windows
if sys.platform == "win32":
    try:
        import winreg
    except ImportError:
        winreg = None
else:
    winreg = None

__version__ = "1.0.0"

def get_bin_directory():
    """Get the absolute path to the bundled binary directory."""
    package_dir = Path(__file__).parent
    bin_dir = package_dir / "_bin" / "windows_x86_64"
    return str(bin_dir.absolute())

def add_to_path():
    """Add the binary directory to the system PATH."""
    if sys.platform != "win32":
        print("Warning: PATH modification only supported on Windows")
        return False
    
    if winreg is None:
        print("Error: winreg module not available")
        return False
    
    bin_dir = get_bin_directory()
    if not os.path.exists(bin_dir):
        print(f"Error: Binary directory not found: {bin_dir}")
        return False
    
    try:
        # Try to add to user PATH first (doesn't require admin)
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""
            
            # Check if already in PATH
            if bin_dir.lower() in current_path.lower():
                print(f"Binary directory already in PATH: {bin_dir}")
                return True
            
            # Add to PATH
            new_path = f"{current_path};{bin_dir}" if current_path else bin_dir
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            
            # Notify system of environment change
            subprocess.run(['powershell', '-Command', 
                          'refreshenv; $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")'],
                          shell=True, capture_output=True)
            
            print(f"Successfully added to PATH: {bin_dir}")
            print("Note: You may need to restart your shell for changes to take effect.")
            return True
            
    except Exception as e:
        print(f"Error adding to PATH: {e}")
        return False

def remove_from_path():
    """Remove the binary directory from the system PATH."""
    if sys.platform != "win32":
        print("Warning: PATH modification only supported on Windows")
        return False
    
    if winreg is None:
        print("Error: winreg module not available")
        return False
    
    bin_dir = get_bin_directory()
    
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                print("No user PATH environment variable found")
                return True
            
            # Remove from PATH
            path_entries = [p.strip() for p in current_path.split(";") if p.strip()]
            new_entries = [p for p in path_entries if p.lower() != bin_dir.lower()]
            
            if len(new_entries) == len(path_entries):
                print(f"Binary directory not found in PATH: {bin_dir}")
                return True
            
            new_path = ";".join(new_entries)
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            
            print(f"Successfully removed from PATH: {bin_dir}")
            return True
            
    except Exception as e:
        print(f"Error removing from PATH: {e}")
        return False

def install():
    """Install mkcd and add binaries to PATH."""
    print("Installing mkcd utilities...")
    success = add_to_path()
    if success:
        print("Installation complete! Linux utilities are now available in your shell.")
        print("Available commands: ls, cat, grep, sed, awk, tar, gzip, and many more.")
        print("Try running: ls --help")
    else:
        print("Installation completed but failed to add to PATH.")
        print("You may need to manually add the binary directory to your PATH:")
        print(f"  {get_bin_directory()}")

def uninstall():
    """Uninstall mkcd and remove binaries from PATH."""
    print("Uninstalling mkcd utilities...")
    success = remove_from_path()
    if success:
        print("Uninstallation complete!")
    else:
        print("Uninstallation completed but failed to remove from PATH.")
