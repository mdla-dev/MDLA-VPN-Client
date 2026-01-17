# MDLA VPN - Android Version

MDLA VPN Manager for Android - A powerful and user-friendly VPN client supporting multiple protocols.

## Features

- **Multi-Protocol Support**: VMess, VLESS, Trojan, Shadowsocks, Hysteria2
- **Subscription Management**: Auto-update server lists from subscription URLs
- **Real-time Statistics**: Monitor upload/download speeds and traffic
- **Server Testing**: Ping servers to check latency
- **Android VPN Service**: Native Android VPN integration
- **Dark Theme**: Beautiful purple-themed UI optimized for mobile

## Supported Protocols

- **VMess**: V2Ray protocol with various transport options
- **VLESS**: Lightweight protocol with Reality support
- **Trojan**: TLS-based proxy protocol
- **Shadowsocks**: Popular SOCKS5 proxy
- **Hysteria2**: High-performance UDP-based protocol

## Installation

### Prerequisites

1. **Python 3.8+** with pip
2. **Buildozer** for Android compilation
3. **Android SDK** and **NDK**
4. **Java JDK 8** or higher

### Setup Development Environment

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Buildozer
pip install buildozer

# Install Cython (required for compilation)
pip install cython

# Setup Android SDK (if not already installed)
# Follow Android Studio installation guide
```

### Building APK

```bash
# Initialize buildozer (first time only)
buildozer init

# Build debug APK
buildozer android debug

# Build release APK (requires signing)
buildozer android release
```

### Development Testing

For desktop testing during development:

```bash
# Install desktop Kivy dependencies
pip install kivy[base]

# Run on desktop
python main.py
```

## Project Structure

```
mdla-android/
├── main.py                 # Application entry point
├── buildozer.spec         # Android build configuration
├── requirements.txt       # Python dependencies
├── src/
│   ├── config/
│   │   └── settings.py    # App configuration
│   ├── core/              # Core VPN logic (reused from Windows)
│   │   ├── protocol_parser.py
│   │   ├── subscription.py
│   │   ├── core_manager.py
│   │   ├── traffic_monitor.py
│   │   └── speed_test.py
│   └── ui/                # Kivy UI components
│       ├── main_screen.py
│       ├── components.py
│       └── theme.py
```

## Usage

### Adding Servers

1. **Single Server**: Paste server URL (vmess://, vless://, trojan://, ss://)
2. **Subscription**: Add subscription URL for automatic server updates
3. **Bulk Import**: Paste multiple server URLs (one per line)

### Connecting

1. Select a server from the list
2. Tap "Connect" button
3. Grant VPN permission when prompted
4. Monitor connection status and traffic statistics

### Server Management

- **Ping Test**: Check server latency
- **Auto-Update**: Subscriptions update automatically
- **Manual Refresh**: Update subscriptions manually
- **Delete**: Remove subscriptions or servers

## Android Permissions

The app requires the following permissions:

- `INTERNET` - Network access
- `ACCESS_NETWORK_STATE` - Check network status
- `CHANGE_NETWORK_STATE` - Modify network settings
- `BIND_VPN_SERVICE` - Create VPN connections
- `WRITE_EXTERNAL_STORAGE` - Save configuration files
- `READ_EXTERNAL_STORAGE` - Read configuration files

## Configuration

### App Settings

- **VPN Mode**: TUN mode (recommended for Android)
- **Local Proxy**: HTTP and SOCKS5 proxy ports
- **Auto-Update**: Subscription update intervals

### File Locations

- **Config**: `/storage/emulated/0/MDLA/config/`
- **Logs**: `/storage/emulated/0/MDLA/logs/`
- **Cores**: `/storage/emulated/0/MDLA/cores/`

## Development

### Code Reuse from Windows Version

The Android version reuses 90% of the core logic from the Windows version:

- **Protocol Parser**: Identical URL parsing logic
- **Subscription Manager**: Same subscription handling
- **Traffic Monitor**: Adapted for Android VPN interface
- **Speed Test**: Same ping and speed test logic

### Android-Specific Adaptations

- **UI Framework**: Kivy instead of CustomTkinter
- **VPN Integration**: Android VpnService API
- **File Paths**: Android external storage
- **Permissions**: Android permission system
- **Notifications**: Android notification system

### Building for Production

1. **Generate Keystore**:
```bash
keytool -genkey -v -keystore mdla-release-key.keystore -alias mdla -keyalg RSA -keysize 2048 -validity 10000
```

2. **Configure Signing** in `buildozer.spec`:
```ini
[app]
android.release_artifact = aab
android.debug_artifact = apk

[buildozer]
android.keystore = mdla-release-key.keystore
android.keyalias = mdla
```

3. **Build Release**:
```bash
buildozer android release
```

## Troubleshooting

### Common Issues

1. **Build Errors**: Ensure all dependencies are installed
2. **VPN Permission**: Grant VPN permission in Android settings
3. **Network Issues**: Check internet connection and firewall
4. **Core Not Found**: Ensure VPN core is properly bundled

### Debug Mode

Enable debug logging in `src/config/settings.py`:

```python
DEBUG = True
LOG_LEVEL = "DEBUG"
```

### Logs

Check application logs:
```bash
# During development
adb logcat | grep python

# In app logs directory
/storage/emulated/0/MDLA/logs/
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test on Android device/emulator
5. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For issues and support:
- Check existing issues in the repository
- Create new issue with detailed description
- Include device information and logs