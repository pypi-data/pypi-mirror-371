import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WorkflowStat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PENDING: _ClassVar[WorkflowStat]
    RUNNING: _ClassVar[WorkflowStat]
    FINISHED: _ClassVar[WorkflowStat]
    TIMEOUT: _ClassVar[WorkflowStat]
PENDING: WorkflowStat
RUNNING: WorkflowStat
FINISHED: WorkflowStat
TIMEOUT: WorkflowStat

class Workflow(_message.Message):
    __slots__ = ("id", "organization_id", "created_by", "name", "description", "flow", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FLOW_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    created_by: int
    name: str
    description: str
    flow: Flow
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., created_by: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., flow: _Optional[_Union[Flow, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class WorkflowTask(_message.Message):
    __slots__ = ("id", "organization_id", "workflow_id", "device_id", "flow", "pointer")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    FLOW_FIELD_NUMBER: _ClassVar[int]
    POINTER_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    workflow_id: int
    device_id: int
    flow: Flow
    pointer: int
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., workflow_id: _Optional[int] = ..., device_id: _Optional[int] = ..., flow: _Optional[_Union[Flow, _Mapping]] = ..., pointer: _Optional[int] = ...) -> None: ...

class Flow(_message.Message):
    __slots__ = ("default", "notification", "events")
    DEFAULT_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    default: DefaultReportModule
    notification: NotificationTrigger
    events: _containers.RepeatedCompositeFieldContainer[Event]
    def __init__(self, default: _Optional[_Union[DefaultReportModule, _Mapping]] = ..., notification: _Optional[_Union[NotificationTrigger, _Mapping]] = ..., events: _Optional[_Iterable[_Union[Event, _Mapping]]] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("notification", "area", "shovel")
    NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    SHOVEL_FIELD_NUMBER: _ClassVar[int]
    notification: NotificationTrigger
    area: AreaModule
    shovel: ShovelModule
    def __init__(self, notification: _Optional[_Union[NotificationTrigger, _Mapping]] = ..., area: _Optional[_Union[AreaModule, _Mapping]] = ..., shovel: _Optional[_Union[ShovelModule, _Mapping]] = ...) -> None: ...

class AreaModule(_message.Message):
    __slots__ = ("inside", "area_id", "min_active_sec", "max_active_sec", "min_mileage_sec", "max_mileage_sec")
    INSIDE_FIELD_NUMBER: _ClassVar[int]
    AREA_ID_FIELD_NUMBER: _ClassVar[int]
    MIN_ACTIVE_SEC_FIELD_NUMBER: _ClassVar[int]
    MAX_ACTIVE_SEC_FIELD_NUMBER: _ClassVar[int]
    MIN_MILEAGE_SEC_FIELD_NUMBER: _ClassVar[int]
    MAX_MILEAGE_SEC_FIELD_NUMBER: _ClassVar[int]
    inside: bool
    area_id: int
    min_active_sec: int
    max_active_sec: int
    min_mileage_sec: int
    max_mileage_sec: int
    def __init__(self, inside: bool = ..., area_id: _Optional[int] = ..., min_active_sec: _Optional[int] = ..., max_active_sec: _Optional[int] = ..., min_mileage_sec: _Optional[int] = ..., max_mileage_sec: _Optional[int] = ...) -> None: ...

class ShovelModule(_message.Message):
    __slots__ = ("inside", "shovel_id", "min_active_sec", "max_active_sec", "min_mileage_sec", "max_mileage_sec")
    INSIDE_FIELD_NUMBER: _ClassVar[int]
    SHOVEL_ID_FIELD_NUMBER: _ClassVar[int]
    MIN_ACTIVE_SEC_FIELD_NUMBER: _ClassVar[int]
    MAX_ACTIVE_SEC_FIELD_NUMBER: _ClassVar[int]
    MIN_MILEAGE_SEC_FIELD_NUMBER: _ClassVar[int]
    MAX_MILEAGE_SEC_FIELD_NUMBER: _ClassVar[int]
    inside: bool
    shovel_id: int
    min_active_sec: int
    max_active_sec: int
    min_mileage_sec: int
    max_mileage_sec: int
    def __init__(self, inside: bool = ..., shovel_id: _Optional[int] = ..., min_active_sec: _Optional[int] = ..., max_active_sec: _Optional[int] = ..., min_mileage_sec: _Optional[int] = ..., max_mileage_sec: _Optional[int] = ...) -> None: ...

class DefaultReportModule(_message.Message):
    __slots__ = ("device_id", "duration", "mileage", "started_at", "finished_at")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    duration: int
    mileage: int
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    def __init__(self, device_id: _Optional[int] = ..., duration: _Optional[int] = ..., mileage: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class NotificationTrigger(_message.Message):
    __slots__ = ("title", "body")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    title: str
    body: str
    def __init__(self, title: _Optional[str] = ..., body: _Optional[str] = ...) -> None: ...
