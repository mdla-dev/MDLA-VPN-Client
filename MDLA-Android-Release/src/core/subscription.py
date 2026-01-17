"""Subscription Manager - Handle subscription URLs and updates"""
import asyncio
import base64
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import aiohttp

from .protocol_parser import ProtocolParser, ServerConfig
from ..config.settings import CONFIG_DIR


@dataclass
class Subscription:
    """Subscription data"""
    id: str
    name: str
    url: str
    servers: List[ServerConfig] = field(default_factory=list)
    last_update: Optional[datetime] = None
    auto_update: bool = True
    update_interval: int = 3600  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "servers": [s.to_dict() for s in self.servers],
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "auto_update": self.auto_update,
            "update_interval": self.update_interval,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Subscription":
        sub = cls(
            id=data["id"],
            name=data["name"],
            url=data["url"],
            auto_update=data.get("auto_update", True),
            update_interval=data.get("update_interval", 3600),
        )
        if data.get("last_update"):
            sub.last_update = datetime.fromisoformat(data["last_update"])
        return sub


class SubscriptionManager:
    """Manage VPN subscriptions"""
    
    def __init__(self):
        self._subscriptions: Dict[str, Subscription] = {}
        self._servers: List[ServerConfig] = []
        self._data_file = CONFIG_DIR / "subscriptions.json"
        self._load()
    
    def _load(self):
        """Load subscriptions from file"""
        if self._data_file.exists():
            try:
                with open(self._data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Load subscriptions
                for sub_data in data.get("subscriptions", []):
                    sub = Subscription.from_dict(sub_data)
                    # Also load servers for this subscription
                    for srv_data in sub_data.get("servers", []):
                        try:
                            srv = ServerConfig.from_dict(srv_data)
                            sub.servers.append(srv)
                        except Exception:
                            pass
                    self._subscriptions[sub.id] = sub
                
                # Load manually added servers
                for srv_data in data.get("servers", []):
                    try:
                        srv = ServerConfig.from_dict(srv_data)
                        self._servers.append(srv)
                    except Exception:
                        pass
                        
            except Exception as e:
                print(f"Failed to load subscriptions: {e}")
    
    def _save(self):
        """Save subscriptions to file"""
        try:
            data = {
                "subscriptions": [s.to_dict() for s in self._subscriptions.values()],
                "servers": [s.to_dict() for s in self._servers]  # Save manual servers too
            }
            with open(self._data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save subscriptions: {e}")
    
    def add_subscription(self, name: str, url: str) -> Subscription:
        """Add a new subscription"""
        import uuid
        sub_id = str(uuid.uuid4())[:8]
        sub = Subscription(id=sub_id, name=name, url=url)
        self._subscriptions[sub_id] = sub
        self._save()
        return sub
    
    def remove_subscription(self, sub_id: str) -> bool:
        """Remove a subscription"""
        if sub_id in self._subscriptions:
            del self._subscriptions[sub_id]
            self._save()
            return True
        return False
    
    def get_subscriptions(self) -> List[Subscription]:
        """Get all subscriptions"""
        return list(self._subscriptions.values())
    
    def get_all_servers(self) -> List[ServerConfig]:
        """Get all servers from all subscriptions"""
        servers = []
        for sub in self._subscriptions.values():
            servers.extend(sub.servers)
        servers.extend(self._servers)  # Add manually added servers
        return servers
    
    async def update_subscription(self, sub_id: str) -> bool:
        """Update a single subscription"""
        if sub_id not in self._subscriptions:
            return False
        
        sub = self._subscriptions[sub_id]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(sub.url, timeout=30) as response:
                    if response.status != 200:
                        return False
                    
                    content = await response.text()
                    
                    # Try to decode base64
                    try:
                        decoded = base64.b64decode(content).decode("utf-8")
                        lines = decoded.strip().split("\n")
                    except Exception:
                        lines = content.strip().split("\n")
                    
                    # Parse each line
                    servers = []
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        config = ProtocolParser.parse(line)
                        if config:
                            servers.append(config)
                    
                    sub.servers = servers
                    sub.last_update = datetime.now()
                    self._save()
                    return True
                    
        except Exception as e:
            print(f"Failed to update subscription {sub.name}: {e}")
            return False
    
    async def update_all_subscriptions(self) -> Dict[str, bool]:
        """Update all subscriptions"""
        results = {}
        tasks = []
        
        for sub_id in self._subscriptions:
            tasks.append(self.update_subscription(sub_id))
        
        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            for sub_id, result in zip(self._subscriptions.keys(), task_results):
                results[sub_id] = result if isinstance(result, bool) else False
        
        return results
    
    def add_server_from_url(self, url: str) -> Optional[ServerConfig]:
        """Add a single server from URL"""
        config = ProtocolParser.parse(url)
        if config:
            self._servers.append(config)
            self._save()
        return config
    
    def add_server_from_clipboard(self, text: str) -> List[ServerConfig]:
        """Add servers from clipboard text (may contain multiple URLs)"""
        added = []
        lines = text.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            config = ProtocolParser.parse(line)
            if config:
                self._servers.append(config)
                added.append(config)
        
        if added:
            self._save()
        
        return added