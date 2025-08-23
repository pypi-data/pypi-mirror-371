"""
Mono - Reactive Stream for 0-1 items

Inspired by Spring Reactor Mono
"""

from typing import TypeVar, Generic, Callable, Optional, Any
import asyncio

T = TypeVar('T')
R = TypeVar('R')

class Mono(Generic[T]):
    """
    0 또는 1개의 데이터만 방출하는 리액티브 스트림
    
    Spring Reactor의 Mono를 Python으로 구현
    """
    
    def __init__(self, source: Callable[[], Optional[T]] = None):
        self.source = source or (lambda: None)
    
    @staticmethod
    def just(value: T) -> 'Mono[T]':
        """단일 값으로 Mono 생성"""
        async def generator():
            return value
        return Mono(generator)
    
    @staticmethod
    def empty() -> 'Mono[None]':
        """빈 Mono 생성"""
        async def generator():
            return None
        return Mono(generator)
    
    @staticmethod
    def from_callable(callable_func: Callable[[], T]) -> 'Mono[T]':
        """Callable로부터 Mono 생성"""
        async def generator():
            return callable_func()
        return Mono(generator)
    
    @staticmethod
    def delay(duration: float, value: T = None) -> 'Mono[T]':
        """지연된 값을 방출하는 Mono"""
        async def generator():
            await asyncio.sleep(duration)
            return value
        return Mono(generator)
    
    def map(self, mapper: Callable[[T], R]) -> 'Mono[R]':
        """값 변환"""
        async def mapped():
            value = await self.source()
            return mapper(value) if value is not None else None
        return Mono(mapped)
    
    def flat_map(self, mapper: Callable[[T], 'Mono[R]']) -> 'Mono[R]':
        """Mono를 반환하는 함수로 변환"""
        async def flat_mapped():
            value = await self.source()
            if value is not None:
                inner_mono = mapper(value)
                return await inner_mono.source()
            return None
        return Mono(flat_mapped)
    
    def filter(self, predicate: Callable[[T], bool]) -> 'Mono[T]':
        """조건 필터링"""
        async def filtered():
            value = await self.source()
            return value if value is not None and predicate(value) else None
        return Mono(filtered)
    
    def default_if_empty(self, default_value: T) -> 'Mono[T]':
        """비어있을 때 기본값 반환"""
        async def with_default():
            value = await self.source()
            return value if value is not None else default_value
        return Mono(with_default)
    
    def switch_if_empty(self, alternative: 'Mono[T]') -> 'Mono[T]':
        """비어있을 때 대안 Mono로 전환"""
        async def switched():
            value = await self.source()
            if value is not None:
                return value
            return await alternative.source()
        return Mono(switched)
    
    def or_else(self, alternative: T) -> 'Mono[T]':
        """비어있을 때 대안 값 반환"""
        return self.default_if_empty(alternative)
    
    def zip_with(self, other: 'Mono[R]') -> 'Mono[tuple[T, R]]':
        """다른 Mono와 결합"""
        async def zipped():
            value1 = await self.source()
            value2 = await other.source()
            if value1 is not None and value2 is not None:
                return (value1, value2)
            return None
        return Mono(zipped)
    
    def then(self, next_mono: 'Mono[R]') -> 'Mono[R]':
        """현재 Mono 완료 후 다음 Mono 실행"""
        async def chained():
            await self.source()  # 현재 Mono 완료 대기
            return await next_mono.source()
        return Mono(chained)
    
    def timeout(self, duration: float) -> 'Mono[T]':
        """타임아웃 설정"""
        async def with_timeout():
            try:
                return await asyncio.wait_for(self.source(), timeout=duration)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Mono timed out after {duration} seconds")
        return Mono(with_timeout)
    
    def retry(self, max_attempts: int = 3) -> 'Mono[T]':
        """재시도 설정"""
        async def with_retry():
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await self.source()
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(0.1 * (attempt + 1))  # 지수 백오프
                    continue
            raise last_exception or Exception("Max retry attempts exceeded")
        return Mono(with_retry)
    
    def on_error_return(self, fallback_value: T) -> 'Mono[T]':
        """에러 시 대체 값 반환"""
        async def with_error_fallback():
            try:
                return await self.source()
            except Exception:
                return fallback_value
        return Mono(with_error_fallback)
    
    def on_error_resume(self, fallback_mono: 'Mono[T]') -> 'Mono[T]':
        """에러 시 대체 Mono로 전환"""
        async def with_error_resume():
            try:
                return await self.source()
            except Exception:
                return await fallback_mono.source()
        return Mono(with_error_resume)
    
    def do_on_next(self, action: Callable[[T], None]) -> 'Mono[T]':
        """값이 있을 때 사이드 이펙트 실행"""
        async def with_side_effect():
            value = await self.source()
            if value is not None:
                action(value)
            return value
        return Mono(with_side_effect)
    
    def do_on_error(self, action: Callable[[Exception], None]) -> 'Mono[T]':
        """에러 시 사이드 이펙트 실행"""
        async def with_error_side_effect():
            try:
                return await self.source()
            except Exception as e:
                action(e)
                raise
        return Mono(with_error_side_effect)
    
    def do_finally(self, action: Callable[[], None]) -> 'Mono[T]':
        """완료/에러 상관없이 항상 실행"""
        async def with_finally():
            try:
                return await self.source()
            finally:
                action()
        return Mono(with_finally)
    
    async def block(self, timeout: Optional[float] = None) -> Optional[T]:
        """
        블로킹 방식으로 값 가져오기
        
        Args:
            timeout: 타임아웃 (초)
            
        Returns:
            값 또는 None
        """
        if timeout:
            return await asyncio.wait_for(self.source(), timeout=timeout)
        return await self.source()
    
    async def subscribe(self,
                        on_success: Callable[[T], None] = None,
                        on_error: Callable[[Exception], None] = None,
                        on_complete: Callable[[], None] = None) -> None:
        """
        Mono 구독
        
        Args:
            on_success: 성공 시 콜백
            on_error: 에러 시 콜백  
            on_complete: 완료 시 콜백
        """
        try:
            value = await self.source()
            if value is not None and on_success:
                on_success(value)
            if on_complete:
                on_complete()
        except Exception as e:
            if on_error:
                on_error(e)
            else:
                raise
    
    def __await__(self):
        """await 지원"""
        return self.source().__await__()
    
    def __repr__(self) -> str:
        return f"Mono({self.__class__.__name__})"