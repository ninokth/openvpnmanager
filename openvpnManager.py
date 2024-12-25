#!/usr/bin/env python3

# -----------------------------------------------------------------------------
# OpenVPN Manager
# A Python script for managing OpenVPN connections with support for multiple
# configurations and secure credential management.
#
# Tested on Debian 12 (Bookworm). Use at your own risk. 
# No warranty is provided; author assumes no responsibility for any damages
# or data loss that may occur from using this software.
#
# Copyright (c) 2024 Nino Kurtalj
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
# -----------------------------------------------------------------------------

# Standard library imports
import os
import sys
import time
import subprocess
import configparser
from getpass import getpass

# ANSI color codes for output formatting
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

# Helper functions for output formatting
def print_success(msg):
    """Print success message in green"""
    print(f"{Colors.GREEN}{msg}{Colors.RESET}")

def print_error(msg):
    """Print error message in red"""
    print(f"{Colors.RED}{msg}{Colors.RESET}")

# Configuration and initialization
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# CONFIG_FILE = os.path.join(SCRIPT_DIR, 'openvpn_manager.ini')

def get_config_path():
    """Get configuration file path checking multiple locations"""
    # Check for environment variable override
    if 'OPENVPN_MANAGER_CONFIG' in os.environ:
        return os.environ['OPENVPN_MANAGER_CONFIG']
    
    # Check standard locations in order of preference
    config_locations = [
        os.path.expanduser('~/.config/openvpn_manager/config.ini'),
        '/etc/openvpn_manager/config.ini',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'openvpn_manager.ini')
    ]
    
    for location in config_locations:
        if os.path.exists(location):
            return location
            
    # Return default user config path for creation
    default_path = config_locations[0]
    default_dir = os.path.dirname(default_path)
    if not os.path.exists(default_dir):
        os.makedirs(default_dir, mode=0o755)
    return default_path

def load_config():
    """Load configuration from INI file, create default if doesn't exist"""
    config = configparser.ConfigParser()
    config_file = get_config_path()
    
    if not os.path.exists(config_file):
        # Create default configuration
        config['Paths'] = {
            'openvpn_dir': '$HOME/openvpn/OpenVPN_files',
            'credentials_dir': '$HOME/openvpn/.credentials'
        }
        
        # Save default configuration
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            config.write(f)
        print_success(f"Created default configuration file: {config_file}")
    else:
        config.read(config_file)
    
    # Expand environment variables in paths
    openvpn_dir = os.path.expandvars(config['Paths']['openvpn_dir'])
    credentials_dir = os.path.expandvars(config['Paths']['credentials_dir'])
    
    # Ensure directories exist
    if not os.path.exists(openvpn_dir):
        print_error(f"OpenVPN directory not found: {openvpn_dir}")
        sys.exit(1)
        
    if not os.path.exists(credentials_dir):
        try:
            os.makedirs(credentials_dir, mode=0o700)
            print_success(f"Created credentials directory: {credentials_dir}")
        except Exception as e:
            print_error(f"Failed to create credentials directory: {e}")
            sys.exit(1)
    
    return openvpn_dir, credentials_dir

# Load global configuration
OPENVPN_DIR, CREDENTIALS_DIR = load_config()

# Security and permission functions
def check_sudo():
    """Ensure we have sudo privileges"""
    try:
        subprocess.run(["sudo", "-v"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_permissions():
    """Check and report permission issues"""
    issues_found = False
    fix_commands = []
    
    # Check OpenVPN config files
    for root, _, files in os.walk(OPENVPN_DIR):
        for file in files:
            if file.endswith('.ovpn'):
                full_path = os.path.join(root, file)
                stat = os.stat(full_path)
                if stat.st_mode & 0o777 != 0o600:
                    issues_found = True
                    print_error(f"Incorrect permissions {oct(stat.st_mode & 0o777)} on {full_path}")
                    fix_commands.append(f"chmod 600 '{full_path}'")

    # Check credentials directory
    if os.path.exists(CREDENTIALS_DIR):
        stat = os.stat(CREDENTIALS_DIR)
        if stat.st_mode & 0o777 != 0o700:
            issues_found = True
            print_error(f"Incorrect permissions {oct(stat.st_mode & 0o777)} on {CREDENTIALS_DIR}")
            fix_commands.append(f"chmod 700 '{CREDENTIALS_DIR}'")

        # Check credential files
        for file in os.listdir(CREDENTIALS_DIR):
            if file.endswith('.cred'):
                full_path = os.path.join(CREDENTIALS_DIR, file)
                stat = os.stat(full_path)
                if stat.st_mode & 0o777 != 0o600:
                    issues_found = True
                    print_error(f"Incorrect permissions {oct(stat.st_mode & 0o777)} on {full_path}")
                    fix_commands.append(f"chmod 600 '{full_path}'")

    if issues_found:
        print_error("\nPermission issues found! Please run the following commands to fix:")
        print("\n".join(f"  {cmd}" for cmd in fix_commands))
        print("\nOr run this combined command:")
        print(f"  {' && '.join(fix_commands)}")
        
        fix_now = input("\nWould you like to fix these issues now? (y/n): ").lower().strip()
        if fix_now.startswith('y'):
            try:
                for cmd in fix_commands:
                    subprocess.run(cmd, shell=True, check=True)
                print_success("Permissions fixed successfully!")
                return True
            except subprocess.CalledProcessError as e:
                print_error(f"Error fixing permissions: {e}")
                return False
        return False
    else:
        print_success("All file permissions are correct.")
        return True

# Credential management functions
def ensure_credentials_dir():
    """Create .credentials directory if it doesn't exist"""
    if not os.path.exists(CREDENTIALS_DIR):
        os.makedirs(CREDENTIALS_DIR, mode=0o700)

def get_credentials(config_name):
    """Get credentials from user or file"""
    ensure_credentials_dir()
    cred_file = os.path.join(CREDENTIALS_DIR, f"{os.path.splitext(config_name)[0]}.cred")
    
    if os.path.exists(cred_file):
        use_existing = input("Use existing credentials? (y/n): ").lower().strip()
        if use_existing.startswith('y'):
            print_success("Using existing credentials.")
            return cred_file

    username = input("Username: ").strip()
    password = getpass("Password: ").strip()
    
    try:
        with open(cred_file, 'w') as f:
            os.chmod(cred_file, 0o600)
            f.write(f"{username}\n{password}\n")
        print_success("Credentials saved.")
        return cred_file
    except Exception as e:
        print_error(f"Error saving credentials: {e}")
        return None

# OpenVPN management functions
def find_ovpn_files():
    """Find all .ovpn files in the OpenVPN directory"""
    ovpn_list = []
    for root, _, files in os.walk(OPENVPN_DIR):
        for file in files:
            if file.endswith(".ovpn"):
                ovpn_list.append({
                    "name": file,
                    "full_path": os.path.join(root, file),
                    "dir": os.path.basename(root)
                })
    return ovpn_list

def needs_credentials(ovpn_path):
    """Check if OpenVPN config requires credentials"""
    with open(ovpn_path, 'r') as f:
        return 'auth-user-pass' in f.read()

def kill_openvpn():
    """Kill any running OpenVPN processes"""
    try:
        output = subprocess.check_output(["pgrep", "openvpn"])
        pids = output.decode().strip().split()
        for pid in pids:
            subprocess.run(["sudo", "kill", pid], check=True)
            print_success(f"Killed OpenVPN process {pid}")
        return True
    except subprocess.CalledProcessError:
        return False

def is_openvpn_running():
    """Check if OpenVPN is running"""
    try:
        subprocess.check_output(["pgrep", "openvpn"])
        return True
    except subprocess.CalledProcessError:
        return False

def wait_for_initialization(log_process):
    """Wait for OpenVPN initialization to complete"""
    try:
        while True:
            output = log_process.stdout.readline()
            if not output:
                break
            
            print(output.strip())
            
            if "Initialization Sequence Completed" in output:
                return True
            if any(x in output for x in ["AUTH_FAILED", "Connection refused", "No such file or directory"]):
                return False
    except KeyboardInterrupt:
        return False
    return False

def start_vpn(config, debug=False):
    """Start OpenVPN with the given configuration"""
    if not check_sudo():
        print_error("This script requires sudo privileges.")
        return False

    kill_openvpn()  # Kill any existing OpenVPN processes
    
    # Setup and configure log file
    log_file = "/tmp/openvpn-debug.log" if debug else "/tmp/openvpn.log"
    try:
        subprocess.run(["sudo", "touch", log_file], check=True)
        subprocess.run(["sudo", "chmod", "666", log_file], check=True)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to setup log file: {e}")
        return False

    # Prepare OpenVPN command
    cmd = ["sudo", "openvpn"]
    cmd.extend(["--verb", "4", "--daemon", "openvpn-debug", "--log", log_file] if debug
              else ["--daemon", "openvpn", "--log", log_file])
    cmd.extend(["--config", config['full_path'], "--user", os.environ["USER"]])

    # Handle credentials if needed
    if needs_credentials(config['full_path']):
        cred_file = get_credentials(config['name'])
        if not cred_file:
            return False
        cmd.extend(["--auth-user-pass", cred_file])

    try:
        # Start OpenVPN
        subprocess.run(cmd, check=True)
        
        if debug:
            print("OpenVPN started in debug mode. Showing log output:")
            time.sleep(1)
            
            # Follow log file in debug mode
            log_process = subprocess.Popen(
                ["tail", "-f", log_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            if wait_for_initialization(log_process):
                print_success("\nOpenVPN connection established.")
                print("\nOptions:")
                print("  1) Return to menu")
                print("  2) Exit to shell")
                
                while True:
                    choice = input("\nSelect option (1-2): ").strip()
                    if choice == '1':
                        log_process.terminate()
                        return True
                    elif choice == '2':
                        log_process.terminate()
                        print_success("VPN connection running in background.")
                        sys.exit(0)
                    else:
                        print_error("Invalid choice. Please enter 1 or 2.")
            else:
                print_error("\nOpenVPN failed to initialize properly.")
                log_process.terminate()
                return False
        else:
            time.sleep(2)
            if is_openvpn_running():
                print_success("OpenVPN started successfully")
                return True
            else:
                print_error("Failed to start OpenVPN")
                return False
            
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to start OpenVPN: {e}")
        return False
    except KeyboardInterrupt:
        print_error("\nInterrupted by user")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False
    finally:
        if not debug:
            try:
                subprocess.run(["sudo", "rm", "-f", log_file], check=True)
            except subprocess.CalledProcessError:
                pass

# UI Functions
def show_menu(configs):
    """Display available OpenVPN configurations"""
    print("\nAvailable OpenVPN configurations:")
    for i, config in enumerate(configs, 1):
        print(f"  {i}) {config['dir']}/{config['name']}")
        if needs_credentials(config['full_path']):
            cred_file = os.path.join(CREDENTIALS_DIR, 
                                   f"{os.path.splitext(config['name'])[0]}.cred")
            if os.path.exists(cred_file):
                print("     (credentials saved)")
            else:
                print("     (credentials required)")
    print("  0) Exit")

# Main function
def main():
    # Check if running as root
    if os.geteuid() == 0:
        print_error("Don't run this script as root. Run as normal user with sudo privileges.")
        sys.exit(1)

    # Check file permissions
    if not check_permissions():
        if input("Continue anyway? (y/n): ").lower().strip() != 'y':
            sys.exit(1)

    # Find OpenVPN configurations
    configs = find_ovpn_files()
    if not configs:
        print_error("No OpenVPN configurations found.")
        sys.exit(1)

    # Get debug preference
    debug = input("Run in debug mode? (y/n): ").lower().strip().startswith('y')

    # Main menu loop
    while True:
        show_menu(configs)
        try:
            choice = input("\nSelect configuration (0 to exit): ").strip()
            if choice == '0':
                break
                
            if not choice.isdigit() or not (0 < int(choice) <= len(configs)):
                print_error("Invalid selection")
                continue
                
            config = configs[int(choice) - 1]
            if start_vpn(config, debug):
                break
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print_error(f"Error: {e}")

if __name__ == "__main__":
    main()