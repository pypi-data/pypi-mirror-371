import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from identities import identities_pb2 as _identities_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AreaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Circle: _ClassVar[AreaType]
    Polygon: _ClassVar[AreaType]
    Rectangle: _ClassVar[AreaType]
    Marker: _ClassVar[AreaType]
Circle: AreaType
Polygon: AreaType
Rectangle: AreaType
Marker: AreaType

class Point(_message.Message):
    __slots__ = ("latitude", "longitude")
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    latitude: float
    longitude: float
    def __init__(self, latitude: _Optional[float] = ..., longitude: _Optional[float] = ...) -> None: ...

class Area(_message.Message):
    __slots__ = ("id", "type", "name", "organization_id", "radius", "color", "created_by", "updated_by", "category_id", "created_at", "updated_at", "category", "organization", "coordinates")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    id: int
    type: AreaType
    name: str
    organization_id: int
    radius: float
    color: str
    created_by: int
    updated_by: int
    category_id: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    category: AreaCategory
    organization: _identities_pb2.Organization
    coordinates: _containers.RepeatedCompositeFieldContainer[Point]
    def __init__(self, id: _Optional[int] = ..., type: _Optional[_Union[AreaType, str]] = ..., name: _Optional[str] = ..., organization_id: _Optional[int] = ..., radius: _Optional[float] = ..., color: _Optional[str] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., category_id: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., category: _Optional[_Union[AreaCategory, _Mapping]] = ..., organization: _Optional[_Union[_identities_pb2.Organization, _Mapping]] = ..., coordinates: _Optional[_Iterable[_Union[Point, _Mapping]]] = ...) -> None: ...

class WorkCycle(_message.Message):
    __slots__ = ("device_id", "start", "finish", "area", "started_at", "finished_at", "mileage", "duration")
    class Event(_message.Message):
        __slots__ = ("id", "name", "entered_point", "entered_at", "exited_point", "exited_at", "mileage", "duration")
        ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        ENTERED_POINT_FIELD_NUMBER: _ClassVar[int]
        ENTERED_AT_FIELD_NUMBER: _ClassVar[int]
        EXITED_POINT_FIELD_NUMBER: _ClassVar[int]
        EXITED_AT_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        DURATION_FIELD_NUMBER: _ClassVar[int]
        id: int
        name: str
        entered_point: Point
        entered_at: _timestamp_pb2.Timestamp
        exited_point: Point
        exited_at: _timestamp_pb2.Timestamp
        mileage: int
        duration: int
        def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., entered_point: _Optional[_Union[Point, _Mapping]] = ..., entered_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., exited_point: _Optional[_Union[Point, _Mapping]] = ..., exited_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., mileage: _Optional[int] = ..., duration: _Optional[int] = ...) -> None: ...
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    FINISH_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    start: WorkCycle.Event
    finish: WorkCycle.Event
    area: WorkCycle.Event
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    mileage: int
    duration: int
    def __init__(self, device_id: _Optional[int] = ..., start: _Optional[_Union[WorkCycle.Event, _Mapping]] = ..., finish: _Optional[_Union[WorkCycle.Event, _Mapping]] = ..., area: _Optional[_Union[WorkCycle.Event, _Mapping]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., mileage: _Optional[int] = ..., duration: _Optional[int] = ...) -> None: ...

class AreaAlertIsRunning(_message.Message):
    __slots__ = ("is_running", "latest")
    IS_RUNNING_FIELD_NUMBER: _ClassVar[int]
    LATEST_FIELD_NUMBER: _ClassVar[int]
    is_running: bool
    latest: int
    def __init__(self, is_running: bool = ..., latest: _Optional[int] = ...) -> None: ...

class AreaCategory(_message.Message):
    __slots__ = ("id", "name", "show", "organization_id", "created_by", "updated_by", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHOW_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    show: bool
    organization_id: int
    created_by: int
    updated_by: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., show: bool = ..., organization_id: _Optional[int] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
