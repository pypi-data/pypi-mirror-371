import os
import typing
import dataclasses
import datetime

import jwt

from dataclasses import dataclass


ALGORITHM = "HS256"


@dataclass
class AuthTokenClaims:
    """
    Content of the JWT token a user gets after authorization
    """

    id: int
    email: str

    device_id: int
    is_admin: bool
    notification_provider: typing.Literal["Google"] | typing.Literal["Apple"]

    @staticmethod
    def get_admin_claims() -> "AuthTokenClaims":
        """
        Constructs a token that understood by the system as "admin".
        Being an admin means having the ID equals to 0
        """
        return AuthTokenClaims(
            id=0,
            email="",
            device_id=0,
            is_admin=True,
            notification_provider="Google",
        )

    @staticmethod
    def from_jwt(token: str, secret: str) -> "AuthTokenClaims":
        jwt_data = jwt.decode(token, secret, algorithms=(ALGORITHM,))
        data = {
            field.name: jwt_data[field.name]
            for field in dataclasses.fields(AuthTokenClaims)
        }

        return AuthTokenClaims(**data)

    def to_jwt(self, secret: str, exp_sec: float | None = None):
        data = dataclasses.asdict(self)
        if exp_sec is None:
            exp_sec = datetime.timedelta(minutes=30).total_seconds()

        data["exp"] = int(
            (datetime.datetime.now() + datetime.timedelta(seconds=exp_sec)).timestamp()
        )

        return jwt.encode(
            data,
            secret,
            algorithm=ALGORITHM,
        )


@dataclass
class SendNotificationPayload:
    title: str
    body: str

    user_id: int | None = None
    device_id: int | None = None

    ERR_MSG = "You should define either user_id or device_id but not both"

    def __post_init__(self):
        if self.user_id is None and self.device_id is None:
            raise RuntimeError(self.ERR_MSG)

        if self.user_id is not None and self.device_id is not None:
            raise RuntimeError(self.ERR_MSG)