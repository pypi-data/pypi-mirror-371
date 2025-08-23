# mediapyr (Python)

Mediator pattern implementation for Python, inspired by MediatR in C#. Provides async-first request/response and pub/sub messaging with optional Dependency Injection (DI).

---

## Installation

```bash
pip install mediapyr
```

---

## Quick Start

### Define a Request and Handler

```python
from mediapyr import mediator, Request, IRequestHandler

class Ping(Request):
    def __init__(self, msg: str):
        self.msg = msg

@mediator.request_handler(Ping)
class PingHandler(IRequestHandler):
    async def handle(self, request: Ping) -> str:
        return f"Pong: {request.msg}"
```

### Define an Event and Handlers

```python
from mediapyr import Event, IEventHandler

class UserCreated(Event):
    def __init__(self, username: str):
        self.username = username

@mediator.event_handler(UserCreated)
class SendWelcomeEmail(IEventHandler):
    async def handle(self, event: UserCreated):
        print(f"📧 Send welcome email to {event.username}")

@mediator.event_handler(UserCreated)
class AddToCRM(IEventHandler):
    async def handle(self, event: UserCreated):
        print(f"👤 Add {event.username} to CRM")
```

### Run Example

```python
import asyncio
from mediapyr import mediator

async def main():
    res = await mediator.send(Ping("Hello"))
    print("Send result:", res)

    await mediator.publish(UserCreated("Alice"))

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Dependency Injection with `dependency-injector`

mediapyr supports plugging in your own DI provider. Example using [dependency-injector](https://python-dependency-injector.ets-labs.org/):

```python
from dependency_injector import containers, providers
from mediapyr import mediator, IRequestHandler, IEventHandler

# Example services
class EmailService:
    def send(self, user: str):
        print(f"[EmailService] Sent email to {user}")

class UserRepository:
    def add(self, user: str):
        print(f"[UserRepository] Added user {user}")

# Handlers
class SendWelcomeEmail(IEventHandler):
    def __init__(self, email_service: EmailService):
        self._email = email_service
    async def handle(self, event: UserCreated):
        self._email.send(event.username)

class AddToCRM(IEventHandler):
    def __init__(self, repo: UserRepository):
        self._repo = repo
    async def handle(self, event: UserCreated):
        self._repo.add(event.username)

class PingHandler(IRequestHandler):
    async def handle(self, request: Ping) -> str:
        return f"Pong from DI: {request.msg}"

# Setup DI container
class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration()

    # Services (singleton)
    email_service = providers.Singleton(EmailService)
    user_repo = providers.Singleton(UserRepository)

    # Handlers (factory/transient)
    SendWelcomeEmail = providers.Factory(SendWelcomeEmail, email_service=email_service)
    AddToCRM = providers.Factory(AddToCRM, repo=user_repo)
    PingHandler = providers.Factory(PingHandler)

container = Container()

# Plug into mediator
def provider(cls):
    try:
        return getattr(container, cls.__name__)()
    except AttributeError:
        return cls()  # fallback empty constructor

mediator._provider = provider
```

### Running with DI

```python
import asyncio

async def main():
    res = await mediator.send(Ping("Hello DI"))
    print("Send result:", res)

    await mediator.publish(UserCreated("Alice"))

if __name__ == "__main__":
    asyncio.run(main())
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

Author: NguyenTungSk
