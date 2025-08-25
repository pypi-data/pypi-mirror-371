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

class Via(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NONE: _ClassVar[Via]
    SMS: _ClassVar[Via]
    FCM: _ClassVar[Via]
    EMAIL: _ClassVar[Via]
    DATABASE: _ClassVar[Via]
    CALL: _ClassVar[Via]

class ObjectType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[ObjectType]
    DEVICE: _ClassVar[ObjectType]
    USER: _ClassVar[ObjectType]
    OPERATION: _ClassVar[ObjectType]
NONE: Via
SMS: Via
FCM: Via
EMAIL: Via
DATABASE: Via
CALL: Via
UNKNOWN: ObjectType
DEVICE: ObjectType
USER: ObjectType
OPERATION: ObjectType

class NotifyJob(_message.Message):
    __slots__ = ("id", "user_id", "alert_id", "user_alert_id", "alert", "retries", "priority", "notify", "via")
    class Priority(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOW: _ClassVar[NotifyJob.Priority]
        MEDIUM: _ClassVar[NotifyJob.Priority]
        HIGH: _ClassVar[NotifyJob.Priority]
    LOW: NotifyJob.Priority
    MEDIUM: NotifyJob.Priority
    HIGH: NotifyJob.Priority
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ALERT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ALERT_ID_FIELD_NUMBER: _ClassVar[int]
    ALERT_FIELD_NUMBER: _ClassVar[int]
    RETRIES_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_FIELD_NUMBER: _ClassVar[int]
    VIA_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_id: int
    alert_id: int
    user_alert_id: int
    alert: _dataModel_pb2.Alert
    retries: int
    priority: NotifyJob.Priority
    notify: Notify
    via: _containers.RepeatedScalarFieldContainer[Via]
    def __init__(self, id: _Optional[int] = ..., user_id: _Optional[int] = ..., alert_id: _Optional[int] = ..., user_alert_id: _Optional[int] = ..., alert: _Optional[_Union[_dataModel_pb2.Alert, str]] = ..., retries: _Optional[int] = ..., priority: _Optional[_Union[NotifyJob.Priority, str]] = ..., notify: _Optional[_Union[Notify, _Mapping]] = ..., via: _Optional[_Iterable[_Union[Via, str]]] = ...) -> None: ...

class UserDeviceAlert(_message.Message):
    __slots__ = ("id", "user_id", "device_id", "organization_id", "alert_id", "condition", "timing", "status", "format", "alert", "unit", "object_type", "object_id")
    class Condition(_message.Message):
        __slots__ = ("from_time", "to_time", "sound_id", "text", "value", "type")
        FROM_TIME_FIELD_NUMBER: _ClassVar[int]
        TO_TIME_FIELD_NUMBER: _ClassVar[int]
        SOUND_ID_FIELD_NUMBER: _ClassVar[int]
        TEXT_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        from_time: str
        to_time: str
        sound_id: int
        text: str
        value: int
        type: _containers.RepeatedScalarFieldContainer[Via]
        def __init__(self, from_time: _Optional[str] = ..., to_time: _Optional[str] = ..., sound_id: _Optional[int] = ..., text: _Optional[str] = ..., value: _Optional[int] = ..., type: _Optional[_Iterable[_Union[Via, str]]] = ...) -> None: ...
    class ConditionList(_message.Message):
        __slots__ = ("condition",)
        CONDITION_FIELD_NUMBER: _ClassVar[int]
        condition: _containers.RepeatedCompositeFieldContainer[UserDeviceAlert.Condition]
        def __init__(self, condition: _Optional[_Iterable[_Union[UserDeviceAlert.Condition, _Mapping]]] = ...) -> None: ...
    class ConditionEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: UserDeviceAlert.ConditionList
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[UserDeviceAlert.ConditionList, _Mapping]] = ...) -> None: ...
    class TimingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: UserDeviceAlert.ConditionList
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[UserDeviceAlert.ConditionList, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    ALERT_ID_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    TIMING_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    ALERT_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_id: int
    device_id: int
    organization_id: int
    alert_id: int
    condition: _containers.MessageMap[int, UserDeviceAlert.ConditionList]
    timing: _containers.MessageMap[int, UserDeviceAlert.ConditionList]
    status: bool
    format: str
    alert: _dataModel_pb2.Alert
    unit: str
    object_type: str
    object_id: int
    def __init__(self, id: _Optional[int] = ..., user_id: _Optional[int] = ..., device_id: _Optional[int] = ..., organization_id: _Optional[int] = ..., alert_id: _Optional[int] = ..., condition: _Optional[_Mapping[int, UserDeviceAlert.ConditionList]] = ..., timing: _Optional[_Mapping[int, UserDeviceAlert.ConditionList]] = ..., status: bool = ..., format: _Optional[str] = ..., alert: _Optional[_Union[_dataModel_pb2.Alert, str]] = ..., unit: _Optional[str] = ..., object_type: _Optional[str] = ..., object_id: _Optional[int] = ...) -> None: ...

class UserDeviceAlertList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[UserDeviceAlert]
    def __init__(self, list: _Optional[_Iterable[_Union[UserDeviceAlert, _Mapping]]] = ...) -> None: ...

class Receiver(_message.Message):
    __slots__ = ("phone", "email", "token")
    PHONE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    phone: int
    email: str
    token: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, phone: _Optional[int] = ..., email: _Optional[str] = ..., token: _Optional[_Iterable[str]] = ...) -> None: ...

class Notify(_message.Message):
    __slots__ = ("title", "body", "sound", "image", "icon", "receiver", "object_id", "object_type", "timestamp", "data")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    SOUND_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    title: str
    body: str
    sound: int
    image: str
    icon: str
    receiver: Receiver
    object_id: int
    object_type: ObjectType
    timestamp: _timestamp_pb2.Timestamp
    data: _containers.ScalarMap[str, str]
    def __init__(self, title: _Optional[str] = ..., body: _Optional[str] = ..., sound: _Optional[int] = ..., image: _Optional[str] = ..., icon: _Optional[str] = ..., receiver: _Optional[_Union[Receiver, _Mapping]] = ..., object_id: _Optional[int] = ..., object_type: _Optional[_Union[ObjectType, str]] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Notification(_message.Message):
    __slots__ = ("uuid", "user_id", "object_id", "object_type", "title", "body", "alert_id", "alert", "via", "data", "image", "sound", "created_at", "read_at")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    UUID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    ALERT_ID_FIELD_NUMBER: _ClassVar[int]
    ALERT_FIELD_NUMBER: _ClassVar[int]
    VIA_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    SOUND_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    READ_AT_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    user_id: int
    object_id: int
    object_type: ObjectType
    title: str
    body: str
    alert_id: int
    alert: _dataModel_pb2.Alert
    via: _containers.RepeatedScalarFieldContainer[Via]
    data: _containers.ScalarMap[str, str]
    image: str
    sound: int
    created_at: _timestamp_pb2.Timestamp
    read_at: _timestamp_pb2.Timestamp
    def __init__(self, uuid: _Optional[str] = ..., user_id: _Optional[int] = ..., object_id: _Optional[int] = ..., object_type: _Optional[_Union[ObjectType, str]] = ..., title: _Optional[str] = ..., body: _Optional[str] = ..., alert_id: _Optional[int] = ..., alert: _Optional[_Union[_dataModel_pb2.Alert, str]] = ..., via: _Optional[_Iterable[_Union[Via, str]]] = ..., data: _Optional[_Mapping[str, str]] = ..., image: _Optional[str] = ..., sound: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., read_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AlertModel(_message.Message):
    __slots__ = ("id", "organization_id", "alert_id", "alert_type", "unit", "value", "message", "name", "min_value", "max_value", "picture", "created_by", "updated_by", "created_at", "updated_at", "object_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    ALERT_ID_FIELD_NUMBER: _ClassVar[int]
    ALERT_TYPE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    alert_id: int
    alert_type: int
    unit: str
    value: int
    message: str
    name: str
    min_value: str
    max_value: str
    picture: str
    created_by: int
    updated_by: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    object_type: str
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., alert_id: _Optional[int] = ..., alert_type: _Optional[int] = ..., unit: _Optional[str] = ..., value: _Optional[int] = ..., message: _Optional[str] = ..., name: _Optional[str] = ..., min_value: _Optional[str] = ..., max_value: _Optional[str] = ..., picture: _Optional[str] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., object_type: _Optional[str] = ...) -> None: ...
