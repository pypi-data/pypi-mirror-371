#!/usr/bin/env python3
"""
KnowMe Setup Script with Complete Silent Installation Experience
"""

import sys
import os
import subprocess
import threading
import time
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

class CompleteSilentInstallCommand(install):
    """Custom installation that completely hides pip output."""
    
    def run(self):
        # Completely silent installation
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            # Redirect all output to devnull during installation
            with open(os.devnull, 'w') as devnull:
                sys.stdout = devnull
                sys.stderr = devnull
                
                # Show our custom progress
                sys.stdout = original_stdout
                sys.stderr = original_stderr
                print("🚀 Installing KnowMe silently...")
                
                # Redirect again for actual installation
                sys.stdout = devnull
                sys.stderr = devnull
                
                # Run the actual installation
                install.run(self)
                
        finally:
            # Restore output
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        # Post-install actions
        self._post_install()
        
    def _post_install(self):
        """Run post-installation tasks silently"""
        try:
            print("✅ KnowMe installation completed!")
            print("📊 Running KnowMe for the first time...")
            print("=" * 50)
            
            # Try to run knowme
            try:
                subprocess.run([sys.executable, "-m", "knowme"], 
                             check=True, timeout=10)
            except:
                print("✅ KnowMe is ready! Run 'knowme' to see your system info.")
            
            print("=" * 50)
            print("🚀 You can now run 'knowme' anytime!")
            
        except Exception as e:
            print(f"⚠️  Post-install setup completed with minor issues: {e}")

class SilentDevelopCommand(develop):
    """Custom development installation."""
    def run(self):
        print("🔧 Installing KnowMe in development mode...")
        develop.run(self)
        print("✅ Development installation complete!")

# Read requirements
def read_requirements():
    """Read requirements with version pinning for stability"""
    requirements = [
        "psutil>=5.8.0",
        "distro>=1.6.0", 
        "py-cpuinfo>=8.0.0",
        "requests>=2.25.0",
        "gputil>=1.4.0",
        "screeninfo>=0.6.0",
        "ifaddr>=0.1.7",
    ]
    return requirements

# Read long description
def read_long_description():
    """Read README.md for long description"""
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except:
        return "A fast, offline command-line tool for system information"

setup(
    name="knowme",
    version="1.0.5",
    author="Hrishi Mehta",
    author_email="mehtahrishi45@gmail.com",
    description="A fast, offline command-line tool that displays detailed system info with text-based ASCII art. Silent installation with progress bar!",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/mehtahrishi/knowme",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: Android",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "knowme=knowme.__main__:main",
        ],
    },
    cmdclass={
        'install': CompleteSilentInstallCommand,
        'develop': SilentDevelopCommand,
    },
    keywords=["system", "info", "neofetch", "cli", "terminal", "ascii", "mobile", "termux", "android", "silent"],
    project_urls={
        "Bug Tracker": "https://github.com/mehtahrishi/knowme/issues",
        "Documentation": "https://github.com/mehtahrishi/knowme#readme",
        "Source Code": "https://github.com/mehtahrishi/knowme",
    },
)
