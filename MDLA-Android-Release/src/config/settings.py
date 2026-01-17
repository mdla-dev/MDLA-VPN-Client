"""MDLA Android Configuration Settings"""
import os
from pathlib import Path
from kivy.utils import platform


# App info
APP_NAME = "MDLA"
APP_VERSION = "0.1.0"

# Platform detection
IS_ANDROID = platform == 'android'

# Paths - Android specific
if IS_ANDROID:
    try:
        from android.storage import primary_external_storage_path
        APP_DIR = Path(primary_external_storage_path()) / "MDLA"
    except ImportError:
        # Fallback for older Android versions
        APP_DIR = Path("/storage/emulated/0/MDLA")
else:
    # For desktop testing
    APP_DIR = Path.home() / ".mdla-android"

CONFIG_DIR = APP_DIR / "config"
CORES_DIR = APP_DIR / "cores"
LOGS_DIR = APP_DIR / "logs"


def get_logo_path() -> Path:
    """Get path to logo file"""
    if IS_ANDROID:
        # On Android, logo is bundled in the app
        return Path("logo.png")
    else:
        # Desktop testing
        return Path(__file__).parent.parent.parent / "logo.png"


def setup_android_paths():
    """Setup Android-specific paths and directories"""
    # Create directories
    for d in [APP_DIR, CONFIG_DIR, CORES_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    
    if IS_ANDROID:
        # Request storage permissions
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.INTERNET,
                Permission.ACCESS_NETWORK_STATE,
                Permission.CHANGE_NETWORK_STATE
            ])
        except ImportError:
            pass  # Not on Android


# Theme Colors (Dark Purple Theme - same as Windows)
COLORS = {
    "bg_primary": "#1E0F2F",
    "bg_secondary": "#2A1B3D", 
    "surface": "#3A2A5A",
    "accent": "#B19CD9",
    "accent_blue": "#A6D0E4",
    "accent_pink": "#F5C6D9",
    "text_primary": "#FFFFFF",
    "text_secondary": "#E0E0E0",
    "text_muted": "#999999",
    "success": "#4CAF50",
    "error": "#FF5252",
    "warning": "#FFC107",
}

# Network Settings
DEFAULT_HTTP_PORT = 10809
DEFAULT_SOCKS_PORT = 10808
DEFAULT_DNS = "8.8.8.8"

# Core binaries (Android will use different approach)
XRAY_BINARY = "libxray.so" if IS_ANDROID else "xray"
SINGBOX_BINARY = "libsingbox.so" if IS_ANDROID else "sing-box"