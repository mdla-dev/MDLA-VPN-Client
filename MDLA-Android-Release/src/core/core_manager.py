"""Android Core Manager - Manages VPN through Android VpnService"""
import asyncio
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

from ..config.settings import IS_ANDROID
from .vpn_service import AndroidVPNService
from .traffic_monitor import TrafficMonitor


class CoreType(Enum):
    XRAY = "xray"
    SINGBOX = "sing-box"


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


@dataclass
class CoreStatus:
    state: ConnectionState = ConnectionState.DISCONNECTED
    core_type: Optional[CoreType] = None
    pid: Optional[int] = None
    upload_speed: float = 0.0
    download_speed: float = 0.0
    total_upload: int = 0
    total_download: int = 0
    error_message: str = ""


class AndroidCoreManager:
    """Manages VPN core processes on Android using VpnService"""
    
    def __init__(self):
        self._status = CoreStatus()
        self._on_status_change: Optional[Callable[[CoreStatus], None]] = None
        self._monitor_task: Optional[asyncio.Task] = None
        self._traffic_monitor = TrafficMonitor()
        self._vpn_service = AndroidVPNService()
        
        # Setup callbacks
        self._vpn_service.set_status_callback(self._on_vpn_status_change)
        self._vpn_service.set_traffic_callback(self._on_vpn_traffic_update)
    
    @property
    def status(self) -> CoreStatus:
        return self._status
    
    def set_status_callback(self, callback: Callable[[CoreStatus], None]):
        """Set callback for status changes"""
        self._on_status_change = callback
    
    def set_traffic_callback(self, callback: Callable[[Any], None]):
        """Set callback for traffic stats"""
        self._traffic_monitor.set_callback(callback)
    
    def _notify_status(self):
        """Notify status change"""
        if self._on_status_change:
            self._on_status_change(self._status)
    
    def _on_vpn_status_change(self, status_info: Dict[str, Any]):
        """Handle VPN service status changes"""
        if status_info.get("connected"):
            self._status.state = ConnectionState.CONNECTED
        else:
            self._status.state = ConnectionState.DISCONNECTED
        
        self._notify_status()
    
    def _on_vpn_traffic_update(self, stats: Dict[str, Any]):
        """Handle VPN traffic updates"""
        self._status.upload_speed = stats.get("upload_speed", 0)
        self._status.download_speed = stats.get("download_speed", 0)
        self._status.total_upload = stats.get("total_upload", 0)
        self._status.total_download = stats.get("total_download", 0)
        
        # Also update traffic monitor
        from .traffic_monitor import TrafficStats
        traffic_stats = TrafficStats(
            upload_speed=self._status.upload_speed,
            download_speed=self._status.download_speed,
            total_upload=self._status.total_upload,
            total_download=self._status.total_download
        )
        
        if self._traffic_monitor._callback:
            self._traffic_monitor._callback(traffic_stats)
    
    def is_core_available(self, core_type: CoreType) -> bool:
        """Check if core is available on Android"""
        return True  # Assume available
    
    async def start(self, server_config: Dict[str, Any], 
                    core_type: CoreType = CoreType.XRAY,
                    use_tun: bool = True) -> bool:
        """Start VPN connection on Android"""
        if self._status.state == ConnectionState.CONNECTED:
            await self.stop()
        
        self._status.state = ConnectionState.CONNECTING
        self._status.core_type = core_type
        self._notify_status()
        
        try:
            # Start VPN service
            success = self._vpn_service.start_vpn(server_config)
            
            if success:
                self._status.state = ConnectionState.CONNECTED
                self._status.error_message = ""
                
                # Start traffic monitoring
                await self._traffic_monitor.start_monitoring()
                
                self._notify_status()
                return True
            else:
                self._status.state = ConnectionState.ERROR
                self._status.error_message = "Failed to start VPN service"
                self._notify_status()
                return False
                
        except Exception as e:
            self._status.state = ConnectionState.ERROR
            self._status.error_message = str(e)
            self._notify_status()
            return False
    
    async def stop(self) -> bool:
        """Stop VPN connection"""
        if self._status.state == ConnectionState.DISCONNECTED:
            return True
        
        self._status.state = ConnectionState.DISCONNECTING
        self._notify_status()
        
        try:
            if self._monitor_task:
                self._monitor_task.cancel()
                self._monitor_task = None
            
            # Stop traffic monitoring
            await self._traffic_monitor.stop_monitoring()
            
            # Stop VPN service
            success = self._vpn_service.stop_vpn()
            
            if success:
                self._status.state = ConnectionState.DISCONNECTED
                self._status.pid = None
                self._notify_status()
                return True
            else:
                self._status.state = ConnectionState.ERROR
                self._status.error_message = "Failed to stop VPN service"
                self._notify_status()
                return False
            
        except Exception as e:
            self._status.state = ConnectionState.ERROR
            self._status.error_message = str(e)
            self._notify_status()
            return False
    
    def get_proxy_settings(self) -> Dict[str, Any]:
        """Get current proxy settings"""
        return {
            "http": "http://127.0.0.1:10809",
            "socks5": "socks5://127.0.0.1:10808"
        }