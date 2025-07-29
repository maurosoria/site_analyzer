import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Config:
    """Configuration class for site analyzer"""
    
    target: Optional[str] = None
    
    storage_type: str = "file"
    storage_config: Optional[Dict] = None
    
    security_trails_api_key: Optional[str] = None
    
    enabled_enumerators: Optional[List[str]] = None
    
    grpc_port: int = 50051
    rest_port: int = 5000
    
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    headless: bool = True
    timeout: int = 30000
    
    def __post_init__(self):
        if self.storage_config is None:
            self.storage_config = {}
        if self.enabled_enumerators is None:
            self.enabled_enumerators = ["web_scanner", "dns_enumeration"]
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables"""
        return cls(
            security_trails_api_key=os.getenv('SECURITY_TRAILS_API_KEY'),
            storage_type=os.getenv('STORAGE_TYPE', 'file'),
            grpc_port=int(os.getenv('GRPC_PORT', '50051')),
            rest_port=int(os.getenv('REST_PORT', '5000')),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            headless=os.getenv('HEADLESS', 'true').lower() == 'true'
        )
