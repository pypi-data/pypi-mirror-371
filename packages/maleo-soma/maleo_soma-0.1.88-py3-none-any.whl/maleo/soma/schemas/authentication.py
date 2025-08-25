from fastapi import Request
from pydantic import BaseModel, Field
from typing import Generic, Literal, Optional, Sequence, TypeVar
from maleo.soma.authentication import (
    Credentials as RequestCredentials,
    User as RequestUser,
)
from maleo.soma.schemas.token import AuthenticationToken


TokenT = TypeVar("TokenT")
ScopesT = TypeVar("ScopesT")


class Credentials(
    BaseModel,
    Generic[
        TokenT,
        ScopesT,
    ],
):
    token: TokenT = Field(..., description="Token")
    scopes: ScopesT = Field(..., description="Scopes")


class CredentialsMixin(BaseModel, Generic[TokenT, ScopesT]):
    credentials: Credentials[TokenT, ScopesT] = Field(..., description="Credentials")


IsAuthenticatedT = TypeVar("IsAuthenticatedT")


class User(BaseModel, Generic[IsAuthenticatedT]):
    is_authenticated: IsAuthenticatedT = Field(..., description="Authenticated")
    display_name: str = Field("", description="Username")
    identity: str = Field("", description="Email")


class UserMixin(BaseModel, Generic[IsAuthenticatedT]):
    user: User[IsAuthenticatedT] = Field(..., description="User")


class BaseAuthentication(
    UserMixin[IsAuthenticatedT],
    CredentialsMixin[TokenT, ScopesT],
    Generic[TokenT, ScopesT, IsAuthenticatedT],
):
    @classmethod
    def _validate_request_credentials(cls, request: Request):
        if not isinstance(request.auth, RequestCredentials):
            raise TypeError(
                f"Invalid type of request's credentials: '{type(request.auth)}'"
            )

    @classmethod
    def _validate_request_user(cls, request: Request):
        if not isinstance(request.user, RequestUser):
            raise TypeError(f"Invalid type of request's user: '{type(request.user)}'")


class Authentication(
    BaseAuthentication[Optional[AuthenticationToken], Optional[Sequence[str]], bool]
):
    @classmethod
    def from_request(cls, request: Request) -> "Authentication":
        # validate credentials
        cls._validate_request_credentials(request=request)
        credentials = Credentials[
            Optional[AuthenticationToken], Optional[Sequence[str]]
        ].model_validate(request.auth, from_attributes=True)

        # validate user
        cls._validate_request_user(request=request)
        user = User[bool].model_validate(request.user, from_attributes=True)

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(cls):
        """Create a FastAPI dependency for this authentication."""

        def dependency(request: Request) -> "Authentication":
            return cls.from_request(request)

        return dependency


class AuthenticationMixin(BaseModel):
    authentication: Authentication = Field(
        ...,
        description="Authentication",
    )


class OptionalAuthenticationMixin(BaseModel):
    authentication: Optional[Authentication] = Field(
        None,
        description="Authentication. (Optional)",
    )


class MandatoryAuthentication(
    BaseAuthentication[AuthenticationToken, Sequence[str], Literal[True]]
):
    @classmethod
    def from_request(cls, request: Request) -> "MandatoryAuthentication":
        # validate credentials
        cls._validate_request_credentials(request=request)
        credentials = Credentials[AuthenticationToken, Sequence[str]].model_validate(
            request.auth, from_attributes=True
        )

        # validate user
        cls._validate_request_user(request=request)
        user = User[Literal[True]].model_validate(request.user, from_attributes=True)

        return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(cls):
        """Create a FastAPI dependency for this authentication."""

        def dependency(request: Request) -> "MandatoryAuthentication":
            return cls.from_request(request)

        return dependency

    def to_authentication(self) -> Authentication:
        return Authentication.model_validate(self.model_dump())

    @classmethod
    def from_authentication(
        cls, authentication: Authentication
    ) -> "MandatoryAuthentication":
        return cls.model_validate(authentication.model_dump())
