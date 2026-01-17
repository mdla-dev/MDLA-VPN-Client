"""Traffic Monitor - Monitor VPN traffic statistics"""
import asyncio
from typing import Optional, Callable, Any
from dataclasses import dataclass


@dataclass
class TrafficStats:
    """Traffic statistics"""
    upload_speed: float = 0.0  # bytes/sec
    download_speed: float = 0.0  # bytes/sec
    total_upload: int = 0  # total bytes
    total_download: int = 0  # total bytes


class TrafficMonitor:
    """Monitor VPN traffic statistics"""
    
    def __init__(self):
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._callback: Optional[Callable[[TrafficStats], None]] = None
        self._stats = TrafficStats()
        self._last_upload = 0
        self._last_download = 0
    
    def set_callback(self, callback: Callable[[TrafficStats], None]):
        """Set callback for traffic updates"""
        self._callback = callback
    
    async def start_monitoring(self):
        """Start monitoring traffic"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def stop_monitoring(self):
        """Stop monitoring traffic"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            self._monitor_task = None
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        try:
            while self._monitoring:
                await self._update_stats()
                if self._callback:
                    self._callback(self._stats)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Traffic monitor error: {e}")
    
    async def _update_stats(self):
        """Update traffic statistics"""
        try:
            # TODO: Implement actual traffic monitoring
            # On Android, this would read from VPN interface statistics
            # For now, simulate some traffic
            
            # Mock traffic data
            import random
            
            # Simulate upload/download speeds (bytes/sec)
            if self._monitoring:
                self._stats.upload_speed = random.uniform(0, 1024 * 100)  # 0-100KB/s
                self._stats.download_speed = random.uniform(0, 1024 * 500)  # 0-500KB/s
                
                # Update totals
                self._stats.total_upload += int(self._stats.upload_speed)
                self._stats.total_download += int(self._stats.download_speed)
            else:
                self._stats.upload_speed = 0
                self._stats.download_speed = 0
                
        except Exception as e:
            print(f"Failed to update traffic stats: {e}")
    
    @staticmethod
    def format_speed(bytes_per_sec: float) -> str:
        """Format speed in human readable format"""
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.0f} B/s"
        elif bytes_per_sec < 1024 * 1024:
            return f"{bytes_per_sec / 1024:.1f} KB/s"
        elif bytes_per_sec < 1024 * 1024 * 1024:
            return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"
        else:
            return f"{bytes_per_sec / (1024 * 1024 * 1024):.1f} GB/s"
    
    @staticmethod
    def format_bytes(total_bytes: int) -> str:
        """Format total bytes in human readable format"""
        if total_bytes < 1024:
            return f"{total_bytes} B"
        elif total_bytes < 1024 * 1024:
            return f"{total_bytes / 1024:.1f} KB"
        elif total_bytes < 1024 * 1024 * 1024:
            return f"{total_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{total_bytes / (1024 * 1024 * 1024):.1f} GB"