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
    
    llm_provider: str = "gemini"  # "gemini", "openai", "bedrock"
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    aws_bedrock_url: Optional[str] = None
    aws_region: str = "us-east-1"
    llm_model: str = "gemini-2.0-flash-exp"
    
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
            headless=os.getenv('HEADLESS', 'true').lower() == 'true',
            llm_provider=os.getenv('LLM_PROVIDER', 'gemini'),
            gemini_api_key=os.getenv('GEMINI_API_KEY'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            aws_bedrock_url=os.getenv('AWS_BEDROCK_URL'),
            aws_region=os.getenv('AWS_REGION', 'us-east-1'),
            llm_model=os.getenv('LLM_MODEL', 'gemini-2.0-flash-exp')
        )
