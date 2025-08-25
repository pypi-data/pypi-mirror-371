import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Device(_message.Message):
    __slots__ = ("id", "organization_id", "partner_id", "generation", "device_id", "object_id", "object_type", "tracker_id", "owner_id", "icon_id", "warehouse_id", "created_by", "sim_card", "sim_provider", "id_changed", "icc_id", "sms_username", "sms_password", "config_password", "test", "sim_card_id", "timezone", "is_unlimited", "trip_type", "receive_at", "expires_at", "connect_at", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    PARTNER_ID_FIELD_NUMBER: _ClassVar[int]
    GENERATION_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRACKER_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    ICON_ID_FIELD_NUMBER: _ClassVar[int]
    WAREHOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    SIM_CARD_FIELD_NUMBER: _ClassVar[int]
    SIM_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    ID_CHANGED_FIELD_NUMBER: _ClassVar[int]
    ICC_ID_FIELD_NUMBER: _ClassVar[int]
    SMS_USERNAME_FIELD_NUMBER: _ClassVar[int]
    SMS_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    CONFIG_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    TEST_FIELD_NUMBER: _ClassVar[int]
    SIM_CARD_ID_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    IS_UNLIMITED_FIELD_NUMBER: _ClassVar[int]
    TRIP_TYPE_FIELD_NUMBER: _ClassVar[int]
    RECEIVE_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    CONNECT_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    partner_id: int
    generation: str
    device_id: str
    object_id: int
    object_type: str
    tracker_id: int
    owner_id: int
    icon_id: int
    warehouse_id: int
    created_by: int
    sim_card: str
    sim_provider: int
    id_changed: bool
    icc_id: str
    sms_username: str
    sms_password: str
    config_password: str
    test: bool
    sim_card_id: str
    timezone: str
    is_unlimited: bool
    trip_type: str
    receive_at: _timestamp_pb2.Timestamp
    expires_at: _timestamp_pb2.Timestamp
    connect_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., partner_id: _Optional[int] = ..., generation: _Optional[str] = ..., device_id: _Optional[str] = ..., object_id: _Optional[int] = ..., object_type: _Optional[str] = ..., tracker_id: _Optional[int] = ..., owner_id: _Optional[int] = ..., icon_id: _Optional[int] = ..., warehouse_id: _Optional[int] = ..., created_by: _Optional[int] = ..., sim_card: _Optional[str] = ..., sim_provider: _Optional[int] = ..., id_changed: bool = ..., icc_id: _Optional[str] = ..., sms_username: _Optional[str] = ..., sms_password: _Optional[str] = ..., config_password: _Optional[str] = ..., test: bool = ..., sim_card_id: _Optional[str] = ..., timezone: _Optional[str] = ..., is_unlimited: bool = ..., trip_type: _Optional[str] = ..., receive_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., connect_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DeviceIcon(_message.Message):
    __slots__ = ("id", "organization_id", "created_by", "updated_by", "icon_type", "image_type", "name", "images", "is_default", "created_at", "updated_at")
    class Image(_message.Message):
        __slots__ = ("img_celo", "img_move", "img_stop", "img_towing", "img_timeout")
        IMG_CELO_FIELD_NUMBER: _ClassVar[int]
        IMG_MOVE_FIELD_NUMBER: _ClassVar[int]
        IMG_STOP_FIELD_NUMBER: _ClassVar[int]
        IMG_TOWING_FIELD_NUMBER: _ClassVar[int]
        IMG_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
        img_celo: str
        img_move: str
        img_stop: str
        img_towing: str
        img_timeout: str
        def __init__(self, img_celo: _Optional[str] = ..., img_move: _Optional[str] = ..., img_stop: _Optional[str] = ..., img_towing: _Optional[str] = ..., img_timeout: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    ICON_TYPE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    IS_DEFAULT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    created_by: int
    updated_by: int
    icon_type: int
    image_type: int
    name: str
    images: DeviceIcon.Image
    is_default: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., icon_type: _Optional[int] = ..., image_type: _Optional[int] = ..., name: _Optional[str] = ..., images: _Optional[_Union[DeviceIcon.Image, _Mapping]] = ..., is_default: bool = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Tracker(_message.Message):
    __slots__ = ("id", "name", "picture", "metadata", "generation", "level", "parent_id", "created_by", "created_at", "updated_at", "documents")
    class Metadata(_message.Message):
        __slots__ = ("port", "tags", "type", "id_type", "id_start", "odo_type", "call_type", "id_length", "analog_input", "sms_password", "sms_username", "digital_input", "digital_output", "movement_sensor", "sms_credentials", "device_config_commands")
        class SmsCredentials(_message.Message):
            __slots__ = ("password", "username")
            PASSWORD_FIELD_NUMBER: _ClassVar[int]
            USERNAME_FIELD_NUMBER: _ClassVar[int]
            password: str
            username: str
            def __init__(self, password: _Optional[str] = ..., username: _Optional[str] = ...) -> None: ...
        PORT_FIELD_NUMBER: _ClassVar[int]
        TAGS_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        ID_TYPE_FIELD_NUMBER: _ClassVar[int]
        ID_START_FIELD_NUMBER: _ClassVar[int]
        ODO_TYPE_FIELD_NUMBER: _ClassVar[int]
        CALL_TYPE_FIELD_NUMBER: _ClassVar[int]
        ID_LENGTH_FIELD_NUMBER: _ClassVar[int]
        ANALOG_INPUT_FIELD_NUMBER: _ClassVar[int]
        SMS_PASSWORD_FIELD_NUMBER: _ClassVar[int]
        SMS_USERNAME_FIELD_NUMBER: _ClassVar[int]
        DIGITAL_INPUT_FIELD_NUMBER: _ClassVar[int]
        DIGITAL_OUTPUT_FIELD_NUMBER: _ClassVar[int]
        MOVEMENT_SENSOR_FIELD_NUMBER: _ClassVar[int]
        SMS_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
        DEVICE_CONFIG_COMMANDS_FIELD_NUMBER: _ClassVar[int]
        port: int
        tags: str
        type: int
        id_type: int
        id_start: str
        odo_type: int
        call_type: int
        id_length: int
        analog_input: int
        sms_password: str
        sms_username: str
        digital_input: int
        digital_output: int
        movement_sensor: bool
        sms_credentials: Tracker.Metadata.SmsCredentials
        device_config_commands: str
        def __init__(self, port: _Optional[int] = ..., tags: _Optional[str] = ..., type: _Optional[int] = ..., id_type: _Optional[int] = ..., id_start: _Optional[str] = ..., odo_type: _Optional[int] = ..., call_type: _Optional[int] = ..., id_length: _Optional[int] = ..., analog_input: _Optional[int] = ..., sms_password: _Optional[str] = ..., sms_username: _Optional[str] = ..., digital_input: _Optional[int] = ..., digital_output: _Optional[int] = ..., movement_sensor: bool = ..., sms_credentials: _Optional[_Union[Tracker.Metadata.SmsCredentials, _Mapping]] = ..., device_config_commands: _Optional[str] = ...) -> None: ...
    class Document(_message.Message):
        __slots__ = ("object_id", "created_by", "organization_id", "url", "visibility", "object_type")
        OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
        CREATED_BY_FIELD_NUMBER: _ClassVar[int]
        ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
        URL_FIELD_NUMBER: _ClassVar[int]
        VISIBILITY_FIELD_NUMBER: _ClassVar[int]
        OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
        object_id: int
        created_by: int
        organization_id: int
        url: str
        visibility: str
        object_type: str
        def __init__(self, object_id: _Optional[int] = ..., created_by: _Optional[int] = ..., organization_id: _Optional[int] = ..., url: _Optional[str] = ..., visibility: _Optional[str] = ..., object_type: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    GENERATION_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    picture: str
    metadata: Tracker.Metadata
    generation: str
    level: int
    parent_id: int
    created_by: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    documents: _containers.RepeatedCompositeFieldContainer[Tracker.Document]
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., picture: _Optional[str] = ..., metadata: _Optional[_Union[Tracker.Metadata, _Mapping]] = ..., generation: _Optional[str] = ..., level: _Optional[int] = ..., parent_id: _Optional[int] = ..., created_by: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., documents: _Optional[_Iterable[_Union[Tracker.Document, _Mapping]]] = ...) -> None: ...

class CarModel(_message.Message):
    __slots__ = ("id", "car_brand_id", "name", "picture", "description", "sord", "is_active", "created_by", "updated_by", "metadata", "created_at", "updated_at")
    class Metadata(_message.Message):
        __slots__ = ("key", "name", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        name: str
        value: str
        def __init__(self, key: _Optional[str] = ..., name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    CAR_BRAND_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SORD_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    car_brand_id: int
    name: str
    picture: str
    description: str
    sord: int
    is_active: bool
    created_by: int
    updated_by: int
    metadata: _containers.RepeatedCompositeFieldContainer[CarModel.Metadata]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., car_brand_id: _Optional[int] = ..., name: _Optional[str] = ..., picture: _Optional[str] = ..., description: _Optional[str] = ..., sord: _Optional[int] = ..., is_active: bool = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., metadata: _Optional[_Iterable[_Union[CarModel.Metadata, _Mapping]]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CarBrand(_message.Message):
    __slots__ = ("id", "car_category_id", "name", "description", "picture", "sord", "is_active", "created_by", "updated_by", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    CAR_CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    SORD_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    car_category_id: int
    name: str
    description: str
    picture: str
    sord: int
    is_active: bool
    created_by: int
    updated_by: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., car_category_id: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., picture: _Optional[str] = ..., sord: _Optional[int] = ..., is_active: bool = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Car(_message.Message):
    __slots__ = ("id", "organization_id", "created_by", "updated_by", "name", "picture", "plate_number", "car_group_id", "car_type", "code", "tonnage", "max_speed", "vin", "engine_number", "chassis_number", "model_year", "fuel_usage", "fuel_usage_per_hour", "fuel_type", "fuel_capacity", "description", "guaranty_expiration_date", "guaranty_expiration_km", "color", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    PLATE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CAR_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    CAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    TONNAGE_FIELD_NUMBER: _ClassVar[int]
    MAX_SPEED_FIELD_NUMBER: _ClassVar[int]
    VIN_FIELD_NUMBER: _ClassVar[int]
    ENGINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CHASSIS_NUMBER_FIELD_NUMBER: _ClassVar[int]
    MODEL_YEAR_FIELD_NUMBER: _ClassVar[int]
    FUEL_USAGE_FIELD_NUMBER: _ClassVar[int]
    FUEL_USAGE_PER_HOUR_FIELD_NUMBER: _ClassVar[int]
    FUEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    FUEL_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    GUARANTY_EXPIRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    GUARANTY_EXPIRATION_KM_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    created_by: int
    updated_by: int
    name: str
    picture: str
    plate_number: str
    car_group_id: int
    car_type: int
    code: str
    tonnage: int
    max_speed: int
    vin: str
    engine_number: str
    chassis_number: str
    model_year: int
    fuel_usage: float
    fuel_usage_per_hour: float
    fuel_type: str
    fuel_capacity: float
    description: str
    guaranty_expiration_date: _timestamp_pb2.Timestamp
    guaranty_expiration_km: int
    color: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., name: _Optional[str] = ..., picture: _Optional[str] = ..., plate_number: _Optional[str] = ..., car_group_id: _Optional[int] = ..., car_type: _Optional[int] = ..., code: _Optional[str] = ..., tonnage: _Optional[int] = ..., max_speed: _Optional[int] = ..., vin: _Optional[str] = ..., engine_number: _Optional[str] = ..., chassis_number: _Optional[str] = ..., model_year: _Optional[int] = ..., fuel_usage: _Optional[float] = ..., fuel_usage_per_hour: _Optional[float] = ..., fuel_type: _Optional[str] = ..., fuel_capacity: _Optional[float] = ..., description: _Optional[str] = ..., guaranty_expiration_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., guaranty_expiration_km: _Optional[int] = ..., color: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class SystemIoStyle(_message.Message):
    __slots__ = ("icon", "name", "color")
    ICON_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    icon: str
    name: str
    color: str
    def __init__(self, icon: _Optional[str] = ..., name: _Optional[str] = ..., color: _Optional[str] = ...) -> None: ...

class SystemIo(_message.Message):
    __slots__ = ("id", "name", "device_id", "formula", "type", "unit", "description", "active_style", "inactive_style", "active", "graphable", "sord", "hidden", "unknown", "created_by", "created_at", "updated_at")
    class SystemIoType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRING: _ClassVar[SystemIo.SystemIoType]
        BOOLEAN: _ClassVar[SystemIo.SystemIoType]
        NUMERIC: _ClassVar[SystemIo.SystemIoType]
        FLOAT: _ClassVar[SystemIo.SystemIoType]
    STRING: SystemIo.SystemIoType
    BOOLEAN: SystemIo.SystemIoType
    NUMERIC: SystemIo.SystemIoType
    FLOAT: SystemIo.SystemIoType
    class UnknownEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    FORMULA_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_STYLE_FIELD_NUMBER: _ClassVar[int]
    INACTIVE_STYLE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    GRAPHABLE_FIELD_NUMBER: _ClassVar[int]
    SORD_FIELD_NUMBER: _ClassVar[int]
    HIDDEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    device_id: int
    formula: str
    type: SystemIo.SystemIoType
    unit: str
    description: str
    active_style: SystemIoStyle
    inactive_style: SystemIoStyle
    active: bool
    graphable: bool
    sord: int
    hidden: _containers.RepeatedScalarFieldContainer[str]
    unknown: _containers.ScalarMap[str, str]
    created_by: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., device_id: _Optional[int] = ..., formula: _Optional[str] = ..., type: _Optional[_Union[SystemIo.SystemIoType, str]] = ..., unit: _Optional[str] = ..., description: _Optional[str] = ..., active_style: _Optional[_Union[SystemIoStyle, _Mapping]] = ..., inactive_style: _Optional[_Union[SystemIoStyle, _Mapping]] = ..., active: bool = ..., graphable: bool = ..., sord: _Optional[int] = ..., hidden: _Optional[_Iterable[str]] = ..., unknown: _Optional[_Mapping[str, str]] = ..., created_by: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ShownIo(_message.Message):
    __slots__ = ("name", "style", "unit", "description", "value", "active", "graphable", "sord")
    NAME_FIELD_NUMBER: _ClassVar[int]
    STYLE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    GRAPHABLE_FIELD_NUMBER: _ClassVar[int]
    SORD_FIELD_NUMBER: _ClassVar[int]
    name: str
    style: SystemIoStyle
    unit: str
    description: str
    value: str
    active: bool
    graphable: bool
    sord: int
    def __init__(self, name: _Optional[str] = ..., style: _Optional[_Union[SystemIoStyle, _Mapping]] = ..., unit: _Optional[str] = ..., description: _Optional[str] = ..., value: _Optional[str] = ..., active: bool = ..., graphable: bool = ..., sord: _Optional[int] = ...) -> None: ...
