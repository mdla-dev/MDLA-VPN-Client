"""Protocol URL Parser - VMess, VLESS, Trojan, Shadowsocks, etc."""
import base64
import json
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class ProtocolType(Enum):
    VMESS = "vmess"
    VLESS = "vless"
    TROJAN = "trojan"
    SHADOWSOCKS = "ss"
    HYSTERIA = "hysteria"
    HYSTERIA2 = "hysteria2"
    TUIC = "tuic"
    UNKNOWN = "unknown"


@dataclass
class ServerConfig:
    """Unified server configuration"""
    name: str = ""
    protocol: ProtocolType = ProtocolType.UNKNOWN
    address: str = ""
    port: int = 443
    uuid: str = ""
    password: str = ""
    method: str = ""  # For SS
    network: str = "tcp"
    security: str = "none"
    sni: str = ""
    fingerprint: str = ""
    alpn: str = ""
    path: str = ""
    host: str = ""
    flow: str = ""  # For VLESS Reality
    public_key: str = ""  # For Reality
    short_id: str = ""  # For Reality
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "protocol": self.protocol.value,
            "address": self.address,
            "port": self.port,
            "uuid": self.uuid,
            "password": self.password,
            "method": self.method,
            "network": self.network,
            "security": self.security,
            "sni": self.sni,
            "fingerprint": self.fingerprint,
            "alpn": self.alpn,
            "path": self.path,
            "host": self.host,
            "flow": self.flow,
            "public_key": self.public_key,
            "short_id": self.short_id,
            "extra": self.extra,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerConfig":
        """Create ServerConfig from dictionary"""
        protocol_str = data.get("protocol", "unknown")
        try:
            protocol = ProtocolType(protocol_str)
        except ValueError:
            protocol = ProtocolType.UNKNOWN
        
        return cls(
            name=data.get("name", ""),
            protocol=protocol,
            address=data.get("address", ""),
            port=int(data.get("port", 443)),
            uuid=data.get("uuid", ""),
            password=data.get("password", ""),
            method=data.get("method", ""),
            network=data.get("network", "tcp"),
            security=data.get("security", "none"),
            sni=data.get("sni", ""),
            fingerprint=data.get("fingerprint", ""),
            alpn=data.get("alpn", ""),
            path=data.get("path", ""),
            host=data.get("host", ""),
            flow=data.get("flow", ""),
            public_key=data.get("public_key", ""),
            short_id=data.get("short_id", ""),
            extra=data.get("extra", {}),
        )


class ProtocolParser:
    """Parse various VPN protocol URLs"""
    
    @staticmethod
    def parse(url: str) -> Optional[ServerConfig]:
        """Parse any supported protocol URL"""
        url = url.strip()
        
        if url.startswith("vmess://"):
            return ProtocolParser._parse_vmess(url)
        elif url.startswith("vless://"):
            return ProtocolParser._parse_vless(url)
        elif url.startswith("trojan://"):
            return ProtocolParser._parse_trojan(url)
        elif url.startswith("ss://"):
            return ProtocolParser._parse_shadowsocks(url)
        elif url.startswith("hysteria://"):
            return ProtocolParser._parse_hysteria(url)
        elif url.startswith("hysteria2://") or url.startswith("hy2://"):
            return ProtocolParser._parse_hysteria2(url)
        elif url.startswith("tuic://"):
            return ProtocolParser._parse_tuic(url)
        
        return None
    
    @staticmethod
    def _parse_vmess(url: str) -> Optional[ServerConfig]:
        """Parse VMess URL (base64 encoded JSON)"""
        try:
            encoded = url.replace("vmess://", "")
            # Add padding if needed
            padding = 4 - len(encoded) % 4
            if padding != 4:
                encoded += "=" * padding
            
            decoded = base64.urlsafe_b64decode(encoded).decode("utf-8")
            data = json.loads(decoded)
            
            config = ServerConfig(
                protocol=ProtocolType.VMESS,
                name=data.get("ps", "VMess Server"),
                address=data.get("add", ""),
                port=int(data.get("port", 443)),
                uuid=data.get("id", ""),
                network=data.get("net", "tcp"),
                security=data.get("tls", "none"),
                sni=data.get("sni", ""),
                path=data.get("path", ""),
                host=data.get("host", ""),
                fingerprint=data.get("fp", ""),
                alpn=data.get("alpn", ""),
            )
            return config
        except Exception as e:
            print(f"VMess parse error: {e}")
            return None
    
    @staticmethod
    def _parse_vless(url: str) -> Optional[ServerConfig]:
        """Parse VLESS URL"""
        try:
            url = url.replace("vless://", "")
            # Split UUID and rest
            uuid_part, rest = url.split("@", 1)
            
            # Parse address:port and params
            if "#" in rest:
                addr_params, name = rest.rsplit("#", 1)
                name = urllib.parse.unquote(name)
            else:
                addr_params = rest
                name = "VLESS Server"
            
            if "?" in addr_params:
                addr_port, params_str = addr_params.split("?", 1)
                params = dict(urllib.parse.parse_qsl(params_str))
            else:
                addr_port = addr_params
                params = {}
            
            address, port = addr_port.rsplit(":", 1)
            
            config = ServerConfig(
                protocol=ProtocolType.VLESS,
                name=name,
                address=address,
                port=int(port),
                uuid=uuid_part,
                network=params.get("type", "tcp"),
                security=params.get("security", "none"),
                sni=params.get("sni", ""),
                fingerprint=params.get("fp", ""),
                alpn=params.get("alpn", ""),
                path=params.get("path", ""),
                host=params.get("host", ""),
                flow=params.get("flow", ""),
                public_key=params.get("pbk", ""),
                short_id=params.get("sid", ""),
            )
            return config
        except Exception as e:
            print(f"VLESS parse error: {e}")
            return None
    
    @staticmethod
    def _parse_trojan(url: str) -> Optional[ServerConfig]:
        """Parse Trojan URL"""
        try:
            url = url.replace("trojan://", "")
            password, rest = url.split("@", 1)
            
            if "#" in rest:
                addr_params, name = rest.rsplit("#", 1)
                name = urllib.parse.unquote(name)
            else:
                addr_params = rest
                name = "Trojan Server"
            
            if "?" in addr_params:
                addr_port, params_str = addr_params.split("?", 1)
                params = dict(urllib.parse.parse_qsl(params_str))
            else:
                addr_port = addr_params
                params = {}
            
            address, port = addr_port.rsplit(":", 1)
            
            config = ServerConfig(
                protocol=ProtocolType.TROJAN,
                name=name,
                address=address,
                port=int(port),
                password=password,
                security=params.get("security", "tls"),
                sni=params.get("sni", address),
                fingerprint=params.get("fp", ""),
                alpn=params.get("alpn", ""),
            )
            return config
        except Exception as e:
            print(f"Trojan parse error: {e}")
            return None
    
    @staticmethod
    def _parse_shadowsocks(url: str) -> Optional[ServerConfig]:
        """Parse Shadowsocks URL"""
        try:
            url = url.replace("ss://", "")
            
            if "#" in url:
                main_part, name = url.rsplit("#", 1)
                name = urllib.parse.unquote(name)
            else:
                main_part = url
                name = "Shadowsocks Server"
            
            # Try SIP002 format first (method:password@host:port)
            if "@" in main_part:
                encoded, addr_port = main_part.split("@", 1)
                padding = 4 - len(encoded) % 4
                if padding != 4:
                    encoded += "=" * padding
                decoded = base64.urlsafe_b64decode(encoded).decode("utf-8")
                method, password = decoded.split(":", 1)
                address, port = addr_port.rsplit(":", 1)
            else:
                # Legacy format (base64 encoded)
                padding = 4 - len(main_part) % 4
                if padding != 4:
                    main_part += "=" * padding
                decoded = base64.urlsafe_b64decode(main_part).decode("utf-8")
                method_pass, addr_port = decoded.rsplit("@", 1)
                method, password = method_pass.split(":", 1)
                address, port = addr_port.rsplit(":", 1)
            
            config = ServerConfig(
                protocol=ProtocolType.SHADOWSOCKS,
                name=name,
                address=address,
                port=int(port),
                password=password,
                method=method,
            )
            return config
        except Exception as e:
            print(f"Shadowsocks parse error: {e}")
            return None
    
    @staticmethod
    def _parse_hysteria(url: str) -> Optional[ServerConfig]:
        """Parse Hysteria URL"""
        try:
            url = url.replace("hysteria://", "")
            # Similar parsing logic
            config = ServerConfig(protocol=ProtocolType.HYSTERIA)
            # TODO: Implement full parsing
            return config
        except Exception:
            return None
    
    @staticmethod
    def _parse_hysteria2(url: str) -> Optional[ServerConfig]:
        """Parse Hysteria2 URL"""
        try:
            url = url.replace("hysteria2://", "").replace("hy2://", "")
            password, rest = url.split("@", 1)
            
            if "#" in rest:
                addr_params, name = rest.rsplit("#", 1)
                name = urllib.parse.unquote(name)
            else:
                addr_params = rest
                name = "Hysteria2 Server"
            
            if "?" in addr_params:
                addr_port, params_str = addr_params.split("?", 1)
                params = dict(urllib.parse.parse_qsl(params_str))
            else:
                addr_port = addr_params
                params = {}
            
            address, port = addr_port.rsplit(":", 1)
            
            config = ServerConfig(
                protocol=ProtocolType.HYSTERIA2,
                name=name,
                address=address,
                port=int(port),
                password=password,
                sni=params.get("sni", ""),
                extra={"obfs": params.get("obfs", ""), "obfs-password": params.get("obfs-password", "")}
            )
            return config
        except Exception as e:
            print(f"Hysteria2 parse error: {e}")
            return None
    
    @staticmethod
    def _parse_tuic(url: str) -> Optional[ServerConfig]:
        """Parse TUIC URL"""
        try:
            config = ServerConfig(protocol=ProtocolType.TUIC)
            # TODO: Implement full parsing
            return config
        except Exception:
            return None