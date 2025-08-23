"""
Railway Oriented Programming을 위한 Result 타입

Success/Failure를 명시적으로 처리하는 함수형 에러 처리 패턴
"""

import logging
from abc import ABC, abstractmethod
from functools import singledispatch
from typing import Any, Callable, Generic, Iterator, Optional, TypeVar, Union, List
import asyncio

logger = logging.getLogger(__name__)
T = TypeVar("T")
E = TypeVar("E") 
U = TypeVar("U")
V = TypeVar("V")


class Result(ABC, Generic[T, E]):
    """Result 추상 클래스 - Success 또는 Failure"""
    
    @abstractmethod
    def is_success(self) -> bool:
        """성공 여부 확인"""
        pass
    
    @abstractmethod
    def is_failure(self) -> bool:
        """실패 여부 확인"""
        pass
    
    @abstractmethod
    def unwrap(self) -> T:
        """값 추출 (실패시 예외)"""
        pass
    
    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """값 추출 (실패시 기본값)"""
        pass
    
    @abstractmethod
    def map(self, func: Callable[[T], U]) -> 'Result[U, E]':
        """값 변환"""
        pass
    
    @abstractmethod
    def bind(self, func: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """결과 연결 (flatMap)"""
        pass
    
    @abstractmethod
    def map_error(self, func: Callable[[E], U]) -> 'Result[T, U]':
        """에러 변환"""
        pass


class Success(Result[T, E]):
    """성공 결과"""
    
    def __init__(self, value: T):
        self.value = value
    
    def is_success(self) -> bool:
        return True
    
    def is_failure(self) -> bool:
        return False
    
    def unwrap(self) -> T:
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        return self.value
    
    def map(self, func: Callable[[T], U]) -> Result[U, E]:
        try:
            return Success(func(self.value))
        except Exception as e:
            return Failure(e)
    
    def bind(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        try:
            return func(self.value)
        except Exception as e:
            return Failure(e)
    
    def map_error(self, func: Callable[[E], U]) -> Result[T, U]:
        return Success(self.value)
    
    def __repr__(self) -> str:
        return f"Success({self.value})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Success) and self.value == other.value


class Failure(Result[T, E]):
    """실패 결과"""
    
    def __init__(self, error: E):
        self.error = error
    
    def is_success(self) -> bool:
        return False
    
    def is_failure(self) -> bool:
        return True
    
    def unwrap(self) -> T:
        if isinstance(self.error, Exception):
            raise self.error
        raise ValueError(f"Failure unwrap: {self.error}")
    
    def unwrap_error(self) -> E:
        """에러 값 추출"""
        return self.error
    
    def unwrap_or(self, default: T) -> T:
        return default
    
    def map(self, func: Callable[[T], U]) -> Result[U, E]:
        return Failure(self.error)
    
    def bind(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return Failure(self.error)
    
    def map_error(self, func: Callable[[E], U]) -> Result[T, U]:
        try:
            return Failure(func(self.error))
        except Exception as e:
            return Failure(e)
    
    def __repr__(self) -> str:
        return f"Failure({self.error})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Failure) and self.error == other.error


# 편의 함수들
def success(value: T) -> Result[T, E]:
    """Success 생성"""
    return Success(value)


def failure(error: E) -> Result[T, E]:
    """Failure 생성"""
    return Failure(error)


def try_except(func: Callable[[], T]) -> Result[T, Exception]:
    """함수 실행을 Result로 래핑"""
    try:
        return success(func())
    except Exception as e:
        return failure(e)


async def async_try_except(func: Callable[[], T]) -> Result[T, Exception]:
    """비동기 함수 실행을 Result로 래핑"""
    try:
        if hasattr(func, '__call__'):
            result = func()
            if hasattr(result, '__await__'):
                result = await result
            return success(result)
        return success(await func)
    except Exception as e:
        return failure(e)


def pipe_results(*funcs: Callable[[Any], Result[Any, Any]]) -> Callable[[Any], Result[Any, Any]]:
    """Result를 반환하는 함수들을 파이프라인으로 연결"""
    def pipeline(value: Any) -> Result[Any, Any]:
        result = success(value)
        for func in funcs:
            if result.is_failure():
                break
            result = result.bind(func)
        return result
    return pipeline


async def async_pipe_results(*funcs: Callable[[Any], Result[Any, Any]]) -> Callable[[Any], Result[Any, Any]]:
    """비동기 Result를 반환하는 함수들을 파이프라인으로 연결"""
    async def pipeline(value: Any) -> Result[Any, Any]:
        result = success(value)
        for func in funcs:
            if result.is_failure():
                break
            if hasattr(func, '__call__'):
                next_result = func(result.unwrap())
                if hasattr(next_result, '__await__'):
                    next_result = await next_result
                result = next_result
        return result
    return await pipeline


def is_success(result: Result) -> bool:
    """성공 여부 확인"""
    return result.is_success()


def is_failure(result: Result) -> bool:
    """실패 여부 확인"""
    return result.is_failure()


def from_optional(value: Optional[T], error: E = None) -> Result[T, E]:
    """Optional에서 Result로 변환"""
    if value is not None:
        return success(value)
    return failure(error or ValueError("None value"))


def sequence(results: List[Result[T, E]]) -> Result[List[T], E]:
    """Result 리스트를 리스트 Result로 변환"""
    values = []
    for result in results:
        if result.is_failure():
            return result
        values.append(result.unwrap())
    return success(values)


async def sequence_async(results: List[Result[T, E]]) -> Result[List[T], E]:
    """비동기 Result 리스트를 리스트 Result로 변환"""
    values = []
    for result in results:
        if result.is_failure():
            return result
        values.append(result.unwrap())
    return success(values)


def traverse(items: List[T], func: Callable[[T], Result[U, E]]) -> Result[List[U], E]:
    """리스트의 각 아이템에 함수를 적용하고 Result 리스트로 변환"""
    results = [func(item) for item in items]
    return sequence(results)


async def traverse_async(items: List[T], func: Callable[[T], Result[U, E]]) -> Result[List[U], E]:
    """비동기 traverse"""
    tasks = []
    for item in items:
        if asyncio.iscoroutinefunction(func):
            tasks.append(func(item))
        else:
            tasks.append(asyncio.create_task(asyncio.coroutine(lambda: func(item))()))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 예외를 Failure로 변환
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            processed_results.append(failure(result))
        elif isinstance(result, Result):
            processed_results.append(result)
        else:
            processed_results.append(success(result))
    
    return await sequence_async(processed_results)


# 고차 함수들
def lift(func: Callable[[T], U]) -> Callable[[Result[T, E]], Result[U, E]]:
    """일반 함수를 Result 컨텍스트로 리프트"""
    return lambda result: result.map(func)


def lift2(func: Callable[[T, U], V]) -> Callable[[Result[T, E], Result[U, E]], Result[V, E]]:
    """2개 인자 함수를 Result 컨텍스트로 리프트"""
    def lifted(result1: Result[T, E], result2: Result[U, E]) -> Result[V, E]:
        if result1.is_failure():
            return result1
        if result2.is_failure():
            return result2
        return success(func(result1.unwrap(), result2.unwrap()))
    
    return lifted


# 데코레이터들
def result_decorator(func: Callable[..., T]) -> Callable[..., Result[T, Exception]]:
    """함수를 Result를 반환하도록 래핑"""
    def wrapper(*args, **kwargs) -> Result[T, Exception]:
        try:
            return success(func(*args, **kwargs))
        except Exception as e:
            return failure(e)
    return wrapper


def async_result_decorator(func: Callable[..., T]) -> Callable[..., Result[T, Exception]]:
    """비동기 함수를 Result를 반환하도록 래핑"""
    async def wrapper(*args, **kwargs) -> Result[T, Exception]:
        try:
            result = func(*args, **kwargs)
            if hasattr(result, '__await__'):
                result = await result
            return success(result)
        except Exception as e:
            return failure(e)
    return wrapper


# 함수형 조합자들
def combine_results(*results: Result[Any, E]) -> Result[tuple, E]:
    """여러 Result를 하나의 Result로 결합"""
    values = []
    for result in results:
        if result.is_failure():
            return result
        values.append(result.unwrap())
    return success(tuple(values))


def first_success(*results: Result[T, E]) -> Result[T, List[E]]:
    """첫 번째 성공한 Result 반환"""
    errors = []
    for result in results:
        if result.is_success():
            return result
        errors.append(result.unwrap_error())
    return failure(errors)


def partition_results(results: List[Result[T, E]]) -> tuple[List[T], List[E]]:
    """Result 리스트를 성공과 실패로 분할"""
    successes = []
    failures = []
    
    for result in results:
        if result.is_success():
            successes.append(result.unwrap())
        else:
            failures.append(result.unwrap_error())
    
    return successes, failures


# 호환성 함수들 (기존 Cosmos V2 API)
def get_value(result: Result, default: Any = None) -> Any:
    """값 추출 (실패시 기본값) - 기존 V2 API 유지"""
    if result.is_success():
        return result.unwrap()
    return default


def get_error(result: Result) -> Optional[Any]:
    """에러 추출 - 기존 V2 API 유지"""
    if result.is_failure():
        return result.error
    return None


@singledispatch
def check_is_exception(obj) -> bool:
    """예외 타입 확인 - 기존 V2 API 유지"""
    return False


@check_is_exception.register(Exception)
def _(obj: Exception) -> bool:
    """Exception 타입 확인"""
    return True


@singledispatch
def check_is_result_type(obj) -> bool:
    """Result 타입 확인 - 기존 V2 API 유지"""
    return False


@check_is_result_type.register(Success)
def _(obj: Success) -> bool:
    """Success 타입 확인"""
    return True


@check_is_result_type.register(Failure)
def _(obj: Failure) -> bool:
    """Failure 타입 확인"""
    return True