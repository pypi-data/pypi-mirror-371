import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommandStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PENDING: _ClassVar[CommandStatus]
    OFFLINE: _ClassVar[CommandStatus]
    ERROR: _ClassVar[CommandStatus]
    SENT: _ClassVar[CommandStatus]
PENDING: CommandStatus
OFFLINE: CommandStatus
ERROR: CommandStatus
SENT: CommandStatus

class CommandContent(_message.Message):
    __slots__ = ("device_id", "command_id", "message", "params", "raw_command")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    RAW_COMMAND_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    command_id: int
    message: str
    params: _containers.RepeatedScalarFieldContainer[str]
    raw_command: str
    def __init__(self, device_id: _Optional[int] = ..., command_id: _Optional[int] = ..., message: _Optional[str] = ..., params: _Optional[_Iterable[str]] = ..., raw_command: _Optional[str] = ...) -> None: ...

class CommandAkn(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class Command(_message.Message):
    __slots__ = ("id", "device_id", "user_id", "command_id", "reply_id", "status", "command", "akn", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    REPLY_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    AKN_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    device_id: int
    user_id: int
    command_id: int
    reply_id: int
    status: CommandStatus
    command: CommandContent
    akn: CommandAkn
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., device_id: _Optional[int] = ..., user_id: _Optional[int] = ..., command_id: _Optional[int] = ..., reply_id: _Optional[int] = ..., status: _Optional[_Union[CommandStatus, str]] = ..., command: _Optional[_Union[CommandContent, _Mapping]] = ..., akn: _Optional[_Union[CommandAkn, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CommandValidation(_message.Message):
    __slots__ = ("max", "min", "name", "type", "description", "is_required")
    MAX_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    max: int
    min: int
    name: str
    type: str
    description: str
    is_required: bool
    def __init__(self, max: _Optional[int] = ..., min: _Optional[int] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., description: _Optional[str] = ..., is_required: bool = ...) -> None: ...

class CommandFormat(_message.Message):
    __slots__ = ("structure", "parameters")
    STRUCTURE_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    structure: str
    parameters: _containers.RepeatedCompositeFieldContainer[CommandValidation]
    def __init__(self, structure: _Optional[str] = ..., parameters: _Optional[_Iterable[_Union[CommandValidation, _Mapping]]] = ...) -> None: ...

class CommandStruct(_message.Message):
    __slots__ = ("id", "tracker_id", "user_created_id", "user_updated_id", "organization_id", "name", "sort_order", "visible", "description", "sms", "grpc", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TRACKER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_CREATED_ID_FIELD_NUMBER: _ClassVar[int]
    USER_UPDATED_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SMS_FIELD_NUMBER: _ClassVar[int]
    GRPC_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    tracker_id: int
    user_created_id: int
    user_updated_id: int
    organization_id: int
    name: str
    sort_order: int
    visible: int
    description: str
    sms: CommandFormat
    grpc: CommandFormat
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., tracker_id: _Optional[int] = ..., user_created_id: _Optional[int] = ..., user_updated_id: _Optional[int] = ..., organization_id: _Optional[int] = ..., name: _Optional[str] = ..., sort_order: _Optional[int] = ..., visible: _Optional[int] = ..., description: _Optional[str] = ..., sms: _Optional[_Union[CommandFormat, _Mapping]] = ..., grpc: _Optional[_Union[CommandFormat, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DevicePoolRequestRefetch(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DevicePoolRequest(_message.Message):
    __slots__ = ("device_id", "requested", "request_refetch")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_FIELD_NUMBER: _ClassVar[int]
    REQUEST_REFETCH_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    requested: _timestamp_pb2.Timestamp
    request_refetch: DevicePoolRequestRefetch
    def __init__(self, device_id: _Optional[int] = ..., requested: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., request_refetch: _Optional[_Union[DevicePoolRequestRefetch, _Mapping]] = ...) -> None: ...
