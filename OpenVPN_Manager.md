# OpenVPN Manager

A Python script for managing OpenVPN connections with support for multiple configurations and secure credential management.

## Prerequisites

1. OpenVPN installed on your system:

```bash
sudo apt-get install openvpn
```

2. Sudo privileges for the user running the script
3. Python 3.6 or higher

## Installation

1. Create the OpenVPN directory structure:

```bash
mkdir -p ~/openvpn/OpenVPN_files
```

2. Clone or copy the script:

```bash
cp openvpnManager.py ~/openvpn/
chmod +x ~/openvpn/openvpnManager.py
```

## Directory Structure

```
~/openvpn/
  ├── OpenVPN_files/        # Your .ovpn configurations
  │   ├── Location1/        # Organized by location (optional)
  │   │   └── config1.ovpn
  │   └── Location2/
  │       └── config2.ovpn
  ├── .credentials/         # Created automatically for storing credentials
  ├── openvpnManager.py    # The management script
  └── openvpn_manager.ini  # Created automatically on first run
```

## Configuration File Permissions

1. OpenVPN configuration files (.ovpn):

```bash
chmod 600 ~/openvpn/OpenVPN_files/**/*.ovpn
```

2. Credentials directory (created automatically):

```bash
chmod 700 ~/openvpn/.credentials
```

3. Credential files (managed by script):

```bash
chmod 600 ~/openvpn/.credentials/*.cred
```

## Required System Access

The script requires:

1. Sudo access for OpenVPN operations:

```bash
# Add to /etc/sudoers.d/openvpn (use visudo)
username ALL=(ALL) NOPASSWD: /usr/sbin/openvpn
username ALL=(ALL) NOPASSWD: /bin/kill
```

2. Network configuration access:

- Ability to create/modify network interfaces
- Ability to modify routing tables
- Access to tun/tap devices

## Usage

1. Place your OpenVPN configuration files (.ovpn) in the `OpenVPN_files` directory
2. Run the script:

```bash
./openvpnManager.py
```

### Debug Mode

- Use debug mode for troubleshooting connection issues
- Shows detailed OpenVPN output
- Options to return to menu or exit to shell

### Regular Mode

- Runs OpenVPN in daemon mode
- Manages connections in the background
- Minimal output for regular usage

## Configuration File

The `openvpn_manager.ini` file is created automatically with default settings:

```ini
[Paths]
openvpn_dir = ~/openvpn/OpenVPN_files
credentials_dir = ~/openvpn/.credentials
```

## Security Considerations

1. Configuration files

   - Store .ovpn files with 600 permissions
   - Keep certificates and keys secure
   - Don't share credential files
2. Credentials

   - Stored encrypted in .credentials directory
   - Individual files for each configuration
   - Automatic permission management
3. System Access

   - Run script as regular user
   - Use sudo only for necessary operations
   - Maintain proper file permissions

## Troubleshooting

1. Connection Issues

   - Run in debug mode to see detailed output
   - Check system logs for errors
   - Verify network configuration
2. Permission Issues

   - Verify file permissions
   - Check sudo configuration
   - Ensure proper user rights
3. Common Problems

   - Credential errors: Check saved credentials
   - Network errors: Verify network access
   - Configuration errors: Validate .ovpn files

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
