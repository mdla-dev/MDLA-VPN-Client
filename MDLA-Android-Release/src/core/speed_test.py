"""Speed Test - Test server latency and speed"""
import asyncio
import time
import socket
from typing import List, Tuple, Dict, Any


class SpeedTester:
    """Test server speed and latency"""
    
    @staticmethod
    async def ping_server(server_config: Dict[str, Any], timeout: float = 5.0) -> float:
        """Ping a single server and return latency in ms"""
        address = server_config.get("address", "")
        port = server_config.get("port", 443)
        
        if not address:
            return -1
        
        try:
            start_time = time.time()
            
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((address, port))
            sock.close()
            
            end_time = time.time()
            
            if result == 0:
                latency = (end_time - start_time) * 1000  # Convert to ms
                return latency
            else:
                return -1
                
        except Exception:
            return -1
    
    @staticmethod
    async def batch_ping(server_configs: List[Dict[str, Any]], 
                        timeout: float = 5.0) -> List[Tuple[int, float]]:
        """Ping multiple servers concurrently"""
        tasks = []
        
        for i, config in enumerate(server_configs):
            task = asyncio.create_task(SpeedTester.ping_server(config, timeout))
            tasks.append((i, task))
        
        results = []
        for i, task in tasks:
            try:
                latency = await task
                results.append((i, latency))
            except Exception:
                results.append((i, -1))
        
        return results
    
    @staticmethod
    async def speed_test(server_config: Dict[str, Any]) -> Dict[str, float]:
        """Test download/upload speed through server"""
        # TODO: Implement actual speed test
        # This would involve:
        # 1. Connecting through the VPN
        # 2. Downloading/uploading test data
        # 3. Measuring throughput
        
        return {
            "download_speed": 0.0,  # Mbps
            "upload_speed": 0.0,    # Mbps
            "latency": await SpeedTester.ping_server(server_config)
        }