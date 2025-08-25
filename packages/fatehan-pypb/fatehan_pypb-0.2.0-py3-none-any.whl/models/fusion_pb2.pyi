import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WorkCycleDevice(_message.Message):
    __slots__ = ("device_id", "movable", "radius", "group_id", "organization_id", "name")
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MOVABLE_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    movable: bool
    radius: int
    group_id: int
    organization_id: int
    name: str
    def __init__(self, device_id: _Optional[int] = ..., movable: bool = ..., radius: _Optional[int] = ..., group_id: _Optional[int] = ..., organization_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class WorkCycleDeviceList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[WorkCycleDevice]
    def __init__(self, list: _Optional[_Iterable[_Union[WorkCycleDevice, _Mapping]]] = ...) -> None: ...

class AlertsListDevice(_message.Message):
    __slots__ = ("alert_list_id", "date_create", "user_id", "imei", "content", "alert_read", "alert_id", "title", "disabled", "latitude", "longitude", "latitude_end", "longitude_end", "date_end", "date_read", "alert_send", "date_send", "vals", "rel_id", "created_at", "updated_at", "identification_no")
    ALERT_LIST_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_CREATE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    IMEI_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ALERT_READ_FIELD_NUMBER: _ClassVar[int]
    ALERT_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_END_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_END_FIELD_NUMBER: _ClassVar[int]
    DATE_END_FIELD_NUMBER: _ClassVar[int]
    DATE_READ_FIELD_NUMBER: _ClassVar[int]
    ALERT_SEND_FIELD_NUMBER: _ClassVar[int]
    DATE_SEND_FIELD_NUMBER: _ClassVar[int]
    VALS_FIELD_NUMBER: _ClassVar[int]
    REL_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    IDENTIFICATION_NO_FIELD_NUMBER: _ClassVar[int]
    alert_list_id: int
    date_create: int
    user_id: int
    imei: int
    content: str
    alert_read: int
    alert_id: int
    title: str
    disabled: int
    latitude: float
    longitude: float
    latitude_end: float
    longitude_end: float
    date_end: int
    date_read: int
    alert_send: int
    date_send: int
    vals: str
    rel_id: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    identification_no: str
    def __init__(self, alert_list_id: _Optional[int] = ..., date_create: _Optional[int] = ..., user_id: _Optional[int] = ..., imei: _Optional[int] = ..., content: _Optional[str] = ..., alert_read: _Optional[int] = ..., alert_id: _Optional[int] = ..., title: _Optional[str] = ..., disabled: _Optional[int] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., latitude_end: _Optional[float] = ..., longitude_end: _Optional[float] = ..., date_end: _Optional[int] = ..., date_read: _Optional[int] = ..., alert_send: _Optional[int] = ..., date_send: _Optional[int] = ..., vals: _Optional[str] = ..., rel_id: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., identification_no: _Optional[str] = ...) -> None: ...

class CommandDevice(_message.Message):
    __slots__ = ("cd_id", "command_id", "imei", "user_id", "date_create", "status", "command", "command_parse", "date_send", "response", "response_parse", "date_response", "time_out", "type", "device_id")
    CD_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    IMEI_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_CREATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    COMMAND_PARSE_FIELD_NUMBER: _ClassVar[int]
    DATE_SEND_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_PARSE_FIELD_NUMBER: _ClassVar[int]
    DATE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    TIME_OUT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    cd_id: int
    command_id: int
    imei: int
    user_id: int
    date_create: int
    status: int
    command: str
    command_parse: str
    date_send: int
    response: str
    response_parse: str
    date_response: int
    time_out: int
    type: int
    device_id: int
    def __init__(self, cd_id: _Optional[int] = ..., command_id: _Optional[int] = ..., imei: _Optional[int] = ..., user_id: _Optional[int] = ..., date_create: _Optional[int] = ..., status: _Optional[int] = ..., command: _Optional[str] = ..., command_parse: _Optional[str] = ..., date_send: _Optional[int] = ..., response: _Optional[str] = ..., response_parse: _Optional[str] = ..., date_response: _Optional[int] = ..., time_out: _Optional[int] = ..., type: _Optional[int] = ..., device_id: _Optional[int] = ...) -> None: ...

class FusionCar(_message.Message):
    __slots__ = ("car_id", "device_name", "power_voltage")
    CAR_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    POWER_VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    car_id: int
    device_name: str
    power_voltage: int
    def __init__(self, car_id: _Optional[int] = ..., device_name: _Optional[str] = ..., power_voltage: _Optional[int] = ...) -> None: ...

class FusionNotify(_message.Message):
    __slots__ = ("user_id", "title", "body", "data", "image", "sound", "token")
    class Body(_message.Message):
        __slots__ = ("type", "alert_param", "alert_type", "alert_read", "icon", "unit", "vals", "alert_list_id", "lat", "lng", "gps_time", "imei", "device_name", "rel_id", "title")
        TYPE_FIELD_NUMBER: _ClassVar[int]
        ALERT_PARAM_FIELD_NUMBER: _ClassVar[int]
        ALERT_TYPE_FIELD_NUMBER: _ClassVar[int]
        ALERT_READ_FIELD_NUMBER: _ClassVar[int]
        ICON_FIELD_NUMBER: _ClassVar[int]
        UNIT_FIELD_NUMBER: _ClassVar[int]
        VALS_FIELD_NUMBER: _ClassVar[int]
        ALERT_LIST_ID_FIELD_NUMBER: _ClassVar[int]
        LAT_FIELD_NUMBER: _ClassVar[int]
        LNG_FIELD_NUMBER: _ClassVar[int]
        GPS_TIME_FIELD_NUMBER: _ClassVar[int]
        IMEI_FIELD_NUMBER: _ClassVar[int]
        DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
        REL_ID_FIELD_NUMBER: _ClassVar[int]
        TITLE_FIELD_NUMBER: _ClassVar[int]
        type: str
        alert_param: str
        alert_type: int
        alert_read: str
        icon: str
        unit: str
        vals: str
        alert_list_id: int
        lat: float
        lng: float
        gps_time: int
        imei: int
        device_name: str
        rel_id: int
        title: str
        def __init__(self, type: _Optional[str] = ..., alert_param: _Optional[str] = ..., alert_type: _Optional[int] = ..., alert_read: _Optional[str] = ..., icon: _Optional[str] = ..., unit: _Optional[str] = ..., vals: _Optional[str] = ..., alert_list_id: _Optional[int] = ..., lat: _Optional[float] = ..., lng: _Optional[float] = ..., gps_time: _Optional[int] = ..., imei: _Optional[int] = ..., device_name: _Optional[str] = ..., rel_id: _Optional[int] = ..., title: _Optional[str] = ...) -> None: ...
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    SOUND_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    title: str
    body: str
    data: FusionNotify.Body
    image: str
    sound: int
    token: str
    def __init__(self, user_id: _Optional[int] = ..., title: _Optional[str] = ..., body: _Optional[str] = ..., data: _Optional[_Union[FusionNotify.Body, _Mapping]] = ..., image: _Optional[str] = ..., sound: _Optional[int] = ..., token: _Optional[str] = ...) -> None: ...

class FusionMaintenance(_message.Message):
    __slots__ = ("mc_id", "car_id", "maintenance_id", "project_id", "user_id", "date_set", "price", "expireable", "expire_date", "expire_engin_time", "expire_odo", "expired", "car_engin_time", "car_odo", "date_create", "renewable", "date_renew", "renew_id", "sent", "date_expired", "parts", "service_provider_id", "lat", "lng", "photo", "user_creator_id", "expire_date_warranty", "description", "date_end", "current_mileage", "current_engine_time", "expired_reason", "created_at", "updated_at")
    MC_ID_FIELD_NUMBER: _ClassVar[int]
    CAR_ID_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_SET_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    EXPIREABLE_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_DATE_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_ENGIN_TIME_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_ODO_FIELD_NUMBER: _ClassVar[int]
    EXPIRED_FIELD_NUMBER: _ClassVar[int]
    CAR_ENGIN_TIME_FIELD_NUMBER: _ClassVar[int]
    CAR_ODO_FIELD_NUMBER: _ClassVar[int]
    DATE_CREATE_FIELD_NUMBER: _ClassVar[int]
    RENEWABLE_FIELD_NUMBER: _ClassVar[int]
    DATE_RENEW_FIELD_NUMBER: _ClassVar[int]
    RENEW_ID_FIELD_NUMBER: _ClassVar[int]
    SENT_FIELD_NUMBER: _ClassVar[int]
    DATE_EXPIRED_FIELD_NUMBER: _ClassVar[int]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    LAT_FIELD_NUMBER: _ClassVar[int]
    LNG_FIELD_NUMBER: _ClassVar[int]
    PHOTO_FIELD_NUMBER: _ClassVar[int]
    USER_CREATOR_ID_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_DATE_WARRANTY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DATE_END_FIELD_NUMBER: _ClassVar[int]
    CURRENT_MILEAGE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ENGINE_TIME_FIELD_NUMBER: _ClassVar[int]
    EXPIRED_REASON_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    mc_id: int
    car_id: int
    maintenance_id: int
    project_id: int
    user_id: int
    date_set: int
    price: int
    expireable: bool
    expire_date: int
    expire_engin_time: int
    expire_odo: int
    expired: int
    car_engin_time: int
    car_odo: int
    date_create: int
    renewable: int
    date_renew: int
    renew_id: int
    sent: int
    date_expired: int
    parts: str
    service_provider_id: int
    lat: float
    lng: float
    photo: str
    user_creator_id: int
    expire_date_warranty: int
    description: str
    date_end: int
    current_mileage: int
    current_engine_time: int
    expired_reason: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, mc_id: _Optional[int] = ..., car_id: _Optional[int] = ..., maintenance_id: _Optional[int] = ..., project_id: _Optional[int] = ..., user_id: _Optional[int] = ..., date_set: _Optional[int] = ..., price: _Optional[int] = ..., expireable: bool = ..., expire_date: _Optional[int] = ..., expire_engin_time: _Optional[int] = ..., expire_odo: _Optional[int] = ..., expired: _Optional[int] = ..., car_engin_time: _Optional[int] = ..., car_odo: _Optional[int] = ..., date_create: _Optional[int] = ..., renewable: _Optional[int] = ..., date_renew: _Optional[int] = ..., renew_id: _Optional[int] = ..., sent: _Optional[int] = ..., date_expired: _Optional[int] = ..., parts: _Optional[str] = ..., service_provider_id: _Optional[int] = ..., lat: _Optional[float] = ..., lng: _Optional[float] = ..., photo: _Optional[str] = ..., user_creator_id: _Optional[int] = ..., expire_date_warranty: _Optional[int] = ..., description: _Optional[str] = ..., date_end: _Optional[int] = ..., current_mileage: _Optional[int] = ..., current_engine_time: _Optional[int] = ..., expired_reason: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
