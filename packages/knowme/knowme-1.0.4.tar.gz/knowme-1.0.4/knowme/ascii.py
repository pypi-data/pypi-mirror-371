import platform
import distro
import os
from . import logos

def is_termux():
    """Detect if running in Termux environment."""
    return os.path.exists('/data/data/com.termux') or 'com.termux' in os.environ.get('PREFIX', '')

def is_android():
    """Detect if running on Android."""
    try:
        with open('/proc/version', 'r') as f:
            return 'android' in f.read().lower()
    except:
        return False

def get_os_logo():
    """
    Detects the current OS and returns the corresponding text-based ASCII logo.
    Enhanced with mobile/Termux support.
    """
    system = platform.system()

    # Check for mobile environments first
    if is_termux():
        return logos.TERMUX_LOGO
    elif is_android():
        return logos.ANDROID_LOGO

    if system == "Linux":
        distro_name = distro.id().lower()
        
        # Check for specific distributions
        if "ubuntu" in distro_name:
            return logos.UBUNTU_LOGO
        elif "arch" in distro_name or "manjaro" in distro_name:
            return logos.ARCH_LOGO
        elif "debian" in distro_name:
            return logos.DEBIAN_LOGO
        elif "fedora" in distro_name:
            return logos.FEDORA_LOGO
        elif "centos" in distro_name or "rhel" in distro_name or "redhat" in distro_name:
            return logos.CENTOS_LOGO
        elif "kali" in distro_name:
            return logos.KALI_LOGO
        elif "opensuse" in distro_name or "suse" in distro_name:
            return logos.OPENSUSE_LOGO
        else:
            # Generic Linux logo for unknown distributions
            return logos.LINUX_LOGO
            
    elif system == "Windows":
        return logos.WINDOWS_LOGO
        
    elif system == "Darwin":
        return logos.MACOS_LOGO
        
    else:
        return logos.DEFAULT_LOGO
