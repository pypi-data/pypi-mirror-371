#!/usr/bin/env python3
"""
KnowMe Custom Installer with Progress Bar
Provides a clean installation experience hiding package details
"""

import sys
import subprocess
import time
import threading
import os
from typing import List, Optional

class ProgressBar:
    """Animated progress bar for installation"""
    
    def __init__(self, total_steps: int = 100, width: int = 50):
        self.total_steps = total_steps
        self.width = width
        self.current_step = 0
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
    def start(self, message: str = "Installing KnowMe"):
        """Start the progress bar animation"""
        self.running = True
        self.current_step = 0
        print(f"\n🚀 {message}...")
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
        
    def update(self, step: int, message: str = ""):
        """Update progress bar to specific step"""
        self.current_step = min(step, self.total_steps)
        if message:
            self._print_status(message)
            
    def _animate(self):
        """Animate the progress bar"""
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        spinner_idx = 0
        
        while self.running:
            # Calculate progress
            progress = self.current_step / self.total_steps
            filled_width = int(self.width * progress)
            
            # Create progress bar
            bar = "█" * filled_width + "░" * (self.width - filled_width)
            percentage = int(progress * 100)
            
            # Print progress with spinner
            spinner = spinner_chars[spinner_idx % len(spinner_chars)]
            print(f"\r{spinner} [{bar}] {percentage}%", end="", flush=True)
            
            spinner_idx += 1
            time.sleep(0.1)
            
    def _print_status(self, message: str):
        """Print status message above progress bar"""
        print(f"\r{' ' * (self.width + 20)}", end="")  # Clear line
        print(f"\r📦 {message}")
        
    def finish(self, success: bool = True, message: str = ""):
        """Stop the progress bar and show completion"""
        self.running = False
        if self.thread:
            self.thread.join()
            
        # Clear the progress line
        print(f"\r{' ' * (self.width + 20)}", end="")
        
        if success:
            print(f"\r✅ {message or 'Installation completed successfully!'}")
        else:
            print(f"\r❌ {message or 'Installation failed!'}")
        print()

def run_command(cmd: List[str], capture_output: bool = True) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_python_version() -> bool:
    """Check if Python version is compatible"""
    version = sys.version_info
    return version.major == 3 and version.minor >= 7

def check_pip_available() -> bool:
    """Check if pip is available"""
    code, _, _ = run_command([sys.executable, "-m", "pip", "--version"])
    return code == 0

def install_knowme_with_progress():
    """Install KnowMe with a beautiful progress bar"""
    
    # Initialize progress bar
    progress = ProgressBar(total_steps=100, width=40)
    
    try:
        # Step 1: Check Python version
        progress.start("Checking system requirements")
        progress.update(10, "Checking Python version")
        
        if not check_python_version():
            progress.finish(False, "Python 3.7+ required")
            print("❌ Python 3.7 or higher is required.")
            print("📥 Download from: https://www.python.org/downloads/")
            return False
            
        time.sleep(0.5)  # Small delay for visual effect
        
        # Step 2: Check pip
        progress.update(20, "Checking pip availability")
        
        if not check_pip_available():
            progress.finish(False, "pip is not available")
            print("❌ pip is not installed or not accessible.")
            return False
            
        time.sleep(0.5)
        
        # Step 3: Update pip (optional, silent)
        progress.update(30, "Preparing installation environment")
        run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
        time.sleep(1)
        
        # Step 4: Install KnowMe
        progress.update(40, "Downloading KnowMe package")
        time.sleep(1)
        
        progress.update(60, "Installing dependencies")
        
        # Install with minimal output
        install_cmd = [
            sys.executable, "-m", "pip", "install", 
            "knowme", 
            "--quiet", 
            "--no-warn-script-location"
        ]
        
        code, stdout, stderr = run_command(install_cmd)
        
        progress.update(90, "Finalizing installation")
        time.sleep(0.5)
        
        if code != 0:
            progress.finish(False, "Installation failed")
            print(f"❌ Installation error: {stderr}")
            return False
            
        # Step 5: Verify installation
        progress.update(95, "Verifying installation")
        
        verify_cmd = [sys.executable, "-c", "import knowme; print('OK')"]
        code, _, _ = run_command(verify_cmd)
        
        if code != 0:
            progress.finish(False, "Installation verification failed")
            return False
            
        progress.update(100, "Installation complete")
        time.sleep(0.5)
        
        progress.finish(True, "KnowMe installed successfully!")
        
        # Show success message and run knowme
        print("🎉 Welcome to KnowMe!")
        print("📊 Here's your system information:")
        print("=" * 50)
        
        # Run knowme to show the result
        try:
            subprocess.run([sys.executable, "-m", "knowme"], check=True)
        except:
            # Fallback if module execution fails
            try:
                subprocess.run(["knowme"], check=True)
            except:
                print("✅ KnowMe is installed! Run 'knowme' to see your system info.")
        
        print("\n" + "=" * 50)
        print("🚀 Installation complete! You can now run 'knowme' anytime.")
        
        return True
        
    except KeyboardInterrupt:
        progress.finish(False, "Installation cancelled by user")
        print("\n⚠️  Installation cancelled.")
        return False
    except Exception as e:
        progress.finish(False, f"Unexpected error: {str(e)}")
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main installer function"""
    print("🌟 KnowMe Installer")
    print("📋 Fast, offline system information tool")
    print()
    
    success = install_knowme_with_progress()
    
    if success:
        print("\n💡 Tips:")
        print("   • Run 'knowme' to see your system information")
        print("   • KnowMe works completely offline")
        print("   • No configuration needed!")
        
        # Ask if user wants to add to PATH (if needed)
        try:
            subprocess.run(["knowme", "--version"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n⚠️  Note: If 'knowme' command is not found, you may need to:")
            print("   • Restart your terminal")
            print("   • Add Python Scripts to your PATH")
            print("   • Or run: python -m knowme")
    else:
        print("\n🔧 Troubleshooting:")
        print("   • Ensure you have Python 3.7+")
        print("   • Check your internet connection")
        print("   • Try: pip install knowme")
        sys.exit(1)

if __name__ == "__main__":
    main()
