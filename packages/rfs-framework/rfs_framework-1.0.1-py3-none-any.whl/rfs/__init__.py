"""
RFS Framework - Reactive Functional Serverless

A comprehensive framework combining:
- Reactive Streams (inspired by Spring Reactor)
- Functional Programming patterns
- State Machine systems
- Serverless optimizations (Cloud Run, Cloud Tasks)
- Event-Driven Architecture

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "RFS Framework Team"

# Core exports
from .reactive import Flux, Mono
from .core.result import Result, Success, Failure, success, failure
from .core.singleton import StatelessRegistry
from .state_machine import StateMachine, State, Transition
from .serverless import CloudRunOptimizer, CloudTasksClient
from .events import EventBus, Event, Saga

__all__ = [
    # Reactive
    "Flux",
    "Mono",
    
    # Functional
    "Result", 
    "Success",
    "Failure",
    "success", 
    "failure",
    
    # Core
    "StatelessRegistry",
    
    # State Machine
    "StateMachine",
    "State", 
    "Transition",
    
    # Serverless
    "CloudRunOptimizer",
    "CloudTasksClient",
    
    # Events  
    "EventBus",
    "Event",
    "Saga"
]