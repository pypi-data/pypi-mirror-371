"""
Configuration Management

환경 변수 및 설정 관리
"""

import os
from typing import Dict, Any, Optional, Type, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml
from enum import Enum

class Environment(Enum):
    """실행 환경"""
    DEVELOPMENT = "development"
    TEST = "test" 
    PRODUCTION = "production"

@dataclass
class RFSConfig:
    """RFS Framework 설정"""
    environment: Environment = Environment.DEVELOPMENT
    
    # Reactive 설정
    default_buffer_size: int = 100
    max_concurrency: int = 10
    
    # 서버리스 설정
    enable_cold_start_optimization: bool = True
    cloud_run_max_instances: int = 100
    cloud_tasks_queue_name: str = "default-queue"
    
    # 이벤트 설정
    redis_url: str = "redis://localhost:6379"
    event_store_enabled: bool = True
    
    # 로깅 설정
    log_level: str = "INFO"
    log_format: str = "json"
    
    # 보안 설정
    enable_tracing: bool = False
    api_key_header: str = "X-API-Key"
    
    # 커스텀 설정
    custom: Dict[str, Any] = field(default_factory=dict)

class ConfigManager:
    """설정 관리자"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._config: Optional[RFSConfig] = None
        self._env_prefix = "RFS_"
    
    def load_config(self) -> RFSConfig:
        """설정 로드"""
        if self._config is not None:
            return self._config
        
        # 기본 설정으로 시작
        config_dict = {}
        
        # 파일에서 설정 로드
        if self.config_path and Path(self.config_path).exists():
            config_dict = self._load_from_file(self.config_path)
        
        # 환경 변수로 덮어쓰기
        env_config = self._load_from_env()
        config_dict.update(env_config)
        
        # RFSConfig 인스턴스 생성
        self._config = self._create_config(config_dict)
        
        return self._config
    
    def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """파일에서 설정 로드"""
        path = Path(file_path)
        
        if path.suffix.lower() == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        elif path.suffix.lower() in ['.yml', '.yaml']:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")
    
    def _load_from_env(self) -> Dict[str, Any]:
        """환경 변수에서 설정 로드"""
        config = {}
        
        for key, value in os.environ.items():
            if key.startswith(self._env_prefix):
                # RFS_LOG_LEVEL -> log_level
                config_key = key[len(self._env_prefix):].lower()
                config[config_key] = self._convert_env_value(value)
        
        return config
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """환경 변수 값 변환"""
        # Boolean 변환
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False
        
        # 숫자 변환 시도
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # 문자열로 반환
        return value
    
    def _create_config(self, config_dict: Dict[str, Any]) -> RFSConfig:
        """설정 딕셔너리를 RFSConfig로 변환"""
        # 환경 설정
        env_str = config_dict.get('environment', 'development')
        if isinstance(env_str, str):
            try:
                environment = Environment(env_str.lower())
            except ValueError:
                environment = Environment.DEVELOPMENT
        else:
            environment = env_str
        
        return RFSConfig(
            environment=environment,
            default_buffer_size=config_dict.get('default_buffer_size', 100),
            max_concurrency=config_dict.get('max_concurrency', 10),
            enable_cold_start_optimization=config_dict.get('enable_cold_start_optimization', True),
            cloud_run_max_instances=config_dict.get('cloud_run_max_instances', 100),
            cloud_tasks_queue_name=config_dict.get('cloud_tasks_queue_name', 'default-queue'),
            redis_url=config_dict.get('redis_url', 'redis://localhost:6379'),
            event_store_enabled=config_dict.get('event_store_enabled', True),
            log_level=config_dict.get('log_level', 'INFO'),
            log_format=config_dict.get('log_format', 'json'),
            enable_tracing=config_dict.get('enable_tracing', False),
            api_key_header=config_dict.get('api_key_header', 'X-API-Key'),
            custom=config_dict.get('custom', {})
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값 조회"""
        config = self.load_config()
        return getattr(config, key, default)
    
    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.load_config().environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """운영 환경 여부"""
        return self.load_config().environment == Environment.PRODUCTION
    
    def is_test(self) -> bool:
        """테스트 환경 여부"""
        return self.load_config().environment == Environment.TEST

# 전역 설정 관리자
config_manager = ConfigManager()

# 편의 함수들
def get_config() -> RFSConfig:
    """현재 설정 조회"""
    return config_manager.load_config()

def get(key: str, default: Any = None) -> Any:
    """설정 값 조회"""
    return config_manager.get(key, default)