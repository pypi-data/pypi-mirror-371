from typing import Any

import dataclasses
import os
import httpx

from dataclasses import dataclass

from .types import SendNotificationPayload, AuthTokenClaims


@dataclass
class NotificationMessage:
    title: str
    body: str


@dataclass
class BusMessage:
    event: str
    payload: Any


class AuthProvider:
    _endpoint: str
    _jwt_secret: str

    def __init__(self, *, endpoint: str | None = None, jwt_secret: str | None = None):
        if endpoint is None:
            self._endpoint = "http://auth:3030"
        else:
            if endpoint.endswith("/"):
                endpoint = endpoint[:-1]

            self._endpoint = endpoint

        if jwt_secret is None:
            value = os.environ.get("JWT_SECRET")

            if not value:
                raise RuntimeError(
                    "JWT Secret should be provided explicitly or via JWT_SECRET environment variable"
                )

            self._jwt_secret = value
        else:
            self._jwt_secret = jwt_secret

    async def _send_notification(self, payload: SendNotificationPayload):
        claims = AuthTokenClaims.get_admin_claims()

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self._endpoint}/notifications/send",
                json=dataclasses.asdict(payload),
                headers={"Authorization": f"Bearer {claims.to_jwt(self._jwt_secret)}"},
            )

            r.raise_for_status()

    async def send_bus_msg(
        self,
        user_id: int,
        message: BusMessage,
    ):
        claims = AuthTokenClaims.get_admin_claims()

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self._endpoint}/message-bus/send",
                json={
                    "user_id": user_id,
                    "message": dataclasses.asdict(message)
                },
                headers={"Authorization": f"Bearer {claims.to_jwt(self._jwt_secret)}"},
            )

            r.raise_for_status()

    async def send_notification_to_user(
        self, message: NotificationMessage, user_id: int
    ):
        payload = SendNotificationPayload(
            title=message.title,
            body=message.body,
            user_id=user_id,
        )

        await self._send_notification(payload)

    async def send_notification_to_device(
        self, message: NotificationMessage, device_id: int
    ):
        payload = SendNotificationPayload(
            title=message.title,
            body=message.body,
            device_id=device_id,
        )

        await self._send_notification(payload)