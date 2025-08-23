import psutil
import platform
import socket
import cpuinfo
import requests
import datetime
import os
import sys
import subprocess
import ifaddr
from .utils import format_bytes, format_uptime, colorize

# --- Mobile/Termux Detection ---

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

# --- Mobile-Specific Information Functions ---

def get_android_version():
    """Get Android version information."""
    if not is_android():
        return "N/A"
    
    try:
        # Try to get Android version from system properties
        result = subprocess.run(['getprop', 'ro.build.version.release'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            android_version = result.stdout.strip()
            
            # Get API level
            api_result = subprocess.run(['getprop', 'ro.build.version.sdk'], 
                                      capture_output=True, text=True, timeout=5)
            if api_result.returncode == 0 and api_result.stdout.strip():
                api_level = api_result.stdout.strip()
                return f"Android {android_version} (API {api_level})"
            
            return f"Android {android_version}"
    except:
        pass
    
    # Fallback: try to read from build.prop
    try:
        with open('/system/build.prop', 'r') as f:
            for line in f:
                if 'ro.build.version.release=' in line:
                    version = line.split('=')[1].strip()
                    return f"Android {version}"
    except:
        pass
    
    return "Android (version unknown)"

def get_device_model():
    """Get device model information."""
    if not is_android():
        return "N/A"
    
    try:
        # Get device model
        result = subprocess.run(['getprop', 'ro.product.model'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            model = result.stdout.strip()
            
            # Get manufacturer
            brand_result = subprocess.run(['getprop', 'ro.product.brand'], 
                                        capture_output=True, text=True, timeout=5)
            if brand_result.returncode == 0 and brand_result.stdout.strip():
                brand = brand_result.stdout.strip()
                return f"{brand} {model}"
            
            return model
    except:
        pass
    
    return "Unknown Device"

def get_mobile_network_info():
    """Get mobile network information (carrier, signal, etc.)."""
    if not is_android():
        return {}
    
    mobile_info = {}
    
    try:
        # Try to get network operator
        result = subprocess.run(['getprop', 'gsm.operator.alpha'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            mobile_info['carrier'] = result.stdout.strip()
        
        # Try to get network type
        network_result = subprocess.run(['getprop', 'gsm.network.type'], 
                                      capture_output=True, text=True, timeout=5)
        if network_result.returncode == 0 and network_result.stdout.strip():
            mobile_info['network_type'] = network_result.stdout.strip()
    except:
        pass
    
    return mobile_info

def get_termux_info():
    """Get Termux-specific information."""
    if not is_termux():
        return {}
    
    termux_info = {}
    
    try:
        # Get Termux version
        result = subprocess.run(['pkg', 'list-installed', 'termux-tools'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            termux_info['termux_version'] = "Installed"
        
        # Check if Termux:API is available
        if os.path.exists('/data/data/com.termux/files/usr/bin/termux-battery-status'):
            termux_info['termux_api'] = "Available"
        
        # Get storage info
        prefix = os.environ.get('PREFIX', '/data/data/com.termux/files/usr')
        if os.path.exists(prefix):
            termux_info['prefix'] = prefix
    except:
        pass
    
    return termux_info

def get_mobile_battery_info():
    """Get enhanced battery information for mobile devices."""
    try:
        battery = psutil.sensors_battery()
        if battery:
            status = "Charging" if battery.power_plugged else "Discharging"
            return f"{battery.percent:.1f}% ({status})"
    except:
        pass
    
    # Try Termux API if available
    if is_termux():
        try:
            result = subprocess.run(['termux-battery-status'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                import json
                battery_data = json.loads(result.stdout)
                percentage = battery_data.get('percentage', 'N/A')
                status = battery_data.get('status', 'Unknown')
                temperature = battery_data.get('temperature', 'N/A')
                
                battery_str = f"{percentage}% ({status})"
                if temperature != 'N/A':
                    battery_str += f", {temperature}°C"
                return battery_str
        except:
            pass
    
    return "N/A"

def get_mobile_sensors():
    """Get mobile sensor information."""
    if not is_termux():
        return {}
    
    sensors = {}
    
    try:
        # Try to get sensor info using Termux API
        sensor_commands = {
            'accelerometer': 'termux-sensor -s accelerometer -n 1',
            'gyroscope': 'termux-sensor -s gyroscope -n 1',
            'magnetometer': 'termux-sensor -s magnetometer -n 1',
            'light': 'termux-sensor -s light -n 1'
        }
        
        for sensor_name, command in sensor_commands.items():
            try:
                result = subprocess.run(command.split(), 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0 and result.stdout.strip():
                    sensors[sensor_name] = "Available"
            except:
                continue
    except:
        pass
    
    return sensors

# --- Enhanced Existing Functions ---

def get_logged_in_users():
    """Gets a list of currently logged-in users."""
    try:
        users = psutil.users()
        if is_termux():
            # In Termux, show current user info
            current_user = os.environ.get('USER', 'termux')
            return f"{current_user} (Termux session)"
        
        user_list = [f"{u.name} (since {datetime.datetime.fromtimestamp(u.started).strftime('%Y-%m-%d %H:%M')})" for u in users]
        return "\n           ".join(user_list) if user_list else "No users logged in"
    except Exception:
        return "N/A"

def get_top_processes(count=5):
    """Gets top processes by memory usage."""
    try:
        procs = [p for p in psutil.process_iter(['pid', 'name', 'memory_percent'])]
        sorted_procs = sorted(procs, key=lambda p: p.info['memory_percent'], reverse=True)
        
        proc_list = [f"{p.info['name']} (PID: {p.info['pid']}, Mem: {p.info['memory_percent']:.1f}%)" for p in sorted_procs[:count]]
        return "\n           ".join(proc_list)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return "Could not retrieve processes."

def get_listening_ports(count=10):
    """Gets open TCP listening ports and the associated process."""
    try:
        connections = psutil.net_connections(kind='inet')
        listeners = [c for c in connections if c.status == psutil.CONN_LISTEN]
        
        if not listeners:
            return "None"
        
        port_list = []
        for conn in listeners[:count]:
            proc_name = "N/A"
            try:
                if conn.pid:
                    proc = psutil.Process(conn.pid)
                    proc_name = proc.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            port_info = f"{conn.laddr.port}/{conn.type.name} - {proc_name}"
            port_list.append(port_info)
        
        return "\n           ".join(port_list)
    except (psutil.AccessDenied, AttributeError):
        return "N/A"

def get_default_gateway():
    """Gets the default network gateway using ifaddr."""
    try:
        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            for ip in adapter.ips:
                if isinstance(ip.ip, str) and not ip.ip.startswith('127.') and not ip.ip.startswith('169.254.'):
                    # This is a simplified approach; getting the actual gateway requires more complex logic
                    return "N/A (See Primary Interface)"
        return "N/A"
    except Exception:
        return "N/A"

# --- Existing Functions (Enhanced for Mobile) ---

def get_system_condition():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    
    if cpu_usage > 80 or ram_usage > 90:
        return colorize("High Load", color="red")
    elif cpu_usage > 60 or ram_usage > 75:
        return colorize("Moderate Load", color="yellow")
    
    return colorize("Healthy", color="green")

def get_gpu_info():
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            return f"{gpu.name} ({gpu.memoryTotal}MB)"
    except (ImportError, Exception):
        pass
    
    # For mobile devices, try to get GPU info from system
    if is_android():
        try:
            result = subprocess.run(['getprop', 'ro.hardware.vulkan'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return f"Mobile GPU ({result.stdout.strip()})"
        except:
            pass
        return "Mobile GPU"
    
    return "N/A"

def get_screen_resolution():
    try:
        import screeninfo
        monitors = screeninfo.get_monitors()
        if monitors:
            monitor = monitors[0]
            return f"{monitor.width}x{monitor.height}"
    except (ImportError, Exception):
        pass
    
    # For Termux, try to get display info
    if is_termux():
        try:
            result = subprocess.run(['termux-display-info'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                import json
                display_data = json.loads(result.stdout)
                width = display_data.get('width', 'N/A')
                height = display_data.get('height', 'N/A')
                if width != 'N/A' and height != 'N/A':
                    return f"{width}x{height}"
        except:
            pass
    
    return "N/A"

def get_process_info():
    return f"{len(psutil.pids())} running"

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org', timeout=5).text
    except requests.exceptions.RequestException:
        return "N/A"

def get_network_info():
    interfaces = psutil.net_if_addrs()
    network_str, mac_str = "", ""
    
    for interface_name, interface_addresses in interfaces.items():
        if interface_name.startswith(('lo', 'docker', 'br-')):
            continue
            
        for address in interface_addresses:
            # IP addresses
            if str(address.family) == 'AddressFamily.AF_INET':
                network_str += f"{interface_name}: {address.address}\n           "
            # MAC addresses - check multiple ways
            elif (str(address.family) == 'AddressFamily.AF_PACKET' or 
                  str(address.family) == 'AddressFamily.AF_LINK' or
                  (hasattr(address, 'address') and address.address and 
                   len(address.address) in [17, 18] and (':' in address.address or '-' in address.address))):
                mac_str += f"{interface_name}: {address.address}\n           "
    
    return network_str.strip(), mac_str.strip()

def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_str = ""
    
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            disk_str += f"{partition.mountpoint} ({partition.fstype}): {format_bytes(partition_usage.used)} / {format_bytes(partition_usage.total)} ({partition_usage.percent:.1f}%)\n           "
        except PermissionError:
            continue
    
    return disk_str.strip()

def get_battery_info():
    return get_mobile_battery_info()

def get_cpu_temperature():
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                if entries:
                    return f"{entries[0].current:.1f}°C"
    except (AttributeError, NotImplementedError):
        pass
    
    # For mobile devices, try alternative methods
    if is_android():
        try:
            # Try to read thermal zones
            thermal_paths = [
                '/sys/class/thermal/thermal_zone0/temp',
                '/sys/class/thermal/thermal_zone1/temp'
            ]
            
            for path in thermal_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        temp = int(f.read().strip()) / 1000  # Convert from millidegrees
                        return f"{temp:.1f}°C"
        except:
            pass
    
    return "N/A"

# --- Main Info Gathering Function (Enhanced for Mobile) ---

def get_all_system_info():
    uname = platform.uname()
    cpu_info = cpuinfo.get_cpu_info()
    
    # Get network info once and store it
    network_info = get_network_info()
    private_ip = network_info[0] if network_info[0] else "N/A"
    mac_address = network_info[1] if network_info[1] else "N/A"
    
    info_dict = {
        "Condition": get_system_condition(),
        "OS": f"{uname.system} {uname.release}",
        "Hostname": uname.node,
        "Kernel": uname.version.split()[0] if uname.version else "N/A",
        "Uptime": format_uptime(psutil.boot_time()),
        "Logged In": get_logged_in_users(),
        "CPU": cpu_info.get('brand_raw', 'Unknown CPU'),
        "CPU Cores": f"{psutil.cpu_count(logical=False)} (Physical), {psutil.cpu_count(logical=True)} (Logical)",
        "Arch": uname.machine,
        "GPU": get_gpu_info(),
        "Resolution": get_screen_resolution(),
        "RAM": f"{format_bytes(psutil.virtual_memory().used)} / {format_bytes(psutil.virtual_memory().total)} ({psutil.virtual_memory().percent:.1f}%)",
        "Disk": get_disk_info(),
        "Battery": get_battery_info(),
        "CPU Temp": get_cpu_temperature(),
        "Processes": get_process_info(),
        "Top Procs": get_top_processes(),
        "Public IP": get_public_ip(),
        "Gateway": get_default_gateway(),
        "Private IP": private_ip,
        "MAC Address": mac_address,
        "Open Ports": get_listening_ports()
    }
    
    # Add mobile-specific information
    if is_android():
        android_version = get_android_version()
        if android_version != "N/A":
            info_dict["Android"] = android_version
        
        device_model = get_device_model()
        if device_model != "N/A":
            info_dict["Device"] = device_model
        
        mobile_network = get_mobile_network_info()
        if mobile_network.get('carrier'):
            info_dict["Carrier"] = mobile_network['carrier']
        if mobile_network.get('network_type'):
            info_dict["Network Type"] = mobile_network['network_type']
    
    if is_termux():
        termux_info = get_termux_info()
        if termux_info:
            info_dict["Environment"] = "Termux"
            if termux_info.get('termux_api'):
                info_dict["Termux API"] = termux_info['termux_api']
        
        # Add sensor information
        sensors = get_mobile_sensors()
        if sensors:
            sensor_list = ", ".join(sensors.keys())
            info_dict["Sensors"] = sensor_list
    
    return info_dict
