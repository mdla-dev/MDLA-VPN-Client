"""Enhanced Android VPN Service Integration"""
import json
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from kivy.utils import platform
from kivy.logger import Logger

from ..config.settings import IS_ANDROID, CORES_DIR, LOGS_DIR


class AndroidVPNService:
    """Enhanced Android VPN Service with Xray integration"""
    
    def __init__(self):
        self.is_running = False
        self.vpn_process: Optional[subprocess.Popen] = None
        self.config_file: Optional[Path] = None
        self.status_callback: Optional[Callable] = None
        self.traffic_callback: Optional[Callable] = None
        self._monitor_thread: Optional[threading.Thread] = None
        
        if IS_ANDROID:
            self._setup_android()
    
    def _setup_android(self):
        """Setup Android-specific components"""
        try:
            from jnius import autoclass
            
            # Android VPN classes
            self.VpnService = autoclass('android.net.VpnService')
            self.Intent = autoclass('android.content.Intent')
            self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.ParcelFileDescriptor = autoclass('android.os.ParcelFileDescriptor')
            
            # Network classes
            self.InetAddress = autoclass('java.net.InetAddress')
            
            self.activity = self.PythonActivity.mActivity
            Logger.info("MDLA: Android VPN classes loaded successfully")
            
        except ImportError as e:
            Logger.error(f"MDLA: Failed to load Android classes: {e}")
    
    def request_vpn_permission(self) -> bool:
        """Request VPN permission from Android system"""
        if not IS_ANDROID:
            return True
        
        try:
            intent = self.VpnService.prepare(self.activity)
            if intent is None:
                Logger.info("MDLA: VPN permission already granted")
                return True
            else:
                Logger.info("MDLA: VPN permission required")
                # In real implementation, would show permission dialog
                return False
        except Exception as e:
            Logger.error(f"MDLA: Error requesting VPN permission: {e}")
            return False
    
    def create_xray_config(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Xray configuration optimized for Android"""
        config = {
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [
                {
                    "tag": "tun-in",
                    "port": 1080,
                    "protocol": "socks",
                    "settings": {
                        "auth": "noauth",
                        "udp": True,
                        "userLevel": 0
                    },
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"]
                    }
                }
            ],
            "outbounds": [
                self._build_outbound(server_config),
                {
                    "tag": "direct",
                    "protocol": "freedom"
                },
                {
                    "tag": "block",
                    "protocol": "blackhole"
                }
            ],
            "routing": {
                "domainStrategy": "IPIfNonMatch",
                "rules": [
                    {
                        "type": "field",
                        "ip": ["geoip:private"],
                        "outboundTag": "direct"
                    },
                    {
                        "type": "field",
                        "ip": ["geoip:cn"],
                        "outboundTag": "direct"
                    }
                ]
            }
        }
        
        return config
    
    def _build_outbound(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build outbound configuration for server"""
        protocol = server_config.get("protocol", "vmess")
        address = server_config.get("address", "")
        port = server_config.get("port", 443)
        
        outbound = {
            "tag": "proxy",
            "protocol": protocol,
            "settings": {},
            "streamSettings": {
                "network": server_config.get("network", "tcp")
            }
        }
        
        # Protocol-specific settings
        if protocol == "vmess":
            outbound["settings"] = {
                "vnext": [{
                    "address": address,
                    "port": port,
                    "users": [{
                        "id": server_config.get("uuid", ""),
                        "alterId": 0,
                        "security": "auto"
                    }]
                }]
            }
        elif protocol == "vless":
            outbound["settings"] = {
                "vnext": [{
                    "address": address,
                    "port": port,
                    "users": [{
                        "id": server_config.get("uuid", ""),
                        "encryption": "none",
                        "flow": server_config.get("flow", "")
                    }]
                }]
            }
        elif protocol == "trojan":
            outbound["settings"] = {
                "servers": [{
                    "address": address,
                    "port": port,
                    "password": server_config.get("password", "")
                }]
            }
        elif protocol == "shadowsocks":
            outbound["protocol"] = "shadowsocks"
            outbound["settings"] = {
                "servers": [{
                    "address": address,
                    "port": port,
                    "method": server_config.get("method", "aes-256-gcm"),
                    "password": server_config.get("password", "")
                }]
            }
        
        # Stream settings
        network = server_config.get("network", "tcp")
        security = server_config.get("security", "none")
        
        if network == "ws":
            outbound["streamSettings"]["wsSettings"] = {
                "path": server_config.get("path", "/"),
                "headers": {"Host": server_config.get("host", "")}
            }
        elif network == "grpc":
            outbound["streamSettings"]["grpcSettings"] = {
                "serviceName": server_config.get("path", "")
            }
        
        if security == "tls":
            outbound["streamSettings"]["security"] = "tls"
            outbound["streamSettings"]["tlsSettings"] = {
                "serverName": server_config.get("sni", address),
                "fingerprint": server_config.get("fingerprint", "chrome")
            }
        elif security == "reality":
            outbound["streamSettings"]["security"] = "reality"
            outbound["streamSettings"]["realitySettings"] = {
                "serverName": server_config.get("sni", ""),
                "fingerprint": server_config.get("fingerprint", "chrome"),
                "publicKey": server_config.get("public_key", ""),
                "shortId": server_config.get("short_id", "")
            }
        
        return outbound
    
    def start_vpn(self, server_config: Dict[str, Any]) -> bool:
        """Start VPN connection"""
        if self.is_running:
            self.stop_vpn()
        
        try:
            # Create Xray config
            config = self.create_xray_config(server_config)
            
            # Save config file
            self.config_file = CORES_DIR / "android_config.json"
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            if IS_ANDROID:
                # Start Android VPN service
                success = self._start_android_vpn()
            else:
                # Desktop testing mode
                success = self._start_desktop_mode()
            
            if success:
                self.is_running = True
                self._start_monitoring()
                Logger.info("MDLA: VPN started successfully")
                return True
            else:
                Logger.error("MDLA: Failed to start VPN")
                return False
                
        except Exception as e:
            Logger.error(f"MDLA: Error starting VPN: {e}")
            return False
    
    def _start_android_vpn(self) -> bool:
        """Start VPN on Android using native service"""
        try:
            # Check permission
            if not self.request_vpn_permission():
                return False
            
            # Start Xray process (would need embedded binary)
            # For now, simulate successful start
            Logger.info("MDLA: Android VPN service started (simulated)")
            
            # In real implementation:
            # 1. Create VPN interface using VpnService.Builder
            # 2. Configure routing and DNS
            # 3. Start Xray process with TUN interface
            # 4. Handle traffic routing
            
            return True
            
        except Exception as e:
            Logger.error(f"MDLA: Android VPN start error: {e}")
            return False
    
    def _start_desktop_mode(self) -> bool:
        """Start VPN in desktop testing mode"""
        try:
            # For desktop testing, just simulate
            Logger.info("MDLA: Desktop VPN mode started (simulated)")
            return True
        except Exception as e:
            Logger.error(f"MDLA: Desktop VPN error: {e}")
            return False
    
    def stop_vpn(self) -> bool:
        """Stop VPN connection"""
        if not self.is_running:
            return True
        
        try:
            self.is_running = False
            
            # Stop monitoring
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=2)
            
            # Stop VPN process
            if self.vpn_process:
                self.vpn_process.terminate()
                self.vpn_process.wait(timeout=5)
                self.vpn_process = None
            
            Logger.info("MDLA: VPN stopped successfully")
            return True
            
        except Exception as e:
            Logger.error(f"MDLA: Error stopping VPN: {e}")
            return False
    
    def _start_monitoring(self):
        """Start monitoring VPN status and traffic"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def _monitor_loop(self):
        """Monitor VPN connection and traffic"""
        upload_total = 0
        download_total = 0
        last_time = time.time()
        
        while self.is_running:
            try:
                current_time = time.time()
                time_diff = current_time - last_time
                
                if time_diff >= 1.0:  # Update every second
                    # Simulate traffic stats
                    import random
                    upload_speed = random.uniform(0, 1024 * 100)  # 0-100KB/s
                    download_speed = random.uniform(0, 1024 * 500)  # 0-500KB/s
                    
                    upload_total += int(upload_speed * time_diff)
                    download_total += int(download_speed * time_diff)
                    
                    # Call traffic callback
                    if self.traffic_callback:
                        stats = {
                            'upload_speed': upload_speed,
                            'download_speed': download_speed,
                            'total_upload': upload_total,
                            'total_download': download_total
                        }
                        self.traffic_callback(stats)
                    
                    last_time = current_time
                
                time.sleep(0.5)
                
            except Exception as e:
                Logger.error(f"MDLA: Monitor error: {e}")
                break
    
    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def set_traffic_callback(self, callback: Callable):
        """Set callback for traffic updates"""
        self.traffic_callback = callback
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection information"""
        return {
            "connected": self.is_running,
            "config_file": str(self.config_file) if self.config_file else None,
            "process_id": self.vpn_process.pid if self.vpn_process else None
        }