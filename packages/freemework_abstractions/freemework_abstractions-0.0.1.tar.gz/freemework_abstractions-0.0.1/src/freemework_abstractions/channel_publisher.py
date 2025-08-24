from abc import ABC, abstractmethod
from typing import Awaitable, Generic, TypeVar

from .execution_context import FExecutionContext

TData = TypeVar('TData')

class FChannelPublisher(ABC, Generic[TData]):
    @abstractmethod
    def publish(executionContext: FExecutionContext, data: TData) -> Awaitable[None]:
        pass