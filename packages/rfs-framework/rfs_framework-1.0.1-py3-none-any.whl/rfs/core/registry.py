"""
Service Registry

서비스 등록 및 검색을 위한 레지스트리
"""

from typing import Dict, Any, Type, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class ServiceScope(Enum):
    """서비스 스코프"""
    SINGLETON = "singleton"
    PROTOTYPE = "prototype"  # 매번 새 인스턴스
    REQUEST = "request"      # 요청 별 인스턴스

@dataclass
class ServiceDefinition:
    """서비스 정의"""
    name: str
    service_class: Type
    scope: ServiceScope = ServiceScope.SINGLETON
    dependencies: List[str] = field(default_factory=list)
    lazy: bool = False
    created_at: datetime = field(default_factory=datetime.now)

class ServiceRegistry:
    """
    고급 서비스 레지스트리
    
    특징:
    - 다양한 서비스 스코프 지원
    - 순환 의존성 검출
    - 서비스 생명주기 관리
    """
    
    def __init__(self):
        self._definitions: Dict[str, ServiceDefinition] = {}
        self._instances: Dict[str, Any] = {}
        self._creating: set[str] = set()  # 순환 의존성 검출용
    
    def register(self, 
                 name: str, 
                 service_class: Type, 
                 scope: ServiceScope = ServiceScope.SINGLETON,
                 dependencies: List[str] = None,
                 lazy: bool = False) -> None:
        """서비스 등록"""
        definition = ServiceDefinition(
            name=name,
            service_class=service_class,
            scope=scope,
            dependencies=dependencies or [],
            lazy=lazy
        )
        
        self._definitions[name] = definition
        
        # 즉시 로딩 (lazy가 False인 경우)
        if not lazy and scope == ServiceScope.SINGLETON:
            self.get(name)
    
    def get(self, name: str) -> Any:
        """서비스 인스턴스 가져오기"""
        if name not in self._definitions:
            raise ValueError(f"Service '{name}' not registered")
        
        definition = self._definitions[name]
        
        if definition.scope == ServiceScope.SINGLETON:
            return self._get_singleton(name)
        elif definition.scope == ServiceScope.PROTOTYPE:
            return self._create_instance(name)
        else:
            raise NotImplementedError(f"Scope {definition.scope} not implemented")
    
    def _get_singleton(self, name: str) -> Any:
        """싱글톤 인스턴스 가져오기"""
        if name not in self._instances:
            self._instances[name] = self._create_instance(name)
        return self._instances[name]
    
    def _create_instance(self, name: str) -> Any:
        """새 인스턴스 생성"""
        if name in self._creating:
            raise ValueError(f"Circular dependency detected: {name}")
        
        self._creating.add(name)
        
        try:
            definition = self._definitions[name]
            
            # 의존성 해결
            dependencies = []
            for dep_name in definition.dependencies:
                dep_instance = self.get(dep_name)
                dependencies.append(dep_instance)
            
            # 인스턴스 생성
            instance = definition.service_class(*dependencies)
            
            return instance
            
        finally:
            self._creating.remove(name)
    
    def list_services(self) -> List[str]:
        """등록된 서비스 목록"""
        return list(self._definitions.keys())
    
    def get_definition(self, name: str) -> Optional[ServiceDefinition]:
        """서비스 정의 조회"""
        return self._definitions.get(name)
    
    def clear(self) -> None:
        """모든 서비스 정리"""
        self._instances.clear()
        self._definitions.clear()
        self._creating.clear()
    
    def health_check(self) -> Dict[str, Any]:
        """서비스 헬스체크"""
        status = {
            "total_services": len(self._definitions),
            "instantiated": len(self._instances),
            "services": {}
        }
        
        for name, definition in self._definitions.items():
            is_instantiated = name in self._instances
            status["services"][name] = {
                "scope": definition.scope.value,
                "dependencies": definition.dependencies,
                "instantiated": is_instantiated,
                "created_at": definition.created_at.isoformat() if is_instantiated else None
            }
        
        return status

# 전역 레지스트리 인스턴스
default_registry = ServiceRegistry()