from typing import Dict, List, Type, Callable, Any
from abc import ABC, abstractmethod

# -------------------- Base Classes --------------------
class Request: pass
class Event: pass

# -------------------- Interfaces --------------------
class IRequestHandler(ABC):
    @abstractmethod
    async def handle(self, request: Request) -> Any: ...

class IEventHandler(ABC):
    @abstractmethod
    async def handle(self, event: Event) -> None: ...

# -------------------- Mediator --------------------
class Mediator:
    def __init__(self, provider: Callable[[Type], Any] = None):
        self._provider = provider or (lambda cls: cls())
        self._request_handlers: Dict[Type, Type] = {}
        self._event_handlers: Dict[Type, List[Type]] = {}

    def _resolve(self, cls):
        """Resolve handler with DI provider"""
        return self._provider(cls)

    def request_handler(self, request_type: Type[Request]):
        def deco(handler_class: Type[IRequestHandler]):
            self._request_handlers[request_type] = handler_class
            return handler_class
        return deco

    def event_handler(self, event_type: Type[Event]):
        def deco(handler_class: Type[IEventHandler]):
            self._event_handlers.setdefault(event_type, []).append(handler_class)
            return handler_class
        return deco

    async def send(self, request: Request) -> Any:
        handler_cls = self._request_handlers.get(type(request))
        if not handler_cls:
            raise KeyError(f"No handler for {type(request).__name__}")
        handler = self._resolve(handler_cls)
        return await handler.handle(request)

    async def publish(self, event: Event) -> None:
        for handler_cls in self._event_handlers.get(type(event), []):
            handler = self._resolve(handler_cls)
            await handler.handle(event)

# Global singleton
mediator = Mediator()