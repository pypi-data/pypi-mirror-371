import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from areas import area_pb2 as _area_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Operation(_message.Message):
    __slots__ = ("id", "device_id", "status", "destinations_index", "geo_id", "description", "destinations", "destination_name", "picture", "passengers", "passengers_name", "work_time", "extra_work_time", "extra_night_work_time", "holiday_extra_work_time", "holiday_extra_night_work_time", "internal_mileage", "external_mileage", "total_nightly", "organization_id", "user_accepted_id", "user_created_id", "user_rejected_id", "user_requested_id", "requested_at", "started_at", "accepted_at", "rejected_at", "ended_at", "created_at", "updated_at", "error_code")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Pending: _ClassVar[Operation.Status]
        Running: _ClassVar[Operation.Status]
        Finished: _ClassVar[Operation.Status]
        Accepted: _ClassVar[Operation.Status]
        Rejected: _ClassVar[Operation.Status]
    Pending: Operation.Status
    Running: Operation.Status
    Finished: Operation.Status
    Accepted: Operation.Status
    Rejected: Operation.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DESTINATIONS_INDEX_FIELD_NUMBER: _ClassVar[int]
    GEO_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DESTINATIONS_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_NAME_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    PASSENGERS_FIELD_NUMBER: _ClassVar[int]
    PASSENGERS_NAME_FIELD_NUMBER: _ClassVar[int]
    WORK_TIME_FIELD_NUMBER: _ClassVar[int]
    EXTRA_WORK_TIME_FIELD_NUMBER: _ClassVar[int]
    EXTRA_NIGHT_WORK_TIME_FIELD_NUMBER: _ClassVar[int]
    HOLIDAY_EXTRA_WORK_TIME_FIELD_NUMBER: _ClassVar[int]
    HOLIDAY_EXTRA_NIGHT_WORK_TIME_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_MILEAGE_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_MILEAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_NIGHTLY_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ACCEPTED_ID_FIELD_NUMBER: _ClassVar[int]
    USER_CREATED_ID_FIELD_NUMBER: _ClassVar[int]
    USER_REJECTED_ID_FIELD_NUMBER: _ClassVar[int]
    USER_REQUESTED_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_AT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_AT_FIELD_NUMBER: _ClassVar[int]
    REJECTED_AT_FIELD_NUMBER: _ClassVar[int]
    ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    id: int
    device_id: int
    status: Operation.Status
    destinations_index: int
    geo_id: int
    description: str
    destinations: DestinationList
    destination_name: str
    picture: str
    passengers: str
    passengers_name: str
    work_time: int
    extra_work_time: int
    extra_night_work_time: int
    holiday_extra_work_time: int
    holiday_extra_night_work_time: int
    internal_mileage: int
    external_mileage: int
    total_nightly: int
    organization_id: int
    user_accepted_id: int
    user_created_id: int
    user_rejected_id: int
    user_requested_id: int
    requested_at: _timestamp_pb2.Timestamp
    started_at: _timestamp_pb2.Timestamp
    accepted_at: _timestamp_pb2.Timestamp
    rejected_at: _timestamp_pb2.Timestamp
    ended_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    error_code: int
    def __init__(self, id: _Optional[int] = ..., device_id: _Optional[int] = ..., status: _Optional[_Union[Operation.Status, str]] = ..., destinations_index: _Optional[int] = ..., geo_id: _Optional[int] = ..., description: _Optional[str] = ..., destinations: _Optional[_Union[DestinationList, _Mapping]] = ..., destination_name: _Optional[str] = ..., picture: _Optional[str] = ..., passengers: _Optional[str] = ..., passengers_name: _Optional[str] = ..., work_time: _Optional[int] = ..., extra_work_time: _Optional[int] = ..., extra_night_work_time: _Optional[int] = ..., holiday_extra_work_time: _Optional[int] = ..., holiday_extra_night_work_time: _Optional[int] = ..., internal_mileage: _Optional[int] = ..., external_mileage: _Optional[int] = ..., total_nightly: _Optional[int] = ..., organization_id: _Optional[int] = ..., user_accepted_id: _Optional[int] = ..., user_created_id: _Optional[int] = ..., user_rejected_id: _Optional[int] = ..., user_requested_id: _Optional[int] = ..., requested_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., accepted_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., rejected_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., ended_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., error_code: _Optional[int] = ...) -> None: ...

class DestinationList(_message.Message):
    __slots__ = ("destination",)
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    destination: _containers.RepeatedCompositeFieldContainer[Destination]
    def __init__(self, destination: _Optional[_Iterable[_Union[Destination, _Mapping]]] = ...) -> None: ...

class Destination(_message.Message):
    __slots__ = ("area_id", "start", "finish", "duration", "mileage")
    class Event(_message.Message):
        __slots__ = ("point", "datetime", "gps_time", "mileage")
        POINT_FIELD_NUMBER: _ClassVar[int]
        DATETIME_FIELD_NUMBER: _ClassVar[int]
        GPS_TIME_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        point: _area_pb2.Point
        datetime: _timestamp_pb2.Timestamp
        gps_time: _timestamp_pb2.Timestamp
        mileage: int
        def __init__(self, point: _Optional[_Union[_area_pb2.Point, _Mapping]] = ..., datetime: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., gps_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., mileage: _Optional[int] = ...) -> None: ...
    AREA_ID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    FINISH_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    area_id: int
    start: Destination.Event
    finish: Destination.Event
    duration: int
    mileage: int
    def __init__(self, area_id: _Optional[int] = ..., start: _Optional[_Union[Destination.Event, _Mapping]] = ..., finish: _Optional[_Union[Destination.Event, _Mapping]] = ..., duration: _Optional[int] = ..., mileage: _Optional[int] = ...) -> None: ...

class OperationMileageMemory(_message.Message):
    __slots__ = ("status", "gps_time", "mileage")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    GPS_TIME_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    status: bool
    gps_time: _timestamp_pb2.Timestamp
    mileage: int
    def __init__(self, status: bool = ..., gps_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., mileage: _Optional[int] = ...) -> None: ...

class TripFailedJob(_message.Message):
    __slots__ = ("uuid", "handler", "date", "device_id", "started_at", "failed_at", "running_at", "tries", "exception", "payload")
    UUID_FIELD_NUMBER: _ClassVar[int]
    HANDLER_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FAILED_AT_FIELD_NUMBER: _ClassVar[int]
    RUNNING_AT_FIELD_NUMBER: _ClassVar[int]
    TRIES_FIELD_NUMBER: _ClassVar[int]
    EXCEPTION_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    handler: str
    date: str
    device_id: str
    started_at: _timestamp_pb2.Timestamp
    failed_at: _timestamp_pb2.Timestamp
    running_at: _timestamp_pb2.Timestamp
    tries: int
    exception: str
    payload: bytes
    def __init__(self, uuid: _Optional[str] = ..., handler: _Optional[str] = ..., date: _Optional[str] = ..., device_id: _Optional[str] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., failed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., running_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., tries: _Optional[int] = ..., exception: _Optional[str] = ..., payload: _Optional[bytes] = ...) -> None: ...
