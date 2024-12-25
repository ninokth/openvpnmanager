# OpenVPN Manager

A Python script for managing OpenVPN connections with support for multiple configurations and secure credential management.

## Prerequisites

1. **OpenVPN Installed on Your System:**

   ```bash
   sudo apt-get install openvpn
   ```
2. **Sudo Privileges for the User Running the Script**
3. **Python 3.6 or Higher**

## Installation

Follow these steps to set up the OpenVPN Manager:

### 1. Create the OpenVPN Directory Structure

```bash
mkdir -p ~/openvpn/OpenVPN_files
```

### 2. Clone or Copy the Script

Copy the `openvpnManager.py` script to the OpenVPN directory and make it executable:

```bash
cp openvpnManager.py ~/openvpn/
chmod +x ~/openvpn/openvpnManager.py
```

### 3. Run the Installation Script

The `install.sh` script sets up a symbolic link for `openvpnManager.py` in `/usr/local/bin`, allowing you to run the OpenVPN Manager from any directory without specifying the full path.

**Steps to Run the Installation Script:**

1. **Ensure `install.sh` and `openvpnManager.py` Are in the Same Directory:**

   Navigate to your OpenVPN directory:

   ```bash
   cd ~/openvpn
   ```
2. **Make Sure the `install.sh` Script Is Executable:**

   If not already executable, modify its permissions:

   ```bash
   chmod +x install.sh
   ```
3. **Run the `install.sh` Script with `sudo`:**

   ```bash
   sudo ./install.sh
   ```

   **Explanation:**

   - **Purpose of `install.sh`:** The script creates a symbolic link (`symlink`) in `/usr/local/bin`, pointing to the `openvpnManager.py` script. This allows you to execute `openvpnManager` from any directory without needing to specify the full path to the script.
   - **Benefits:**

     - **Convenience:** Run `openvpnManager` from anywhere in the terminal.
     - **Consistency:** Ensures the script is accessible system-wide.
     - **Simplicity:** Avoids the need to remember the script's installation path.
4. **Verify the Symlink Creation:**

   After running the script, verify that the symlink was created successfully:

   ```bash
   ls -l /usr/local/bin/openvpnManager
   ```

   **Expected Output:**

   ```
   lrwxrwxrwx 1 root root 36 Dec 24 19:19 /usr/local/bin/openvpnManager -> /home/<user>/openvpn/openvpnManager.py
   ```
5. **Test the Symlink:**

   Ensure that you can run `openvpnManager` from any directory:

   ```bash
   openvpnManager
   ```

   If the script executes as expected, the installation was successful.

## Directory Structure

```
~/openvpn/
├── OpenVPN_files/        # Your .ovpn configurations
│   ├── Location1/        # Organized by location (optional)
│   │   └── config1.ovpn
│   └── Location2/
│       └── config2.ovpn
├── .credentials/         # Created automatically for storing credentials
├── openvpnManager.py     # The management script
├── install.sh            # Installation script
└── openvpn_manager.ini   # Created automatically on first run
```

## Configuration File Permissions

1. **OpenVPN Configuration Files (.ovpn):**

   ```bash
   chmod 600 ~/openvpn/OpenVPN_files/**/*.ovpn
   ```
2. **Credentials Directory (Created Automatically):**

   ```bash
   chmod 700 ~/openvpn/.credentials
   ```
3. **Credential Files (Managed by Script):**

   ```bash
   chmod 600 ~/openvpn/.credentials/*.cred
   ```

## Required System Access

The script requires:

1. **Sudo Access for OpenVPN Operations:**

   ```bash
   # Add to /etc/sudoers.d/openvpn (use visudo)
   username ALL=(ALL) NOPASSWD: /usr/sbin/openvpn
   username ALL=(ALL) NOPASSWD: /bin/kill
   ```
2. **Network Configuration Access:**

   - Ability to create/modify network interfaces
   - Ability to modify routing tables
   - Access to tun/tap devices

## Usage

1. **Place Your OpenVPN Configuration Files (.ovpn) in the `OpenVPN_files` Directory**
2. **Run the Script:**

   ```bash
   openvpnManager
   ```

   Since you've set up a symlink in `/usr/local/bin`, you can run `openvpnManager` from any directory.

### Debug Mode

- **Use Debug Mode for Troubleshooting Connection Issues**
  - Shows detailed OpenVPN output
  - Options to return to menu or exit to shell

### Regular Mode

- **Runs OpenVPN in Daemon Mode**
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

1. **Configuration Files**

   - Store `.ovpn` files with `600` permissions
   - Keep certificates and keys secure
   - Don't share credential files
2. **Credentials**

   - Stored encrypted in `.credentials` directory
   - Individual files for each configuration
   - Automatic permission management
3. **System Access**

   - Run script as a regular user
   - Use `sudo` only for necessary operations
   - Maintain proper file permissions

## Troubleshooting

1. **Connection Issues**

   - Run in debug mode to see detailed output
   - Check system logs for errors
   - Verify network configuration
2. **Permission Issues**

   - Verify file permissions
   - Check sudo configuration
   - Ensure proper user rights
3. **Common Problems**

   - Credential errors: Check saved credentials
   - Network errors: Verify network access
   - Configuration errors: Validate `.ovpn` files

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
