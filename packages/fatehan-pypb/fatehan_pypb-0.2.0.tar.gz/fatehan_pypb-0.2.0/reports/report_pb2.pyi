import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from packets import dataModel_pb2 as _dataModel_pb2
from packets import messages_pb2 as _messages_pb2
from trips import trip_pb2 as _trip_pb2
from areas import area_pb2 as _area_pb2
from devices import devices_pb2 as _devices_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Source(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MYSQL: _ClassVar[Source]
    CASSANDRA: _ClassVar[Source]

class RouteStopType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NONE: _ClassVar[RouteStopType]
    IDLING: _ClassVar[RouteStopType]
    STOPS: _ClassVar[RouteStopType]

class StopCalculateIo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BOTH: _ClassVar[StopCalculateIo]
    SPEED: _ClassVar[StopCalculateIo]
    IGNITION: _ClassVar[StopCalculateIo]
MYSQL: Source
CASSANDRA: Source
NONE: RouteStopType
IDLING: RouteStopType
STOPS: RouteStopType
BOTH: StopCalculateIo
SPEED: StopCalculateIo
IGNITION: StopCalculateIo

class SystemIoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SystemIoResponse(_message.Message):
    __slots__ = ("cost", "records", "ios")
    COST_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    IOS_FIELD_NUMBER: _ClassVar[int]
    cost: int
    records: int
    ios: _containers.RepeatedCompositeFieldContainer[_devices_pb2.SystemIo]
    def __init__(self, cost: _Optional[int] = ..., records: _Optional[int] = ..., ios: _Optional[_Iterable[_Union[_devices_pb2.SystemIo, _Mapping]]] = ...) -> None: ...

class ChartRequest(_message.Message):
    __slots__ = ("device_ids", "ios", "started_at", "finished_at")
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    IOS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    ios: _containers.RepeatedScalarFieldContainer[str]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    def __init__(self, device_ids: _Optional[_Iterable[int]] = ..., ios: _Optional[_Iterable[str]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ChartResponse(_message.Message):
    __slots__ = ("cost", "records", "chart", "section")
    class Series(_message.Message):
        __slots__ = ("series",)
        SERIES_FIELD_NUMBER: _ClassVar[int]
        series: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, series: _Optional[_Iterable[str]] = ...) -> None: ...
    class Chart(_message.Message):
        __slots__ = ("ios", "datetime")
        class IosEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: ChartResponse.Series
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ChartResponse.Series, _Mapping]] = ...) -> None: ...
        IOS_FIELD_NUMBER: _ClassVar[int]
        DATETIME_FIELD_NUMBER: _ClassVar[int]
        ios: _containers.MessageMap[str, ChartResponse.Series]
        datetime: _containers.RepeatedCompositeFieldContainer[_timestamp_pb2.Timestamp]
        def __init__(self, ios: _Optional[_Mapping[str, ChartResponse.Series]] = ..., datetime: _Optional[_Iterable[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]] = ...) -> None: ...
    class ChartEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: ChartResponse.Chart
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[ChartResponse.Chart, _Mapping]] = ...) -> None: ...
    COST_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    CHART_FIELD_NUMBER: _ClassVar[int]
    SECTION_FIELD_NUMBER: _ClassVar[int]
    cost: int
    records: int
    chart: _containers.MessageMap[int, ChartResponse.Chart]
    section: int
    def __init__(self, cost: _Optional[int] = ..., records: _Optional[int] = ..., chart: _Optional[_Mapping[int, ChartResponse.Chart]] = ..., section: _Optional[int] = ...) -> None: ...

class CommandHistoryRequest(_message.Message):
    __slots__ = ("device_id", "limit", "page")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    limit: int
    page: int
    def __init__(self, device_id: _Optional[int] = ..., limit: _Optional[int] = ..., page: _Optional[int] = ...) -> None: ...

class CommandHistoryResponse(_message.Message):
    __slots__ = ("records", "cost", "page", "list")
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    records: int
    cost: int
    page: int
    list: _containers.RepeatedCompositeFieldContainer[_messages_pb2.Command]
    def __init__(self, records: _Optional[int] = ..., cost: _Optional[int] = ..., page: _Optional[int] = ..., list: _Optional[_Iterable[_Union[_messages_pb2.Command, _Mapping]]] = ...) -> None: ...

class WorkCycleRequest(_message.Message):
    __slots__ = ("device_ids", "started_at", "finished_at", "shovel_stop_seconds", "area_stop_seconds")
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    SHOVEL_STOP_SECONDS_FIELD_NUMBER: _ClassVar[int]
    AREA_STOP_SECONDS_FIELD_NUMBER: _ClassVar[int]
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    shovel_stop_seconds: float
    area_stop_seconds: float
    def __init__(self, device_ids: _Optional[_Iterable[int]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., shovel_stop_seconds: _Optional[float] = ..., area_stop_seconds: _Optional[float] = ...) -> None: ...

class WorkCycleResponse(_message.Message):
    __slots__ = ("work_cycles", "cost", "threads", "records")
    WORK_CYCLES_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    THREADS_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    work_cycles: _containers.RepeatedCompositeFieldContainer[_area_pb2.WorkCycle]
    cost: int
    threads: int
    records: int
    def __init__(self, work_cycles: _Optional[_Iterable[_Union[_area_pb2.WorkCycle, _Mapping]]] = ..., cost: _Optional[int] = ..., threads: _Optional[int] = ..., records: _Optional[int] = ...) -> None: ...

class TripReportRequest(_message.Message):
    __slots__ = ("device_ids", "started_at", "finished_at")
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    def __init__(self, device_ids: _Optional[_Iterable[int]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AreaSplitterRequest(_message.Message):
    __slots__ = ("device_ids", "area_ids", "started_at", "finished_at")
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    AREA_IDS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    area_ids: _containers.RepeatedScalarFieldContainer[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    def __init__(self, device_ids: _Optional[_Iterable[int]] = ..., area_ids: _Optional[_Iterable[int]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AreaSplitterResponse(_message.Message):
    __slots__ = ("reports", "started_at", "finished_at")
    class Area(_message.Message):
        __slots__ = ("id", "name")
        ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        id: int
        name: str
        def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...
    class Record(_message.Message):
        __slots__ = ("device_id", "start", "finish", "started_at", "finished_at", "duration_origin", "duration_trip", "duration_destination", "mileage", "speed_max", "speed_avg")
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        START_FIELD_NUMBER: _ClassVar[int]
        FINISH_FIELD_NUMBER: _ClassVar[int]
        STARTED_AT_FIELD_NUMBER: _ClassVar[int]
        FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
        DURATION_ORIGIN_FIELD_NUMBER: _ClassVar[int]
        DURATION_TRIP_FIELD_NUMBER: _ClassVar[int]
        DURATION_DESTINATION_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        SPEED_MAX_FIELD_NUMBER: _ClassVar[int]
        SPEED_AVG_FIELD_NUMBER: _ClassVar[int]
        device_id: int
        start: AreaSplitterResponse.Area
        finish: AreaSplitterResponse.Area
        started_at: _timestamp_pb2.Timestamp
        finished_at: _timestamp_pb2.Timestamp
        duration_origin: int
        duration_trip: int
        duration_destination: int
        mileage: int
        speed_max: int
        speed_avg: int
        def __init__(self, device_id: _Optional[int] = ..., start: _Optional[_Union[AreaSplitterResponse.Area, _Mapping]] = ..., finish: _Optional[_Union[AreaSplitterResponse.Area, _Mapping]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., duration_origin: _Optional[int] = ..., duration_trip: _Optional[int] = ..., duration_destination: _Optional[int] = ..., mileage: _Optional[int] = ..., speed_max: _Optional[int] = ..., speed_avg: _Optional[int] = ...) -> None: ...
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    reports: _containers.RepeatedCompositeFieldContainer[AreaSplitterResponse.Record]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    def __init__(self, reports: _Optional[_Iterable[_Union[AreaSplitterResponse.Record, _Mapping]]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MaintenanceRequest(_message.Message):
    __slots__ = ("device_ids", "started_at", "finished_at", "group_by")
    class GroupBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        None: _ClassVar[MaintenanceRequest.GroupBy]
        Day: _ClassVar[MaintenanceRequest.GroupBy]
        Week: _ClassVar[MaintenanceRequest.GroupBy]
        Month: _ClassVar[MaintenanceRequest.GroupBy]
        Year: _ClassVar[MaintenanceRequest.GroupBy]
    None: MaintenanceRequest.GroupBy
    Day: MaintenanceRequest.GroupBy
    Week: MaintenanceRequest.GroupBy
    Month: MaintenanceRequest.GroupBy
    Year: MaintenanceRequest.GroupBy
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    GROUP_BY_FIELD_NUMBER: _ClassVar[int]
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    group_by: MaintenanceRequest.GroupBy
    def __init__(self, device_ids: _Optional[_Iterable[int]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., group_by: _Optional[_Union[MaintenanceRequest.GroupBy, str]] = ...) -> None: ...

class MaintenanceResponse(_message.Message):
    __slots__ = ("organization_id", "uptime", "mileage", "price", "started_at", "finished_at", "services", "devices")
    class Cost(_message.Message):
        __slots__ = ("name", "price", "description")
        NAME_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        name: str
        price: int
        description: str
        def __init__(self, name: _Optional[str] = ..., price: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...
    class List(_message.Message):
        __slots__ = ("id", "service_id", "started_at", "expires_at", "duration_percentage", "current_uptime", "uptime", "uptime_percentage", "current_mileage", "mileage", "mileage_percentage", "status", "cost", "price", "count", "created_at", "updated_at")
        ID_FIELD_NUMBER: _ClassVar[int]
        SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
        STARTED_AT_FIELD_NUMBER: _ClassVar[int]
        EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
        DURATION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
        CURRENT_UPTIME_FIELD_NUMBER: _ClassVar[int]
        UPTIME_FIELD_NUMBER: _ClassVar[int]
        UPTIME_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
        CURRENT_MILEAGE_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        COST_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
        id: int
        service_id: int
        started_at: _timestamp_pb2.Timestamp
        expires_at: _timestamp_pb2.Timestamp
        duration_percentage: int
        current_uptime: int
        uptime: int
        uptime_percentage: int
        current_mileage: int
        mileage: int
        mileage_percentage: int
        status: int
        cost: _containers.RepeatedCompositeFieldContainer[MaintenanceResponse.Cost]
        price: int
        count: int
        created_at: _timestamp_pb2.Timestamp
        updated_at: _timestamp_pb2.Timestamp
        def __init__(self, id: _Optional[int] = ..., service_id: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., duration_percentage: _Optional[int] = ..., current_uptime: _Optional[int] = ..., uptime: _Optional[int] = ..., uptime_percentage: _Optional[int] = ..., current_mileage: _Optional[int] = ..., mileage: _Optional[int] = ..., mileage_percentage: _Optional[int] = ..., status: _Optional[int] = ..., cost: _Optional[_Iterable[_Union[MaintenanceResponse.Cost, _Mapping]]] = ..., price: _Optional[int] = ..., count: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    class Group(_message.Message):
        __slots__ = ("uptime", "mileage", "price", "started_at", "finished_at", "services", "list")
        UPTIME_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        STARTED_AT_FIELD_NUMBER: _ClassVar[int]
        FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
        SERVICES_FIELD_NUMBER: _ClassVar[int]
        LIST_FIELD_NUMBER: _ClassVar[int]
        uptime: int
        mileage: int
        price: int
        started_at: _timestamp_pb2.Timestamp
        finished_at: _timestamp_pb2.Timestamp
        services: _containers.RepeatedCompositeFieldContainer[MaintenanceResponse.Service]
        list: _containers.RepeatedCompositeFieldContainer[MaintenanceResponse.List]
        def __init__(self, uptime: _Optional[int] = ..., mileage: _Optional[int] = ..., price: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., services: _Optional[_Iterable[_Union[MaintenanceResponse.Service, _Mapping]]] = ..., list: _Optional[_Iterable[_Union[MaintenanceResponse.List, _Mapping]]] = ...) -> None: ...
    class Service(_message.Message):
        __slots__ = ("service_id", "name", "price", "count")
        SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        service_id: int
        name: str
        price: int
        count: int
        def __init__(self, service_id: _Optional[int] = ..., name: _Optional[str] = ..., price: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...
    class Device(_message.Message):
        __slots__ = ("device_id", "organization_id", "uptime", "mileage", "price", "services", "groups")
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        UPTIME_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        SERVICES_FIELD_NUMBER: _ClassVar[int]
        GROUPS_FIELD_NUMBER: _ClassVar[int]
        device_id: int
        organization_id: int
        uptime: int
        mileage: int
        price: int
        services: _containers.RepeatedCompositeFieldContainer[MaintenanceResponse.Service]
        groups: _containers.RepeatedCompositeFieldContainer[MaintenanceResponse.Group]
        def __init__(self, device_id: _Optional[int] = ..., organization_id: _Optional[int] = ..., uptime: _Optional[int] = ..., mileage: _Optional[int] = ..., price: _Optional[int] = ..., services: _Optional[_Iterable[_Union[MaintenanceResponse.Service, _Mapping]]] = ..., groups: _Optional[_Iterable[_Union[MaintenanceResponse.Group, _Mapping]]] = ...) -> None: ...
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    UPTIME_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    SERVICES_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    organization_id: int
    uptime: int
    mileage: int
    price: int
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    services: _containers.RepeatedCompositeFieldContainer[MaintenanceResponse.Service]
    devices: _containers.RepeatedCompositeFieldContainer[MaintenanceResponse.Device]
    def __init__(self, organization_id: _Optional[int] = ..., uptime: _Optional[int] = ..., mileage: _Optional[int] = ..., price: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., services: _Optional[_Iterable[_Union[MaintenanceResponse.Service, _Mapping]]] = ..., devices: _Optional[_Iterable[_Union[MaintenanceResponse.Device, _Mapping]]] = ...) -> None: ...

class TripPerformanceRequest(_message.Message):
    __slots__ = ("device_id", "started_at", "finished_at", "group_by_device", "group_by_datetime", "hourly")
    class GroupBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        All: _ClassVar[TripPerformanceRequest.GroupBy]
        Day: _ClassVar[TripPerformanceRequest.GroupBy]
        Month: _ClassVar[TripPerformanceRequest.GroupBy]
        Year: _ClassVar[TripPerformanceRequest.GroupBy]
        Hour: _ClassVar[TripPerformanceRequest.GroupBy]
    All: TripPerformanceRequest.GroupBy
    Day: TripPerformanceRequest.GroupBy
    Month: TripPerformanceRequest.GroupBy
    Year: TripPerformanceRequest.GroupBy
    Hour: TripPerformanceRequest.GroupBy
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    GROUP_BY_DEVICE_FIELD_NUMBER: _ClassVar[int]
    GROUP_BY_DATETIME_FIELD_NUMBER: _ClassVar[int]
    HOURLY_FIELD_NUMBER: _ClassVar[int]
    device_id: _containers.RepeatedScalarFieldContainer[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    group_by_device: bool
    group_by_datetime: TripPerformanceRequest.GroupBy
    hourly: bool
    def __init__(self, device_id: _Optional[_Iterable[int]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., group_by_device: bool = ..., group_by_datetime: _Optional[_Union[TripPerformanceRequest.GroupBy, str]] = ..., hourly: bool = ...) -> None: ...

class TripPerformanceResponse(_message.Message):
    __slots__ = ("data", "cost", "threads", "records")
    DATA_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    THREADS_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[TripPerformance]
    cost: int
    threads: int
    records: int
    def __init__(self, data: _Optional[_Iterable[_Union[TripPerformance, _Mapping]]] = ..., cost: _Optional[int] = ..., threads: _Optional[int] = ..., records: _Optional[int] = ...) -> None: ...

class TripPerformance(_message.Message):
    __slots__ = ("device_id", "mileage", "idling", "parking", "moving", "towing", "total_speed", "sum_speed", "max_speed", "started_at", "finished_at", "driving", "temperature", "humidity", "i_button", "ignition", "door_opened", "fuel_used", "fuel_rate", "engine_rpm", "engine_load", "crashes", "speeds", "points", "records", "average")
    class Average(_message.Message):
        __slots__ = ("name", "uint_value", "int_value", "seconds", "kind")
        NAME_FIELD_NUMBER: _ClassVar[int]
        UINT_VALUE_FIELD_NUMBER: _ClassVar[int]
        INT_VALUE_FIELD_NUMBER: _ClassVar[int]
        SECONDS_FIELD_NUMBER: _ClassVar[int]
        KIND_FIELD_NUMBER: _ClassVar[int]
        name: str
        uint_value: int
        int_value: int
        seconds: int
        kind: int
        def __init__(self, name: _Optional[str] = ..., uint_value: _Optional[int] = ..., int_value: _Optional[int] = ..., seconds: _Optional[int] = ..., kind: _Optional[int] = ...) -> None: ...
    class DrivingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class TemperatureEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class HumidityEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class CrashesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class SpeedsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: _trip_pb2.TripDurationStat
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[_trip_pb2.TripDurationStat, _Mapping]] = ...) -> None: ...
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    IDLING_FIELD_NUMBER: _ClassVar[int]
    PARKING_FIELD_NUMBER: _ClassVar[int]
    MOVING_FIELD_NUMBER: _ClassVar[int]
    TOWING_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SPEED_FIELD_NUMBER: _ClassVar[int]
    SUM_SPEED_FIELD_NUMBER: _ClassVar[int]
    MAX_SPEED_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    DRIVING_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    HUMIDITY_FIELD_NUMBER: _ClassVar[int]
    I_BUTTON_FIELD_NUMBER: _ClassVar[int]
    IGNITION_FIELD_NUMBER: _ClassVar[int]
    DOOR_OPENED_FIELD_NUMBER: _ClassVar[int]
    FUEL_USED_FIELD_NUMBER: _ClassVar[int]
    FUEL_RATE_FIELD_NUMBER: _ClassVar[int]
    ENGINE_RPM_FIELD_NUMBER: _ClassVar[int]
    ENGINE_LOAD_FIELD_NUMBER: _ClassVar[int]
    CRASHES_FIELD_NUMBER: _ClassVar[int]
    SPEEDS_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    mileage: int
    idling: int
    parking: int
    moving: int
    towing: int
    total_speed: int
    sum_speed: int
    max_speed: int
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    driving: _containers.ScalarMap[str, int]
    temperature: _containers.ScalarMap[str, int]
    humidity: _containers.ScalarMap[str, int]
    i_button: _containers.RepeatedScalarFieldContainer[int]
    ignition: int
    door_opened: int
    fuel_used: int
    fuel_rate: int
    engine_rpm: int
    engine_load: int
    crashes: _containers.ScalarMap[str, int]
    speeds: _containers.MessageMap[int, _trip_pb2.TripDurationStat]
    points: int
    records: int
    average: _containers.RepeatedCompositeFieldContainer[TripPerformance.Average]
    def __init__(self, device_id: _Optional[int] = ..., mileage: _Optional[int] = ..., idling: _Optional[int] = ..., parking: _Optional[int] = ..., moving: _Optional[int] = ..., towing: _Optional[int] = ..., total_speed: _Optional[int] = ..., sum_speed: _Optional[int] = ..., max_speed: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., driving: _Optional[_Mapping[str, int]] = ..., temperature: _Optional[_Mapping[str, int]] = ..., humidity: _Optional[_Mapping[str, int]] = ..., i_button: _Optional[_Iterable[int]] = ..., ignition: _Optional[int] = ..., door_opened: _Optional[int] = ..., fuel_used: _Optional[int] = ..., fuel_rate: _Optional[int] = ..., engine_rpm: _Optional[int] = ..., engine_load: _Optional[int] = ..., crashes: _Optional[_Mapping[str, int]] = ..., speeds: _Optional[_Mapping[int, _trip_pb2.TripDurationStat]] = ..., points: _Optional[int] = ..., records: _Optional[int] = ..., average: _Optional[_Iterable[_Union[TripPerformance.Average, _Mapping]]] = ...) -> None: ...

class LatestDataModelRequest(_message.Message):
    __slots__ = ("device_id",)
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    def __init__(self, device_id: _Optional[int] = ...) -> None: ...

class DashboardIndividualResponse(_message.Message):
    __slots__ = ("data_list", "title", "mileage", "weight", "fuel_used", "fuel_rate", "trips", "idling", "parking", "moving", "towing", "total_speed", "sum_speed", "max_speed", "points", "environmental", "green_driving", "speeds", "crashes", "cost", "threads", "records")
    class Environmental(_message.Message):
        __slots__ = ("temperature", "humidity")
        class TemperatureEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        class HumidityEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
        HUMIDITY_FIELD_NUMBER: _ClassVar[int]
        temperature: _containers.ScalarMap[int, int]
        humidity: _containers.ScalarMap[int, int]
        def __init__(self, temperature: _Optional[_Mapping[int, int]] = ..., humidity: _Optional[_Mapping[int, int]] = ...) -> None: ...
    class GreenDrivingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    class SpeedsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: _trip_pb2.TripDurationStat
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[_trip_pb2.TripDurationStat, _Mapping]] = ...) -> None: ...
    DATA_LIST_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    FUEL_USED_FIELD_NUMBER: _ClassVar[int]
    FUEL_RATE_FIELD_NUMBER: _ClassVar[int]
    TRIPS_FIELD_NUMBER: _ClassVar[int]
    IDLING_FIELD_NUMBER: _ClassVar[int]
    PARKING_FIELD_NUMBER: _ClassVar[int]
    MOVING_FIELD_NUMBER: _ClassVar[int]
    TOWING_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SPEED_FIELD_NUMBER: _ClassVar[int]
    SUM_SPEED_FIELD_NUMBER: _ClassVar[int]
    MAX_SPEED_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENTAL_FIELD_NUMBER: _ClassVar[int]
    GREEN_DRIVING_FIELD_NUMBER: _ClassVar[int]
    SPEEDS_FIELD_NUMBER: _ClassVar[int]
    CRASHES_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    THREADS_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    data_list: _containers.RepeatedCompositeFieldContainer[_dataModel_pb2.Data]
    title: _containers.RepeatedScalarFieldContainer[str]
    mileage: _containers.RepeatedScalarFieldContainer[int]
    weight: _containers.RepeatedScalarFieldContainer[int]
    fuel_used: _containers.RepeatedScalarFieldContainer[int]
    fuel_rate: _containers.RepeatedScalarFieldContainer[int]
    trips: _containers.RepeatedScalarFieldContainer[int]
    idling: _containers.RepeatedScalarFieldContainer[int]
    parking: _containers.RepeatedScalarFieldContainer[int]
    moving: _containers.RepeatedScalarFieldContainer[int]
    towing: _containers.RepeatedScalarFieldContainer[int]
    total_speed: _containers.RepeatedScalarFieldContainer[int]
    sum_speed: _containers.RepeatedScalarFieldContainer[int]
    max_speed: _containers.RepeatedScalarFieldContainer[int]
    points: _containers.RepeatedCompositeFieldContainer[_trip_pb2.TripPoint]
    environmental: _containers.RepeatedCompositeFieldContainer[DashboardIndividualResponse.Environmental]
    green_driving: _containers.ScalarMap[int, int]
    speeds: _containers.MessageMap[int, _trip_pb2.TripDurationStat]
    crashes: int
    cost: int
    threads: int
    records: int
    def __init__(self, data_list: _Optional[_Iterable[_Union[_dataModel_pb2.Data, _Mapping]]] = ..., title: _Optional[_Iterable[str]] = ..., mileage: _Optional[_Iterable[int]] = ..., weight: _Optional[_Iterable[int]] = ..., fuel_used: _Optional[_Iterable[int]] = ..., fuel_rate: _Optional[_Iterable[int]] = ..., trips: _Optional[_Iterable[int]] = ..., idling: _Optional[_Iterable[int]] = ..., parking: _Optional[_Iterable[int]] = ..., moving: _Optional[_Iterable[int]] = ..., towing: _Optional[_Iterable[int]] = ..., total_speed: _Optional[_Iterable[int]] = ..., sum_speed: _Optional[_Iterable[int]] = ..., max_speed: _Optional[_Iterable[int]] = ..., points: _Optional[_Iterable[_Union[_trip_pb2.TripPoint, _Mapping]]] = ..., environmental: _Optional[_Iterable[_Union[DashboardIndividualResponse.Environmental, _Mapping]]] = ..., green_driving: _Optional[_Mapping[int, int]] = ..., speeds: _Optional[_Mapping[int, _trip_pb2.TripDurationStat]] = ..., crashes: _Optional[int] = ..., cost: _Optional[int] = ..., threads: _Optional[int] = ..., records: _Optional[int] = ...) -> None: ...

class DashboardIndividualRequest(_message.Message):
    __slots__ = ("device_id", "started_at", "finished_at")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    def __init__(self, device_id: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TraffixResponse(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Traffix]
    def __init__(self, list: _Optional[_Iterable[_Union[Traffix, _Mapping]]] = ...) -> None: ...

class Traffix(_message.Message):
    __slots__ = ("device_id", "date_time", "work_started_at", "work_finished_at", "home_started_at", "home_finished_at", "work_traffic", "home_traffic", "stop_list", "work_time_mileage", "total_mileage", "home_to_work_mileage", "work_to_work_mileage", "work_to_home_mileage")
    class Event(_message.Message):
        __slots__ = ("area_id", "started_at", "finished_at", "mileage", "duration", "type", "group_id", "mileage_sum")
        class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            NONE: _ClassVar[Traffix.Event.Type]
            INSIDE: _ClassVar[Traffix.Event.Type]
            OUTSIDE: _ClassVar[Traffix.Event.Type]
        NONE: Traffix.Event.Type
        INSIDE: Traffix.Event.Type
        OUTSIDE: Traffix.Event.Type
        AREA_ID_FIELD_NUMBER: _ClassVar[int]
        STARTED_AT_FIELD_NUMBER: _ClassVar[int]
        FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        DURATION_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        GROUP_ID_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_SUM_FIELD_NUMBER: _ClassVar[int]
        area_id: int
        started_at: _timestamp_pb2.Timestamp
        finished_at: _timestamp_pb2.Timestamp
        mileage: int
        duration: int
        type: Traffix.Event.Type
        group_id: int
        mileage_sum: int
        def __init__(self, area_id: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., mileage: _Optional[int] = ..., duration: _Optional[int] = ..., type: _Optional[_Union[Traffix.Event.Type, str]] = ..., group_id: _Optional[int] = ..., mileage_sum: _Optional[int] = ...) -> None: ...
    class STOP(_message.Message):
        __slots__ = ("started_at", "finished_at", "duration")
        STARTED_AT_FIELD_NUMBER: _ClassVar[int]
        FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
        DURATION_FIELD_NUMBER: _ClassVar[int]
        started_at: _timestamp_pb2.Timestamp
        finished_at: _timestamp_pb2.Timestamp
        duration: int
        def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., duration: _Optional[int] = ...) -> None: ...
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    WORK_STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    WORK_FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    HOME_STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    HOME_FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    WORK_TRAFFIC_FIELD_NUMBER: _ClassVar[int]
    HOME_TRAFFIC_FIELD_NUMBER: _ClassVar[int]
    STOP_LIST_FIELD_NUMBER: _ClassVar[int]
    WORK_TIME_MILEAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_MILEAGE_FIELD_NUMBER: _ClassVar[int]
    HOME_TO_WORK_MILEAGE_FIELD_NUMBER: _ClassVar[int]
    WORK_TO_WORK_MILEAGE_FIELD_NUMBER: _ClassVar[int]
    WORK_TO_HOME_MILEAGE_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    date_time: _timestamp_pb2.Timestamp
    work_started_at: _timestamp_pb2.Timestamp
    work_finished_at: _timestamp_pb2.Timestamp
    home_started_at: _timestamp_pb2.Timestamp
    home_finished_at: _timestamp_pb2.Timestamp
    work_traffic: _containers.RepeatedCompositeFieldContainer[Traffix.Event]
    home_traffic: _containers.RepeatedCompositeFieldContainer[Traffix.Event]
    stop_list: _containers.RepeatedCompositeFieldContainer[Traffix.STOP]
    work_time_mileage: int
    total_mileage: int
    home_to_work_mileage: int
    work_to_work_mileage: int
    work_to_home_mileage: int
    def __init__(self, device_id: _Optional[int] = ..., date_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., work_started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., work_finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., home_started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., home_finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., work_traffic: _Optional[_Iterable[_Union[Traffix.Event, _Mapping]]] = ..., home_traffic: _Optional[_Iterable[_Union[Traffix.Event, _Mapping]]] = ..., stop_list: _Optional[_Iterable[_Union[Traffix.STOP, _Mapping]]] = ..., work_time_mileage: _Optional[int] = ..., total_mileage: _Optional[int] = ..., home_to_work_mileage: _Optional[int] = ..., work_to_work_mileage: _Optional[int] = ..., work_to_home_mileage: _Optional[int] = ...) -> None: ...

class TraffixRequest(_message.Message):
    __slots__ = ("device_ids", "started_at", "finished_at", "work_starts", "work_finishes")
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    WORK_STARTS_FIELD_NUMBER: _ClassVar[int]
    WORK_FINISHES_FIELD_NUMBER: _ClassVar[int]
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    work_starts: str
    work_finishes: str
    def __init__(self, device_ids: _Optional[_Iterable[int]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., work_starts: _Optional[str] = ..., work_finishes: _Optional[str] = ...) -> None: ...

class TripReportResponse(_message.Message):
    __slots__ = ("cost", "threads", "records", "trips")
    COST_FIELD_NUMBER: _ClassVar[int]
    THREADS_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    TRIPS_FIELD_NUMBER: _ClassVar[int]
    cost: int
    threads: int
    records: int
    trips: _containers.RepeatedCompositeFieldContainer[_trip_pb2.Trip]
    def __init__(self, cost: _Optional[int] = ..., threads: _Optional[int] = ..., records: _Optional[int] = ..., trips: _Optional[_Iterable[_Union[_trip_pb2.Trip, _Mapping]]] = ...) -> None: ...

class AreaSummaryReviewRequest(_message.Message):
    __slots__ = ("started_at", "finished_at", "scope", "source", "area_source", "area_ids", "device_ids")
    class ScopeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        inside_only: _ClassVar[AreaSummaryReviewRequest.ScopeEnum]
        outside_only: _ClassVar[AreaSummaryReviewRequest.ScopeEnum]
        both_side: _ClassVar[AreaSummaryReviewRequest.ScopeEnum]
    inside_only: AreaSummaryReviewRequest.ScopeEnum
    outside_only: AreaSummaryReviewRequest.ScopeEnum
    both_side: AreaSummaryReviewRequest.ScopeEnum
    class AreaSourceEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        fusion: _ClassVar[AreaSummaryReviewRequest.AreaSourceEnum]
        odyssey: _ClassVar[AreaSummaryReviewRequest.AreaSourceEnum]
    fusion: AreaSummaryReviewRequest.AreaSourceEnum
    odyssey: AreaSummaryReviewRequest.AreaSourceEnum
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    AREA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    AREA_IDS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    scope: AreaSummaryReviewRequest.ScopeEnum
    source: Source
    area_source: AreaSummaryReviewRequest.AreaSourceEnum
    area_ids: _containers.RepeatedScalarFieldContainer[int]
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., scope: _Optional[_Union[AreaSummaryReviewRequest.ScopeEnum, str]] = ..., source: _Optional[_Union[Source, str]] = ..., area_source: _Optional[_Union[AreaSummaryReviewRequest.AreaSourceEnum, str]] = ..., area_ids: _Optional[_Iterable[int]] = ..., device_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class AreaSummaryReviewResponse(_message.Message):
    __slots__ = ("records", "cost", "total_duration_inside", "total_duration_outside", "total_mileage_inside", "total_mileage_outside", "total_inside_records", "total_outside_records", "reports")
    class trafficType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        inside: _ClassVar[AreaSummaryReviewResponse.trafficType]
        outSide: _ClassVar[AreaSummaryReviewResponse.trafficType]
    inside: AreaSummaryReviewResponse.trafficType
    outSide: AreaSummaryReviewResponse.trafficType
    class Review(_message.Message):
        __slots__ = ("device_id", "area_id", "started", "finished", "mileage", "duration", "max_speed", "total_speed", "count_speed", "type", "area")
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        AREA_ID_FIELD_NUMBER: _ClassVar[int]
        STARTED_FIELD_NUMBER: _ClassVar[int]
        FINISHED_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        DURATION_FIELD_NUMBER: _ClassVar[int]
        MAX_SPEED_FIELD_NUMBER: _ClassVar[int]
        TOTAL_SPEED_FIELD_NUMBER: _ClassVar[int]
        COUNT_SPEED_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        AREA_FIELD_NUMBER: _ClassVar[int]
        device_id: int
        area_id: int
        started: _dataModel_pb2.Data
        finished: _dataModel_pb2.Data
        mileage: int
        duration: int
        max_speed: int
        total_speed: int
        count_speed: int
        type: AreaSummaryReviewResponse.trafficType
        area: _area_pb2.Area
        def __init__(self, device_id: _Optional[int] = ..., area_id: _Optional[int] = ..., started: _Optional[_Union[_dataModel_pb2.Data, _Mapping]] = ..., finished: _Optional[_Union[_dataModel_pb2.Data, _Mapping]] = ..., mileage: _Optional[int] = ..., duration: _Optional[int] = ..., max_speed: _Optional[int] = ..., total_speed: _Optional[int] = ..., count_speed: _Optional[int] = ..., type: _Optional[_Union[AreaSummaryReviewResponse.trafficType, str]] = ..., area: _Optional[_Union[_area_pb2.Area, _Mapping]] = ...) -> None: ...
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_DURATION_INSIDE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_DURATION_OUTSIDE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_MILEAGE_INSIDE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_MILEAGE_OUTSIDE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_INSIDE_RECORDS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_OUTSIDE_RECORDS_FIELD_NUMBER: _ClassVar[int]
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    records: int
    cost: int
    total_duration_inside: int
    total_duration_outside: int
    total_mileage_inside: int
    total_mileage_outside: int
    total_inside_records: int
    total_outside_records: int
    reports: _containers.RepeatedCompositeFieldContainer[AreaSummaryReviewResponse.Review]
    def __init__(self, records: _Optional[int] = ..., cost: _Optional[int] = ..., total_duration_inside: _Optional[int] = ..., total_duration_outside: _Optional[int] = ..., total_mileage_inside: _Optional[int] = ..., total_mileage_outside: _Optional[int] = ..., total_inside_records: _Optional[int] = ..., total_outside_records: _Optional[int] = ..., reports: _Optional[_Iterable[_Union[AreaSummaryReviewResponse.Review, _Mapping]]] = ...) -> None: ...

class ShiftSummaryResponse(_message.Message):
    __slots__ = ("Reports", "trip_records", "trip_milliseconds", "started_at", "finished_at")
    class Summary(_message.Message):
        __slots__ = ("device_id", "mileage", "idling", "parking", "moving", "towing", "speed_total", "speed_sum", "speed_max", "records", "harsh_acceleration", "harsh_break", "harsh_corner", "min_temp_01", "max_temp_01", "min_temp_02", "max_temp_02", "min_temp_03", "max_temp_03", "min_temp_04", "max_temp_04", "min_humidity", "max_humidity", "started_at", "finished_at", "totalSeconds", "includingSeconds", "different")
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        IDLING_FIELD_NUMBER: _ClassVar[int]
        PARKING_FIELD_NUMBER: _ClassVar[int]
        MOVING_FIELD_NUMBER: _ClassVar[int]
        TOWING_FIELD_NUMBER: _ClassVar[int]
        SPEED_TOTAL_FIELD_NUMBER: _ClassVar[int]
        SPEED_SUM_FIELD_NUMBER: _ClassVar[int]
        SPEED_MAX_FIELD_NUMBER: _ClassVar[int]
        RECORDS_FIELD_NUMBER: _ClassVar[int]
        HARSH_ACCELERATION_FIELD_NUMBER: _ClassVar[int]
        HARSH_BREAK_FIELD_NUMBER: _ClassVar[int]
        HARSH_CORNER_FIELD_NUMBER: _ClassVar[int]
        MIN_TEMP_01_FIELD_NUMBER: _ClassVar[int]
        MAX_TEMP_01_FIELD_NUMBER: _ClassVar[int]
        MIN_TEMP_02_FIELD_NUMBER: _ClassVar[int]
        MAX_TEMP_02_FIELD_NUMBER: _ClassVar[int]
        MIN_TEMP_03_FIELD_NUMBER: _ClassVar[int]
        MAX_TEMP_03_FIELD_NUMBER: _ClassVar[int]
        MIN_TEMP_04_FIELD_NUMBER: _ClassVar[int]
        MAX_TEMP_04_FIELD_NUMBER: _ClassVar[int]
        MIN_HUMIDITY_FIELD_NUMBER: _ClassVar[int]
        MAX_HUMIDITY_FIELD_NUMBER: _ClassVar[int]
        STARTED_AT_FIELD_NUMBER: _ClassVar[int]
        FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
        TOTALSECONDS_FIELD_NUMBER: _ClassVar[int]
        INCLUDINGSECONDS_FIELD_NUMBER: _ClassVar[int]
        DIFFERENT_FIELD_NUMBER: _ClassVar[int]
        device_id: int
        mileage: int
        idling: int
        parking: int
        moving: int
        towing: int
        speed_total: int
        speed_sum: int
        speed_max: int
        records: int
        harsh_acceleration: int
        harsh_break: int
        harsh_corner: int
        min_temp_01: int
        max_temp_01: int
        min_temp_02: int
        max_temp_02: int
        min_temp_03: int
        max_temp_03: int
        min_temp_04: int
        max_temp_04: int
        min_humidity: int
        max_humidity: int
        started_at: _timestamp_pb2.Timestamp
        finished_at: _timestamp_pb2.Timestamp
        totalSeconds: int
        includingSeconds: int
        different: int
        def __init__(self, device_id: _Optional[int] = ..., mileage: _Optional[int] = ..., idling: _Optional[int] = ..., parking: _Optional[int] = ..., moving: _Optional[int] = ..., towing: _Optional[int] = ..., speed_total: _Optional[int] = ..., speed_sum: _Optional[int] = ..., speed_max: _Optional[int] = ..., records: _Optional[int] = ..., harsh_acceleration: _Optional[int] = ..., harsh_break: _Optional[int] = ..., harsh_corner: _Optional[int] = ..., min_temp_01: _Optional[int] = ..., max_temp_01: _Optional[int] = ..., min_temp_02: _Optional[int] = ..., max_temp_02: _Optional[int] = ..., min_temp_03: _Optional[int] = ..., max_temp_03: _Optional[int] = ..., min_temp_04: _Optional[int] = ..., max_temp_04: _Optional[int] = ..., min_humidity: _Optional[int] = ..., max_humidity: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., totalSeconds: _Optional[int] = ..., includingSeconds: _Optional[int] = ..., different: _Optional[int] = ...) -> None: ...
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    TRIP_RECORDS_FIELD_NUMBER: _ClassVar[int]
    TRIP_MILLISECONDS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    Reports: _containers.RepeatedCompositeFieldContainer[ShiftSummaryResponse.Summary]
    trip_records: int
    trip_milliseconds: int
    started_at: str
    finished_at: str
    def __init__(self, Reports: _Optional[_Iterable[_Union[ShiftSummaryResponse.Summary, _Mapping]]] = ..., trip_records: _Optional[int] = ..., trip_milliseconds: _Optional[int] = ..., started_at: _Optional[str] = ..., finished_at: _Optional[str] = ...) -> None: ...

class ShiftRequest(_message.Message):
    __slots__ = ("started_at", "finished_at", "device_ids")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., device_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class ShiftResponse(_message.Message):
    __slots__ = ("Reports",)
    class Shift(_message.Message):
        __slots__ = ("id", "device_id", "shift_id", "mileage", "idling", "parking", "moving", "towing", "speed_total", "speed_sum", "speed_max", "records", "harsh_acceleration", "harsh_break", "harsh_corner", "min_temp_01", "max_temp_01", "min_temp_02", "max_temp_02", "min_temp_03", "max_temp_03", "min_temp_04", "max_temp_04", "min_humidity", "max_humidity", "start_lat", "start_lng", "finish_lat", "finish_lng", "started_at", "finished_at", "created_at", "updated_at")
        ID_FIELD_NUMBER: _ClassVar[int]
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        SHIFT_ID_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        IDLING_FIELD_NUMBER: _ClassVar[int]
        PARKING_FIELD_NUMBER: _ClassVar[int]
        MOVING_FIELD_NUMBER: _ClassVar[int]
        TOWING_FIELD_NUMBER: _ClassVar[int]
        SPEED_TOTAL_FIELD_NUMBER: _ClassVar[int]
        SPEED_SUM_FIELD_NUMBER: _ClassVar[int]
        SPEED_MAX_FIELD_NUMBER: _ClassVar[int]
        RECORDS_FIELD_NUMBER: _ClassVar[int]
        HARSH_ACCELERATION_FIELD_NUMBER: _ClassVar[int]
        HARSH_BREAK_FIELD_NUMBER: _ClassVar[int]
        HARSH_CORNER_FIELD_NUMBER: _ClassVar[int]
        MIN_TEMP_01_FIELD_NUMBER: _ClassVar[int]
        MAX_TEMP_01_FIELD_NUMBER: _ClassVar[int]
        MIN_TEMP_02_FIELD_NUMBER: _ClassVar[int]
        MAX_TEMP_02_FIELD_NUMBER: _ClassVar[int]
        MIN_TEMP_03_FIELD_NUMBER: _ClassVar[int]
        MAX_TEMP_03_FIELD_NUMBER: _ClassVar[int]
        MIN_TEMP_04_FIELD_NUMBER: _ClassVar[int]
        MAX_TEMP_04_FIELD_NUMBER: _ClassVar[int]
        MIN_HUMIDITY_FIELD_NUMBER: _ClassVar[int]
        MAX_HUMIDITY_FIELD_NUMBER: _ClassVar[int]
        START_LAT_FIELD_NUMBER: _ClassVar[int]
        START_LNG_FIELD_NUMBER: _ClassVar[int]
        FINISH_LAT_FIELD_NUMBER: _ClassVar[int]
        FINISH_LNG_FIELD_NUMBER: _ClassVar[int]
        STARTED_AT_FIELD_NUMBER: _ClassVar[int]
        FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
        id: int
        device_id: int
        shift_id: int
        mileage: int
        idling: int
        parking: int
        moving: int
        towing: int
        speed_total: int
        speed_sum: int
        speed_max: int
        records: int
        harsh_acceleration: int
        harsh_break: int
        harsh_corner: int
        min_temp_01: int
        max_temp_01: int
        min_temp_02: int
        max_temp_02: int
        min_temp_03: int
        max_temp_03: int
        min_temp_04: int
        max_temp_04: int
        min_humidity: int
        max_humidity: int
        start_lat: float
        start_lng: float
        finish_lat: float
        finish_lng: float
        started_at: _timestamp_pb2.Timestamp
        finished_at: _timestamp_pb2.Timestamp
        created_at: _timestamp_pb2.Timestamp
        updated_at: _timestamp_pb2.Timestamp
        def __init__(self, id: _Optional[int] = ..., device_id: _Optional[int] = ..., shift_id: _Optional[int] = ..., mileage: _Optional[int] = ..., idling: _Optional[int] = ..., parking: _Optional[int] = ..., moving: _Optional[int] = ..., towing: _Optional[int] = ..., speed_total: _Optional[int] = ..., speed_sum: _Optional[int] = ..., speed_max: _Optional[int] = ..., records: _Optional[int] = ..., harsh_acceleration: _Optional[int] = ..., harsh_break: _Optional[int] = ..., harsh_corner: _Optional[int] = ..., min_temp_01: _Optional[int] = ..., max_temp_01: _Optional[int] = ..., min_temp_02: _Optional[int] = ..., max_temp_02: _Optional[int] = ..., min_temp_03: _Optional[int] = ..., max_temp_03: _Optional[int] = ..., min_temp_04: _Optional[int] = ..., max_temp_04: _Optional[int] = ..., min_humidity: _Optional[int] = ..., max_humidity: _Optional[int] = ..., start_lat: _Optional[float] = ..., start_lng: _Optional[float] = ..., finish_lat: _Optional[float] = ..., finish_lng: _Optional[float] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    Reports: _containers.RepeatedCompositeFieldContainer[ShiftResponse.Shift]
    def __init__(self, Reports: _Optional[_Iterable[_Union[ShiftResponse.Shift, _Mapping]]] = ...) -> None: ...

class ShiftSummaryRequest(_message.Message):
    __slots__ = ("started_at", "finished_at", "device_ids")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., device_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class DeviceDataCountRequest(_message.Message):
    __slots__ = ("started_at", "finished_at", "device_ids")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., device_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class DeviceDataCountResponse(_message.Message):
    __slots__ = ("Reports",)
    class DeviceDataCount(_message.Message):
        __slots__ = ("device_id", "count")
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        device_id: int
        count: int
        def __init__(self, device_id: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    Reports: _containers.RepeatedCompositeFieldContainer[DeviceDataCountResponse.DeviceDataCount]
    def __init__(self, Reports: _Optional[_Iterable[_Union[DeviceDataCountResponse.DeviceDataCount, _Mapping]]] = ...) -> None: ...

class DailyTrafficResponse(_message.Message):
    __slots__ = ("Reports",)
    class Traffic(_message.Message):
        __slots__ = ("entered_at", "exited_at", "mileage", "geo_id", "geo_name")
        ENTERED_AT_FIELD_NUMBER: _ClassVar[int]
        EXITED_AT_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        GEO_ID_FIELD_NUMBER: _ClassVar[int]
        GEO_NAME_FIELD_NUMBER: _ClassVar[int]
        entered_at: _timestamp_pb2.Timestamp
        exited_at: _timestamp_pb2.Timestamp
        mileage: int
        geo_id: int
        geo_name: str
        def __init__(self, entered_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., exited_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., mileage: _Optional[int] = ..., geo_id: _Optional[int] = ..., geo_name: _Optional[str] = ...) -> None: ...
    class DailyTraffic(_message.Message):
        __slots__ = ("device_id", "date", "traffics")
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        DATE_FIELD_NUMBER: _ClassVar[int]
        TRAFFICS_FIELD_NUMBER: _ClassVar[int]
        device_id: int
        date: _timestamp_pb2.Timestamp
        traffics: _containers.RepeatedCompositeFieldContainer[DailyTrafficResponse.Traffic]
        def __init__(self, device_id: _Optional[int] = ..., date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., traffics: _Optional[_Iterable[_Union[DailyTrafficResponse.Traffic, _Mapping]]] = ...) -> None: ...
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    Reports: _containers.RepeatedCompositeFieldContainer[DailyTrafficResponse.DailyTraffic]
    def __init__(self, Reports: _Optional[_Iterable[_Union[DailyTrafficResponse.DailyTraffic, _Mapping]]] = ...) -> None: ...

class DailyTrafficRequest(_message.Message):
    __slots__ = ("started_at", "finished_at", "between", "device_ids")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    BETWEEN_FIELD_NUMBER: _ClassVar[int]
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    between: bool
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., between: bool = ..., device_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class RouteStopPoint(_message.Message):
    __slots__ = ("duration", "started_at", "finished_at", "type", "point")
    DURATION_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    POINT_FIELD_NUMBER: _ClassVar[int]
    duration: int
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    type: RouteStopType
    point: _area_pb2.Point
    def __init__(self, duration: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., type: _Optional[_Union[RouteStopType, str]] = ..., point: _Optional[_Union[_area_pb2.Point, _Mapping]] = ...) -> None: ...

class RouteStopResponse(_message.Message):
    __slots__ = ("list", "records", "cost", "threads")
    LIST_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    THREADS_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[RouteStopPoint]
    records: int
    cost: int
    threads: int
    def __init__(self, list: _Optional[_Iterable[_Union[RouteStopPoint, _Mapping]]] = ..., records: _Optional[int] = ..., cost: _Optional[int] = ..., threads: _Optional[int] = ...) -> None: ...

class RouteStopRequest(_message.Message):
    __slots__ = ("started_at", "finished_at", "source", "stop_type", "device_id")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    STOP_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    source: Source
    stop_type: StopCalculateIo
    device_id: int
    def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., source: _Optional[_Union[Source, str]] = ..., stop_type: _Optional[_Union[StopCalculateIo, str]] = ..., device_id: _Optional[int] = ...) -> None: ...

class RouteReviewRequest(_message.Message):
    __slots__ = ("started_at", "finished_at", "source", "stop_type", "device_id", "include_trip")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    STOP_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_TRIP_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    source: Source
    stop_type: StopCalculateIo
    device_id: int
    include_trip: bool
    def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., source: _Optional[_Union[Source, str]] = ..., stop_type: _Optional[_Union[StopCalculateIo, str]] = ..., device_id: _Optional[int] = ..., include_trip: bool = ...) -> None: ...

class RouteReviewResponse(_message.Message):
    __slots__ = ("route_list", "stop_list", "trip_list", "records", "cost", "threads")
    ROUTE_LIST_FIELD_NUMBER: _ClassVar[int]
    STOP_LIST_FIELD_NUMBER: _ClassVar[int]
    TRIP_LIST_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    THREADS_FIELD_NUMBER: _ClassVar[int]
    route_list: _containers.RepeatedCompositeFieldContainer[_dataModel_pb2.Data]
    stop_list: _containers.RepeatedCompositeFieldContainer[RouteStopPoint]
    trip_list: _containers.RepeatedCompositeFieldContainer[_trip_pb2.Trip]
    records: int
    cost: int
    threads: int
    def __init__(self, route_list: _Optional[_Iterable[_Union[_dataModel_pb2.Data, _Mapping]]] = ..., stop_list: _Optional[_Iterable[_Union[RouteStopPoint, _Mapping]]] = ..., trip_list: _Optional[_Iterable[_Union[_trip_pb2.Trip, _Mapping]]] = ..., records: _Optional[int] = ..., cost: _Optional[int] = ..., threads: _Optional[int] = ...) -> None: ...

class AreaReviewRequest(_message.Message):
    __slots__ = ("started_at", "finished_at", "group_by_day", "area_ids", "device_ids")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    GROUP_BY_DAY_FIELD_NUMBER: _ClassVar[int]
    AREA_IDS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    group_by_day: bool
    area_ids: _containers.RepeatedScalarFieldContainer[int]
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., group_by_day: bool = ..., area_ids: _Optional[_Iterable[int]] = ..., device_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class AreaReviewResponse(_message.Message):
    __slots__ = ("reports",)
    class AreaReview(_message.Message):
        __slots__ = ("device_id", "area_id", "started_at", "finished_at", "mileage", "duration", "type")
        class AreaEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            NONE: _ClassVar[AreaReviewResponse.AreaReview.AreaEventType]
            ENTER: _ClassVar[AreaReviewResponse.AreaReview.AreaEventType]
            EXIT: _ClassVar[AreaReviewResponse.AreaReview.AreaEventType]
        NONE: AreaReviewResponse.AreaReview.AreaEventType
        ENTER: AreaReviewResponse.AreaReview.AreaEventType
        EXIT: AreaReviewResponse.AreaReview.AreaEventType
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        AREA_ID_FIELD_NUMBER: _ClassVar[int]
        STARTED_AT_FIELD_NUMBER: _ClassVar[int]
        FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        DURATION_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        device_id: int
        area_id: int
        started_at: _timestamp_pb2.Timestamp
        finished_at: _timestamp_pb2.Timestamp
        mileage: int
        duration: int
        type: AreaReviewResponse.AreaReview.AreaEventType
        def __init__(self, device_id: _Optional[int] = ..., area_id: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., mileage: _Optional[int] = ..., duration: _Optional[int] = ..., type: _Optional[_Union[AreaReviewResponse.AreaReview.AreaEventType, str]] = ...) -> None: ...
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    reports: _containers.RepeatedCompositeFieldContainer[AreaReviewResponse.AreaReview]
    def __init__(self, reports: _Optional[_Iterable[_Union[AreaReviewResponse.AreaReview, _Mapping]]] = ...) -> None: ...

class DeviceDataRequest(_message.Message):
    __slots__ = ("limit", "device_id", "started_at", "finished_at")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    limit: int
    device_id: int
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    def __init__(self, limit: _Optional[int] = ..., device_id: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DeviceDataResponse(_message.Message):
    __slots__ = ("reports",)
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    reports: _containers.RepeatedCompositeFieldContainer[_dataModel_pb2.Data]
    def __init__(self, reports: _Optional[_Iterable[_Union[_dataModel_pb2.Data, _Mapping]]] = ...) -> None: ...

class LogResponse(_message.Message):
    __slots__ = ("total", "records", "cost", "current_page", "last_page", "data")
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PAGE_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    total: int
    records: int
    cost: int
    current_page: int
    last_page: int
    data: _containers.RepeatedCompositeFieldContainer[_dataModel_pb2.Log]
    def __init__(self, total: _Optional[int] = ..., records: _Optional[int] = ..., cost: _Optional[int] = ..., current_page: _Optional[int] = ..., last_page: _Optional[int] = ..., data: _Optional[_Iterable[_Union[_dataModel_pb2.Log, _Mapping]]] = ...) -> None: ...

class LogRequest(_message.Message):
    __slots__ = ("device_id", "started_at", "finished_at", "page", "limit", "sort", "type")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    page: int
    limit: int
    sort: int
    type: int
    def __init__(self, device_id: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ..., sort: _Optional[int] = ..., type: _Optional[int] = ...) -> None: ...

class TrafficRequest(_message.Message):
    __slots__ = ("started_at", "finished_at", "dataset", "device_ids")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    DATASET_FIELD_NUMBER: _ClassVar[int]
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    dataset: str
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., dataset: _Optional[str] = ..., device_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class TrafficResponse(_message.Message):
    __slots__ = ("reports",)
    class Traffic(_message.Message):
        __slots__ = ("type", "area", "date_time", "area_id", "device_id", "mileage")
        class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            NONE_EVENT: _ClassVar[TrafficResponse.Traffic.EventType]
            ENTER: _ClassVar[TrafficResponse.Traffic.EventType]
            EXIT: _ClassVar[TrafficResponse.Traffic.EventType]
        NONE_EVENT: TrafficResponse.Traffic.EventType
        ENTER: TrafficResponse.Traffic.EventType
        EXIT: TrafficResponse.Traffic.EventType
        TYPE_FIELD_NUMBER: _ClassVar[int]
        AREA_FIELD_NUMBER: _ClassVar[int]
        DATE_TIME_FIELD_NUMBER: _ClassVar[int]
        AREA_ID_FIELD_NUMBER: _ClassVar[int]
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        type: TrafficResponse.Traffic.EventType
        area: str
        date_time: _timestamp_pb2.Timestamp
        area_id: int
        device_id: int
        mileage: int
        def __init__(self, type: _Optional[_Union[TrafficResponse.Traffic.EventType, str]] = ..., area: _Optional[str] = ..., date_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., area_id: _Optional[int] = ..., device_id: _Optional[int] = ..., mileage: _Optional[int] = ...) -> None: ...
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    reports: _containers.RepeatedCompositeFieldContainer[TrafficResponse.Traffic]
    def __init__(self, reports: _Optional[_Iterable[_Union[TrafficResponse.Traffic, _Mapping]]] = ...) -> None: ...

class AttendanceRequest(_message.Message):
    __slots__ = ("device_ids", "started_at", "finished_at")
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    def __init__(self, device_ids: _Optional[_Iterable[int]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AttendanceXRequest(_message.Message):
    __slots__ = ("device_ids", "started_at", "finished_at", "excludeLeaves", "source")
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    EXCLUDELEAVES_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    excludeLeaves: bool
    source: Source
    def __init__(self, device_ids: _Optional[_Iterable[int]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., excludeLeaves: bool = ..., source: _Optional[_Union[Source, str]] = ...) -> None: ...

class AttendanceResponse(_message.Message):
    __slots__ = ("reports",)
    class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE_EVENT: _ClassVar[AttendanceResponse.EventType]
        ENTER: _ClassVar[AttendanceResponse.EventType]
        EXIT: _ClassVar[AttendanceResponse.EventType]
    NONE_EVENT: AttendanceResponse.EventType
    ENTER: AttendanceResponse.EventType
    EXIT: AttendanceResponse.EventType
    class Event(_message.Message):
        __slots__ = ("date_time", "type", "duration", "mileage")
        DATE_TIME_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        DURATION_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_FIELD_NUMBER: _ClassVar[int]
        date_time: _timestamp_pb2.Timestamp
        type: AttendanceResponse.EventType
        duration: int
        mileage: int
        def __init__(self, date_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., type: _Optional[_Union[AttendanceResponse.EventType, str]] = ..., duration: _Optional[int] = ..., mileage: _Optional[int] = ...) -> None: ...
    class Attendance(_message.Message):
        __slots__ = ("entered_at", "exited_at", "device_id", "area_id", "area_name", "geo_name", "overtime", "shortage", "work_time", "price_per_hour", "overtime_price", "shortage_price", "work_time_price", "shift_starts_at", "shift_ends_at", "subtotal", "mileage_inside", "mileage_outside", "events")
        ENTERED_AT_FIELD_NUMBER: _ClassVar[int]
        EXITED_AT_FIELD_NUMBER: _ClassVar[int]
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        AREA_ID_FIELD_NUMBER: _ClassVar[int]
        AREA_NAME_FIELD_NUMBER: _ClassVar[int]
        GEO_NAME_FIELD_NUMBER: _ClassVar[int]
        OVERTIME_FIELD_NUMBER: _ClassVar[int]
        SHORTAGE_FIELD_NUMBER: _ClassVar[int]
        WORK_TIME_FIELD_NUMBER: _ClassVar[int]
        PRICE_PER_HOUR_FIELD_NUMBER: _ClassVar[int]
        OVERTIME_PRICE_FIELD_NUMBER: _ClassVar[int]
        SHORTAGE_PRICE_FIELD_NUMBER: _ClassVar[int]
        WORK_TIME_PRICE_FIELD_NUMBER: _ClassVar[int]
        SHIFT_STARTS_AT_FIELD_NUMBER: _ClassVar[int]
        SHIFT_ENDS_AT_FIELD_NUMBER: _ClassVar[int]
        SUBTOTAL_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_INSIDE_FIELD_NUMBER: _ClassVar[int]
        MILEAGE_OUTSIDE_FIELD_NUMBER: _ClassVar[int]
        EVENTS_FIELD_NUMBER: _ClassVar[int]
        entered_at: _timestamp_pb2.Timestamp
        exited_at: _timestamp_pb2.Timestamp
        device_id: int
        area_id: int
        area_name: str
        geo_name: str
        overtime: int
        shortage: int
        work_time: int
        price_per_hour: int
        overtime_price: int
        shortage_price: int
        work_time_price: int
        shift_starts_at: str
        shift_ends_at: str
        subtotal: int
        mileage_inside: int
        mileage_outside: int
        events: _containers.RepeatedCompositeFieldContainer[AttendanceResponse.Event]
        def __init__(self, entered_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., exited_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., device_id: _Optional[int] = ..., area_id: _Optional[int] = ..., area_name: _Optional[str] = ..., geo_name: _Optional[str] = ..., overtime: _Optional[int] = ..., shortage: _Optional[int] = ..., work_time: _Optional[int] = ..., price_per_hour: _Optional[int] = ..., overtime_price: _Optional[int] = ..., shortage_price: _Optional[int] = ..., work_time_price: _Optional[int] = ..., shift_starts_at: _Optional[str] = ..., shift_ends_at: _Optional[str] = ..., subtotal: _Optional[int] = ..., mileage_inside: _Optional[int] = ..., mileage_outside: _Optional[int] = ..., events: _Optional[_Iterable[_Union[AttendanceResponse.Event, _Mapping]]] = ...) -> None: ...
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    reports: _containers.RepeatedCompositeFieldContainer[AttendanceResponse.Attendance]
    def __init__(self, reports: _Optional[_Iterable[_Union[AttendanceResponse.Attendance, _Mapping]]] = ...) -> None: ...

class TripsRequest(_message.Message):
    __slots__ = ("started_at", "finished_at", "device_ids")
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., device_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class TripsResponse(_message.Message):
    __slots__ = ("Reports",)
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    Reports: _containers.RepeatedCompositeFieldContainer[_trip_pb2.FusionTrip]
    def __init__(self, Reports: _Optional[_Iterable[_Union[_trip_pb2.FusionTrip, _Mapping]]] = ...) -> None: ...

class TripsSummaryRequest(_message.Message):
    __slots__ = ("started_at", "finished_at", "device_ids", "group_by")
    class GroupBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        All: _ClassVar[TripsSummaryRequest.GroupBy]
        Day: _ClassVar[TripsSummaryRequest.GroupBy]
        Month: _ClassVar[TripsSummaryRequest.GroupBy]
    All: TripsSummaryRequest.GroupBy
    Day: TripsSummaryRequest.GroupBy
    Month: TripsSummaryRequest.GroupBy
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_IDS_FIELD_NUMBER: _ClassVar[int]
    GROUP_BY_FIELD_NUMBER: _ClassVar[int]
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    device_ids: _containers.RepeatedScalarFieldContainer[int]
    group_by: TripsSummaryRequest.GroupBy
    def __init__(self, started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., device_ids: _Optional[_Iterable[int]] = ..., group_by: _Optional[_Union[TripsSummaryRequest.GroupBy, str]] = ...) -> None: ...

class TripsSummaryResponse(_message.Message):
    __slots__ = ("Reports", "records", "cost", "started_at", "finished_at")
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    Reports: _containers.RepeatedCompositeFieldContainer[_trip_pb2.FusionTrip]
    records: int
    cost: int
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    def __init__(self, Reports: _Optional[_Iterable[_Union[_trip_pb2.FusionTrip, _Mapping]]] = ..., records: _Optional[int] = ..., cost: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
