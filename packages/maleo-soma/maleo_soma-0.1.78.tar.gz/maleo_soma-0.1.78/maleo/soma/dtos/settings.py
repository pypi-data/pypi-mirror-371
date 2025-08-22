from pydantic_settings import BaseSettings
from pydantic import Field, model_validator
from typing import Self
from maleo.soma.enums.environment import Environment
from maleo.soma.enums.service import ServiceKey, ServiceName
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.types.base import OptionalString


class Settings(BaseSettings):
    ENVIRONMENT: Environment = Field(..., description="Environment")
    HOST: str = Field("127.0.0.1", description="Application's host")
    PORT: int = Field(8000, description="Application's port")
    HOST_PORT: int = Field(8000, description="Host's port")
    SERVICE_KEY: ServiceKey = Field(..., description="Service's key")
    SERVICE_NAME: ServiceName = Field(..., description="Service's name")
    ROOT_PATH: str = Field("", description="Application's root path")
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(
        "/etc/maleo/credentials/google-service-account.json",
        description="Google application credential's file path",
    )
    USE_LOCAL_CONFIGURATIONS: bool = Field(
        False, description="Whether to use local configurations"
    )
    CONFIGURATIONS_PATH: OptionalString = Field(None, description="Configurations path")
    KEY_PASSWORD: OptionalString = Field(None, description="Key's password")
    PRIVATE_KEY: OptionalString = Field(None, description="Private key")
    PUBLIC_KEY: OptionalString = Field(None, description="Public key")

    @model_validator(mode="after")
    def validate_configurations_path(self) -> Self:
        if self.USE_LOCAL_CONFIGURATIONS and self.CONFIGURATIONS_PATH is None:
            self.CONFIGURATIONS_PATH = (
                f"/etc/maleo/configurations/{self.SERVICE_KEY}/{self.ENVIRONMENT}.yaml"
            )

        if self.USE_LOCAL_CONFIGURATIONS and self.CONFIGURATIONS_PATH is None:
            raise ValueError(
                "Configurations path must exist if use local configurations is set to true"
            )

        return self

    @property
    def service_context(self) -> ServiceContext:
        return ServiceContext(environment=self.ENVIRONMENT, key=self.SERVICE_KEY)
