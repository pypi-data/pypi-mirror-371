from setuptools import setup, find_packages
from setuptools.command.install import install
import os

class PostInstallCommand(install):
    """Custom install command that adds binaries to PATH after installation."""
    
    def run(self):
        # Run the standard installation
        install.run(self)
        
        # Import and run our PATH modification after installation
        try:
            # Add the installation directory to sys.path temporarily
            import sys
            install_lib = self.install_lib
            if install_lib not in sys.path:
                sys.path.insert(0, install_lib)
            
            # Now try to import and run PATH modification
            import mkcd
            success = mkcd.add_to_path()
            if success:
                print("Successfully added mkcd utilities to PATH!")
            else:
                print("Installation completed but failed to add to PATH automatically.")
                print("Run: mkcd-install")
        except Exception as e:
            print(f"Installation completed but failed to add to PATH automatically: {e}")
            print("You can manually run: mkcd-install")

# Copy binaries from workspace root to package location during build
import shutil
from pathlib import Path

def copy_binaries_to_package():
    """Copy binaries from workspace root to package location."""
    # Source and destination paths
    workspace_bins = Path(__file__).parent / "windows_x86_64"
    package_bins = Path(__file__).parent / "src" / "mkcd" / "_bin" / "windows_x86_64"

    if workspace_bins.exists():
        # Create destination directory
        package_bins.mkdir(parents=True, exist_ok=True)
        
        # Copy all files (exe and dll)
        copied_files = 0
        for file_path in workspace_bins.glob("*"):
            if file_path.is_file():
                shutil.copy2(file_path, package_bins / file_path.name)
                copied_files += 1
        
        print(f"Copied {copied_files} binary files to package")
        return True
    else:
        print(f"Warning: Source binary directory not found: {workspace_bins}")
        return False

# Copy binaries before setup
copy_binaries_to_package()

setup(
    cmdclass={
        'install': PostInstallCommand,
    },
)
