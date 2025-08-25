from typing import Generic, Literal
from maleo.soma.mixins.general import SuccessT
from maleo.soma.enums.operation import OperationType
from maleo.soma.schemas.error import (
    NoErrorMixin,
    ErrorMixin,
)
from maleo.soma.schemas.operation.base import BaseOperationSchema
from maleo.soma.schemas.operation.result import (
    AnyOperationResultMixin,
    NoOperationResultMixin,
    OperationResultSchemaT,
    OptionalOperationResultMixin,
)
from .action import SystemOperationActionSchema


class SystemOperationSchema(
    AnyOperationResultMixin,
    BaseOperationSchema[SuccessT, SystemOperationActionSchema],
    Generic[SuccessT],
):
    type: OperationType = OperationType.SYSTEM


class FailedSystemOperationSchema(
    NoOperationResultMixin, ErrorMixin, SystemOperationSchema[Literal[False]]
):
    success: Literal[False] = False


class SuccessfulSystemOperationSchema(
    OptionalOperationResultMixin[OperationResultSchemaT],
    NoErrorMixin,
    SystemOperationSchema[Literal[True]],
    Generic[OperationResultSchemaT],
):
    success: Literal[True] = True
