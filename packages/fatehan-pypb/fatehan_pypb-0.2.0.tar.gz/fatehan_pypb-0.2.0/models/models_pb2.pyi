import datetime

from packets import dataModel_pb2 as _dataModel_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Gallery(_message.Message):
    __slots__ = ("id", "device_id", "identification_no", "type", "storage", "path", "mime", "codec", "size", "location", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    IDENTIFICATION_NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STORAGE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    MIME_FIELD_NUMBER: _ClassVar[int]
    CODEC_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    device_id: int
    identification_no: bytes
    type: _dataModel_pb2.FileType
    storage: str
    path: str
    mime: str
    codec: str
    size: int
    location: _dataModel_pb2.Data
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., device_id: _Optional[int] = ..., identification_no: _Optional[bytes] = ..., type: _Optional[_Union[_dataModel_pb2.FileType, str]] = ..., storage: _Optional[str] = ..., path: _Optional[str] = ..., mime: _Optional[str] = ..., codec: _Optional[str] = ..., size: _Optional[int] = ..., location: _Optional[_Union[_dataModel_pb2.Data, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class IoList(_message.Message):
    __slots__ = ("items",)
    class ItemsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: bytes
        def __init__(self, key: _Optional[int] = ..., value: _Optional[bytes] = ...) -> None: ...
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.ScalarMap[int, bytes]
    def __init__(self, items: _Optional[_Mapping[int, bytes]] = ...) -> None: ...

class HeartbeatCache(_message.Message):
    __slots__ = ("ignition", "gsm", "battery_percent", "external_voltage", "command_id", "command", "mileage", "terminal_id", "temperature", "ai1", "odyssey_command_id", "schedule_alert")
    IGNITION_FIELD_NUMBER: _ClassVar[int]
    GSM_FIELD_NUMBER: _ClassVar[int]
    BATTERY_PERCENT_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    TERMINAL_ID_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    AI1_FIELD_NUMBER: _ClassVar[int]
    ODYSSEY_COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_ALERT_FIELD_NUMBER: _ClassVar[int]
    ignition: bool
    gsm: int
    battery_percent: int
    external_voltage: int
    command_id: int
    command: str
    mileage: int
    terminal_id: int
    temperature: float
    ai1: int
    odyssey_command_id: int
    schedule_alert: _dataModel_pb2.Alert
    def __init__(self, ignition: bool = ..., gsm: _Optional[int] = ..., battery_percent: _Optional[int] = ..., external_voltage: _Optional[int] = ..., command_id: _Optional[int] = ..., command: _Optional[str] = ..., mileage: _Optional[int] = ..., terminal_id: _Optional[int] = ..., temperature: _Optional[float] = ..., ai1: _Optional[int] = ..., odyssey_command_id: _Optional[int] = ..., schedule_alert: _Optional[_Union[_dataModel_pb2.Alert, str]] = ...) -> None: ...

class SinotrackCache(_message.Message):
    __slots__ = ("gps_time", "fuel_used_gps", "ignition", "command_id", "command")
    GPS_TIME_FIELD_NUMBER: _ClassVar[int]
    FUEL_USED_GPS_FIELD_NUMBER: _ClassVar[int]
    IGNITION_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    gps_time: int
    fuel_used_gps: int
    ignition: bool
    command_id: int
    command: str
    def __init__(self, gps_time: _Optional[int] = ..., fuel_used_gps: _Optional[int] = ..., ignition: bool = ..., command_id: _Optional[int] = ..., command: _Optional[str] = ...) -> None: ...

class PersonalAccessToken(_message.Message):
    __slots__ = ("id", "tokenable_type", "tokenable_id", "name", "token", "abilities", "fcm", "ip", "domain", "partner_id", "user_agent", "device_type", "last_used_at", "expires_at", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TOKENABLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TOKENABLE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    ABILITIES_FIELD_NUMBER: _ClassVar[int]
    FCM_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    PARTNER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_USED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    tokenable_type: str
    tokenable_id: int
    name: str
    token: str
    abilities: str
    fcm: str
    ip: str
    domain: str
    partner_id: int
    user_agent: str
    device_type: str
    last_used_at: _timestamp_pb2.Timestamp
    expires_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., tokenable_type: _Optional[str] = ..., tokenable_id: _Optional[int] = ..., name: _Optional[str] = ..., token: _Optional[str] = ..., abilities: _Optional[str] = ..., fcm: _Optional[str] = ..., ip: _Optional[str] = ..., domain: _Optional[str] = ..., partner_id: _Optional[int] = ..., user_agent: _Optional[str] = ..., device_type: _Optional[str] = ..., last_used_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DeviceStatusList(_message.Message):
    __slots__ = ("cost", "accepted", "list")
    COST_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    cost: int
    accepted: int
    list: _containers.RepeatedCompositeFieldContainer[_dataModel_pb2.DeviceStatus]
    def __init__(self, cost: _Optional[int] = ..., accepted: _Optional[int] = ..., list: _Optional[_Iterable[_Union[_dataModel_pb2.DeviceStatus, _Mapping]]] = ...) -> None: ...

class ChargeLog(_message.Message):
    __slots__ = ("id", "user_id", "device_id", "imei", "object_id", "object_type", "type", "description", "ip", "user_agent", "previous_expiration", "next_expiration", "is_unlimited", "refund", "created_at", "updated_at")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        None: _ClassVar[ChargeLog.Type]
        Wallet: _ClassVar[ChargeLog.Type]
        Store: _ClassVar[ChargeLog.Type]
        Payment: _ClassVar[ChargeLog.Type]
        FirstConnect: _ClassVar[ChargeLog.Type]
        Trial: _ClassVar[ChargeLog.Type]
        Refund: _ClassVar[ChargeLog.Type]
    None: ChargeLog.Type
    Wallet: ChargeLog.Type
    Store: ChargeLog.Type
    Payment: ChargeLog.Type
    FirstConnect: ChargeLog.Type
    Trial: ChargeLog.Type
    Refund: ChargeLog.Type
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    IMEI_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    NEXT_EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    IS_UNLIMITED_FIELD_NUMBER: _ClassVar[int]
    REFUND_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_id: int
    device_id: int
    imei: int
    object_id: int
    object_type: str
    type: ChargeLog.Type
    description: str
    ip: str
    user_agent: str
    previous_expiration: _timestamp_pb2.Timestamp
    next_expiration: _timestamp_pb2.Timestamp
    is_unlimited: bool
    refund: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., user_id: _Optional[int] = ..., device_id: _Optional[int] = ..., imei: _Optional[int] = ..., object_id: _Optional[int] = ..., object_type: _Optional[str] = ..., type: _Optional[_Union[ChargeLog.Type, str]] = ..., description: _Optional[str] = ..., ip: _Optional[str] = ..., user_agent: _Optional[str] = ..., previous_expiration: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., next_expiration: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., is_unlimited: bool = ..., refund: bool = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TrialLog(_message.Message):
    __slots__ = ("id", "imei", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    IMEI_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    imei: int
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., imei: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class LiveLocation(_message.Message):
    __slots__ = ("id", "organization_id", "created_by", "updated_by", "uuid", "expires_at", "password", "created_at", "updated_at", "objects")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    created_by: int
    updated_by: int
    uuid: str
    expires_at: _timestamp_pb2.Timestamp
    password: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    objects: _containers.RepeatedCompositeFieldContainer[LiveLocationRelated]
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., uuid: _Optional[str] = ..., expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., password: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., objects: _Optional[_Iterable[_Union[LiveLocationRelated, _Mapping]]] = ...) -> None: ...

class LiveLocationRelated(_message.Message):
    __slots__ = ("id", "live_location_id", "object_id", "object_type", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    LIVE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    live_location_id: int
    object_id: int
    object_type: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., live_location_id: _Optional[int] = ..., object_id: _Optional[int] = ..., object_type: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("id", "organization_id", "created_by", "updated_by", "key", "value", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    created_by: int
    updated_by: int
    key: str
    value: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., key: _Optional[str] = ..., value: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
