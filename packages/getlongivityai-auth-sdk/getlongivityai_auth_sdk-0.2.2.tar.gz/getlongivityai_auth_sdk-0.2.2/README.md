A Python Library to interact with Auth service in a generic way

## Features

- Common Types
- JWT token construction
- Notifications sending


## Usage

1. Install the library: `uv add getlongivityai-auth-sdk`
2. Import `AuthProvider`


Example of sending a notification:

```python
import asyncio

from getlongivityai_auth_sdk import AuthProvider, NotificationMessage


async def main():
    provider = AuthProvider(
        # By default it's http//auth:3030
        endpoint='http://localhost:3031'
    )
    message = NotificationMessage(
        title='Test Notification',
        body='Body of the notification',
    )

    await provider.send_notification_to_user(
        message=message,
        user_id=1
    )


if __name__ == "__main__":
    asyncio.run(main())
```