import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CrashEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CrashNone: _ClassVar[CrashEnum]
    RealCrash: _ClassVar[CrashEnum]
    LimitedCrashTrace: _ClassVar[CrashEnum]
    LimitedCrashTraceNotCalibrated: _ClassVar[CrashEnum]
    FullCrashTraceNotCalibrated: _ClassVar[CrashEnum]
    FullCrashTrace: _ClassVar[CrashEnum]
    RealCrashNotCalibrated: _ClassVar[CrashEnum]

class GreenDrivingTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    none: _ClassVar[GreenDrivingTypeEnum]
    harshAcceleration: _ClassVar[GreenDrivingTypeEnum]
    harshBraking: _ClassVar[GreenDrivingTypeEnum]
    harshCornering: _ClassVar[GreenDrivingTypeEnum]
    bloodAlcoholContent: _ClassVar[GreenDrivingTypeEnum]
    overSpeeding: _ClassVar[GreenDrivingTypeEnum]

class HumidityEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DefaultHumidityMin: _ClassVar[HumidityEnum]
    DefaultHumidityMax: _ClassVar[HumidityEnum]
    DefaultHumidityAvg: _ClassVar[HumidityEnum]
    EyeHumidity1Min: _ClassVar[HumidityEnum]
    EyeHumidity1Max: _ClassVar[HumidityEnum]
    EyeHumidity1Avg: _ClassVar[HumidityEnum]
    EyeHumidity2Min: _ClassVar[HumidityEnum]
    EyeHumidity2Max: _ClassVar[HumidityEnum]
    EyeHumidity2Avg: _ClassVar[HumidityEnum]
    EyeHumidity3Min: _ClassVar[HumidityEnum]
    EyeHumidity3Max: _ClassVar[HumidityEnum]
    EyeHumidity3Avg: _ClassVar[HumidityEnum]
    EyeHumidity4Min: _ClassVar[HumidityEnum]
    EyeHumidity4Max: _ClassVar[HumidityEnum]
    EyeHumidity4Avg: _ClassVar[HumidityEnum]
    BLEHumidity01Min: _ClassVar[HumidityEnum]
    BLEHumidity01Max: _ClassVar[HumidityEnum]
    BLEHumidity01Avg: _ClassVar[HumidityEnum]
    BLEHumidity02Min: _ClassVar[HumidityEnum]
    BLEHumidity02Max: _ClassVar[HumidityEnum]
    BLEHumidity02Avg: _ClassVar[HumidityEnum]
    BLEHumidity03Min: _ClassVar[HumidityEnum]
    BLEHumidity03Max: _ClassVar[HumidityEnum]
    BLEHumidity03Avg: _ClassVar[HumidityEnum]
    BLEHumidity04Min: _ClassVar[HumidityEnum]
    BLEHumidity04Max: _ClassVar[HumidityEnum]
    BLEHumidity04Avg: _ClassVar[HumidityEnum]

class TemperatureEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DefaultTemperatureMin: _ClassVar[TemperatureEnum]
    DefaultTemperatureMax: _ClassVar[TemperatureEnum]
    DefaultTemperatureAvg: _ClassVar[TemperatureEnum]
    IntakeAirTemperatureMin: _ClassVar[TemperatureEnum]
    IntakeAirTemperatureMax: _ClassVar[TemperatureEnum]
    IntakeAirTemperatureAvg: _ClassVar[TemperatureEnum]
    AmbientAirTemperatureMin: _ClassVar[TemperatureEnum]
    AmbientAirTemperatureMax: _ClassVar[TemperatureEnum]
    AmbientAirTemperatureAvg: _ClassVar[TemperatureEnum]
    EngineOilTemperatureMin: _ClassVar[TemperatureEnum]
    EngineOilTemperatureMax: _ClassVar[TemperatureEnum]
    EngineOilTemperatureAvg: _ClassVar[TemperatureEnum]
    CoolantTemperatureMin: _ClassVar[TemperatureEnum]
    CoolantTemperatureMax: _ClassVar[TemperatureEnum]
    CoolantTemperatureAvg: _ClassVar[TemperatureEnum]
    BLETemperature01Min: _ClassVar[TemperatureEnum]
    BLETemperature01Max: _ClassVar[TemperatureEnum]
    BLETemperature01Avg: _ClassVar[TemperatureEnum]
    BLETemperature02Min: _ClassVar[TemperatureEnum]
    BLETemperature02Max: _ClassVar[TemperatureEnum]
    BLETemperature02Avg: _ClassVar[TemperatureEnum]
    BLETemperature03Min: _ClassVar[TemperatureEnum]
    BLETemperature03Max: _ClassVar[TemperatureEnum]
    BLETemperature03Avg: _ClassVar[TemperatureEnum]
    BLETemperature04Min: _ClassVar[TemperatureEnum]
    BLETemperature04Max: _ClassVar[TemperatureEnum]
    BLETemperature04Avg: _ClassVar[TemperatureEnum]
    EngineTemperatureMin: _ClassVar[TemperatureEnum]
    EngineTemperatureMax: _ClassVar[TemperatureEnum]
    EngineTemperatureAvg: _ClassVar[TemperatureEnum]
    BatteryTemperatureMin: _ClassVar[TemperatureEnum]
    BatteryTemperatureMax: _ClassVar[TemperatureEnum]
    BatteryTemperatureAvg: _ClassVar[TemperatureEnum]
    DallasTemperature1Min: _ClassVar[TemperatureEnum]
    DallasTemperature1Max: _ClassVar[TemperatureEnum]
    DallasTemperature1Avg: _ClassVar[TemperatureEnum]
    DallasTemperature2Min: _ClassVar[TemperatureEnum]
    DallasTemperature2Max: _ClassVar[TemperatureEnum]
    DallasTemperature2Avg: _ClassVar[TemperatureEnum]
    DallasTemperature3Min: _ClassVar[TemperatureEnum]
    DallasTemperature3Max: _ClassVar[TemperatureEnum]
    DallasTemperature3Avg: _ClassVar[TemperatureEnum]
    DallasTemperature4Min: _ClassVar[TemperatureEnum]
    DallasTemperature4Max: _ClassVar[TemperatureEnum]
    DallasTemperature4Avg: _ClassVar[TemperatureEnum]
    LLSTemperature01Min: _ClassVar[TemperatureEnum]
    LLSTemperature01Max: _ClassVar[TemperatureEnum]
    LLSTemperature01Avg: _ClassVar[TemperatureEnum]
    LLSTemperature02Min: _ClassVar[TemperatureEnum]
    LLSTemperature02Max: _ClassVar[TemperatureEnum]
    LLSTemperature02Avg: _ClassVar[TemperatureEnum]
    LLSTemperature03Min: _ClassVar[TemperatureEnum]
    LLSTemperature03Max: _ClassVar[TemperatureEnum]
    LLSTemperature03Avg: _ClassVar[TemperatureEnum]
    LLSTemperature04Min: _ClassVar[TemperatureEnum]
    LLSTemperature04Max: _ClassVar[TemperatureEnum]
    LLSTemperature04Avg: _ClassVar[TemperatureEnum]
    EyeTemperature01Min: _ClassVar[TemperatureEnum]
    EyeTemperature01Max: _ClassVar[TemperatureEnum]
    EyeTemperature01Avg: _ClassVar[TemperatureEnum]
    EyeTemperature02Min: _ClassVar[TemperatureEnum]
    EyeTemperature02Max: _ClassVar[TemperatureEnum]
    EyeTemperature02Avg: _ClassVar[TemperatureEnum]
    EyeTemperature03Min: _ClassVar[TemperatureEnum]
    EyeTemperature03Max: _ClassVar[TemperatureEnum]
    EyeTemperature03Avg: _ClassVar[TemperatureEnum]
    EyeTemperature04Min: _ClassVar[TemperatureEnum]
    EyeTemperature04Max: _ClassVar[TemperatureEnum]
    EyeTemperature04Avg: _ClassVar[TemperatureEnum]
    DallasTemperature05Min: _ClassVar[TemperatureEnum]
    DallasTemperature05Max: _ClassVar[TemperatureEnum]
    DallasTemperature05Avg: _ClassVar[TemperatureEnum]
    DallasTemperature06Min: _ClassVar[TemperatureEnum]
    DallasTemperature06Max: _ClassVar[TemperatureEnum]
    DallasTemperature06Avg: _ClassVar[TemperatureEnum]
    Tire01TemperatureMin: _ClassVar[TemperatureEnum]
    Tire01TemperatureMax: _ClassVar[TemperatureEnum]
    Tire01TemperatureAvg: _ClassVar[TemperatureEnum]
    Tire02TemperatureMin: _ClassVar[TemperatureEnum]
    Tire02TemperatureMax: _ClassVar[TemperatureEnum]
    Tire02TemperatureAvg: _ClassVar[TemperatureEnum]
    Tire03TemperatureMin: _ClassVar[TemperatureEnum]
    Tire03TemperatureMax: _ClassVar[TemperatureEnum]
    Tire03TemperatureAvg: _ClassVar[TemperatureEnum]
    Tire04TemperatureMin: _ClassVar[TemperatureEnum]
    Tire04TemperatureMax: _ClassVar[TemperatureEnum]
    Tire04TemperatureAvg: _ClassVar[TemperatureEnum]
    Tire05TemperatureMin: _ClassVar[TemperatureEnum]
    Tire05TemperatureMax: _ClassVar[TemperatureEnum]
    Tire05TemperatureAvg: _ClassVar[TemperatureEnum]
    Tire06TemperatureMin: _ClassVar[TemperatureEnum]
    Tire06TemperatureMax: _ClassVar[TemperatureEnum]
    Tire06TemperatureAvg: _ClassVar[TemperatureEnum]
    Tire07TemperatureMin: _ClassVar[TemperatureEnum]
    Tire07TemperatureMax: _ClassVar[TemperatureEnum]
    Tire07TemperatureAvg: _ClassVar[TemperatureEnum]
    Tire08TemperatureMin: _ClassVar[TemperatureEnum]
    Tire08TemperatureMax: _ClassVar[TemperatureEnum]
    Tire08TemperatureAvg: _ClassVar[TemperatureEnum]
    Tire09TemperatureMin: _ClassVar[TemperatureEnum]
    Tire09TemperatureMax: _ClassVar[TemperatureEnum]
    Tire09TemperatureAvg: _ClassVar[TemperatureEnum]
    Tire10TemperatureMin: _ClassVar[TemperatureEnum]
    Tire10TemperatureMax: _ClassVar[TemperatureEnum]
    Tire10TemperatureAvg: _ClassVar[TemperatureEnum]
    Tire11TemperatureMin: _ClassVar[TemperatureEnum]
    Tire11TemperatureMax: _ClassVar[TemperatureEnum]
    Tire11TemperatureAvg: _ClassVar[TemperatureEnum]
    Tire12TemperatureMin: _ClassVar[TemperatureEnum]
    Tire12TemperatureMax: _ClassVar[TemperatureEnum]
    Tire12TemperatureAvg: _ClassVar[TemperatureEnum]
CrashNone: CrashEnum
RealCrash: CrashEnum
LimitedCrashTrace: CrashEnum
LimitedCrashTraceNotCalibrated: CrashEnum
FullCrashTraceNotCalibrated: CrashEnum
FullCrashTrace: CrashEnum
RealCrashNotCalibrated: CrashEnum
none: GreenDrivingTypeEnum
harshAcceleration: GreenDrivingTypeEnum
harshBraking: GreenDrivingTypeEnum
harshCornering: GreenDrivingTypeEnum
bloodAlcoholContent: GreenDrivingTypeEnum
overSpeeding: GreenDrivingTypeEnum
DefaultHumidityMin: HumidityEnum
DefaultHumidityMax: HumidityEnum
DefaultHumidityAvg: HumidityEnum
EyeHumidity1Min: HumidityEnum
EyeHumidity1Max: HumidityEnum
EyeHumidity1Avg: HumidityEnum
EyeHumidity2Min: HumidityEnum
EyeHumidity2Max: HumidityEnum
EyeHumidity2Avg: HumidityEnum
EyeHumidity3Min: HumidityEnum
EyeHumidity3Max: HumidityEnum
EyeHumidity3Avg: HumidityEnum
EyeHumidity4Min: HumidityEnum
EyeHumidity4Max: HumidityEnum
EyeHumidity4Avg: HumidityEnum
BLEHumidity01Min: HumidityEnum
BLEHumidity01Max: HumidityEnum
BLEHumidity01Avg: HumidityEnum
BLEHumidity02Min: HumidityEnum
BLEHumidity02Max: HumidityEnum
BLEHumidity02Avg: HumidityEnum
BLEHumidity03Min: HumidityEnum
BLEHumidity03Max: HumidityEnum
BLEHumidity03Avg: HumidityEnum
BLEHumidity04Min: HumidityEnum
BLEHumidity04Max: HumidityEnum
BLEHumidity04Avg: HumidityEnum
DefaultTemperatureMin: TemperatureEnum
DefaultTemperatureMax: TemperatureEnum
DefaultTemperatureAvg: TemperatureEnum
IntakeAirTemperatureMin: TemperatureEnum
IntakeAirTemperatureMax: TemperatureEnum
IntakeAirTemperatureAvg: TemperatureEnum
AmbientAirTemperatureMin: TemperatureEnum
AmbientAirTemperatureMax: TemperatureEnum
AmbientAirTemperatureAvg: TemperatureEnum
EngineOilTemperatureMin: TemperatureEnum
EngineOilTemperatureMax: TemperatureEnum
EngineOilTemperatureAvg: TemperatureEnum
CoolantTemperatureMin: TemperatureEnum
CoolantTemperatureMax: TemperatureEnum
CoolantTemperatureAvg: TemperatureEnum
BLETemperature01Min: TemperatureEnum
BLETemperature01Max: TemperatureEnum
BLETemperature01Avg: TemperatureEnum
BLETemperature02Min: TemperatureEnum
BLETemperature02Max: TemperatureEnum
BLETemperature02Avg: TemperatureEnum
BLETemperature03Min: TemperatureEnum
BLETemperature03Max: TemperatureEnum
BLETemperature03Avg: TemperatureEnum
BLETemperature04Min: TemperatureEnum
BLETemperature04Max: TemperatureEnum
BLETemperature04Avg: TemperatureEnum
EngineTemperatureMin: TemperatureEnum
EngineTemperatureMax: TemperatureEnum
EngineTemperatureAvg: TemperatureEnum
BatteryTemperatureMin: TemperatureEnum
BatteryTemperatureMax: TemperatureEnum
BatteryTemperatureAvg: TemperatureEnum
DallasTemperature1Min: TemperatureEnum
DallasTemperature1Max: TemperatureEnum
DallasTemperature1Avg: TemperatureEnum
DallasTemperature2Min: TemperatureEnum
DallasTemperature2Max: TemperatureEnum
DallasTemperature2Avg: TemperatureEnum
DallasTemperature3Min: TemperatureEnum
DallasTemperature3Max: TemperatureEnum
DallasTemperature3Avg: TemperatureEnum
DallasTemperature4Min: TemperatureEnum
DallasTemperature4Max: TemperatureEnum
DallasTemperature4Avg: TemperatureEnum
LLSTemperature01Min: TemperatureEnum
LLSTemperature01Max: TemperatureEnum
LLSTemperature01Avg: TemperatureEnum
LLSTemperature02Min: TemperatureEnum
LLSTemperature02Max: TemperatureEnum
LLSTemperature02Avg: TemperatureEnum
LLSTemperature03Min: TemperatureEnum
LLSTemperature03Max: TemperatureEnum
LLSTemperature03Avg: TemperatureEnum
LLSTemperature04Min: TemperatureEnum
LLSTemperature04Max: TemperatureEnum
LLSTemperature04Avg: TemperatureEnum
EyeTemperature01Min: TemperatureEnum
EyeTemperature01Max: TemperatureEnum
EyeTemperature01Avg: TemperatureEnum
EyeTemperature02Min: TemperatureEnum
EyeTemperature02Max: TemperatureEnum
EyeTemperature02Avg: TemperatureEnum
EyeTemperature03Min: TemperatureEnum
EyeTemperature03Max: TemperatureEnum
EyeTemperature03Avg: TemperatureEnum
EyeTemperature04Min: TemperatureEnum
EyeTemperature04Max: TemperatureEnum
EyeTemperature04Avg: TemperatureEnum
DallasTemperature05Min: TemperatureEnum
DallasTemperature05Max: TemperatureEnum
DallasTemperature05Avg: TemperatureEnum
DallasTemperature06Min: TemperatureEnum
DallasTemperature06Max: TemperatureEnum
DallasTemperature06Avg: TemperatureEnum
Tire01TemperatureMin: TemperatureEnum
Tire01TemperatureMax: TemperatureEnum
Tire01TemperatureAvg: TemperatureEnum
Tire02TemperatureMin: TemperatureEnum
Tire02TemperatureMax: TemperatureEnum
Tire02TemperatureAvg: TemperatureEnum
Tire03TemperatureMin: TemperatureEnum
Tire03TemperatureMax: TemperatureEnum
Tire03TemperatureAvg: TemperatureEnum
Tire04TemperatureMin: TemperatureEnum
Tire04TemperatureMax: TemperatureEnum
Tire04TemperatureAvg: TemperatureEnum
Tire05TemperatureMin: TemperatureEnum
Tire05TemperatureMax: TemperatureEnum
Tire05TemperatureAvg: TemperatureEnum
Tire06TemperatureMin: TemperatureEnum
Tire06TemperatureMax: TemperatureEnum
Tire06TemperatureAvg: TemperatureEnum
Tire07TemperatureMin: TemperatureEnum
Tire07TemperatureMax: TemperatureEnum
Tire07TemperatureAvg: TemperatureEnum
Tire08TemperatureMin: TemperatureEnum
Tire08TemperatureMax: TemperatureEnum
Tire08TemperatureAvg: TemperatureEnum
Tire09TemperatureMin: TemperatureEnum
Tire09TemperatureMax: TemperatureEnum
Tire09TemperatureAvg: TemperatureEnum
Tire10TemperatureMin: TemperatureEnum
Tire10TemperatureMax: TemperatureEnum
Tire10TemperatureAvg: TemperatureEnum
Tire11TemperatureMin: TemperatureEnum
Tire11TemperatureMax: TemperatureEnum
Tire11TemperatureAvg: TemperatureEnum
Tire12TemperatureMin: TemperatureEnum
Tire12TemperatureMax: TemperatureEnum
Tire12TemperatureAvg: TemperatureEnum

class Monthly(_message.Message):
    __slots__ = ("id", "device_id", "mileage", "idling", "parking", "moving", "towing", "total_speed", "sum_speed", "max_speed", "trips", "compact", "started_at", "finished_at", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    IDLING_FIELD_NUMBER: _ClassVar[int]
    PARKING_FIELD_NUMBER: _ClassVar[int]
    MOVING_FIELD_NUMBER: _ClassVar[int]
    TOWING_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SPEED_FIELD_NUMBER: _ClassVar[int]
    SUM_SPEED_FIELD_NUMBER: _ClassVar[int]
    MAX_SPEED_FIELD_NUMBER: _ClassVar[int]
    TRIPS_FIELD_NUMBER: _ClassVar[int]
    COMPACT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    device_id: int
    mileage: int
    idling: int
    parking: int
    moving: int
    towing: int
    total_speed: int
    sum_speed: int
    max_speed: int
    trips: int
    compact: MonthlyCompact
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., device_id: _Optional[int] = ..., mileage: _Optional[int] = ..., idling: _Optional[int] = ..., parking: _Optional[int] = ..., moving: _Optional[int] = ..., towing: _Optional[int] = ..., total_speed: _Optional[int] = ..., sum_speed: _Optional[int] = ..., max_speed: _Optional[int] = ..., trips: _Optional[int] = ..., compact: _Optional[_Union[MonthlyCompact, _Mapping]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MonthlyCompact(_message.Message):
    __slots__ = ("cost", "records", "green_driving", "temperature", "humidity", "ignition", "door_opened", "fuel_used", "fuel_rate", "engine_rpm", "engine_load", "crashes", "speeds")
    class GreenDrivingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
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
    class CrashesEntry(_message.Message):
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
        value: TripDurationStat
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[TripDurationStat, _Mapping]] = ...) -> None: ...
    COST_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    GREEN_DRIVING_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    HUMIDITY_FIELD_NUMBER: _ClassVar[int]
    IGNITION_FIELD_NUMBER: _ClassVar[int]
    DOOR_OPENED_FIELD_NUMBER: _ClassVar[int]
    FUEL_USED_FIELD_NUMBER: _ClassVar[int]
    FUEL_RATE_FIELD_NUMBER: _ClassVar[int]
    ENGINE_RPM_FIELD_NUMBER: _ClassVar[int]
    ENGINE_LOAD_FIELD_NUMBER: _ClassVar[int]
    CRASHES_FIELD_NUMBER: _ClassVar[int]
    SPEEDS_FIELD_NUMBER: _ClassVar[int]
    cost: int
    records: int
    green_driving: _containers.ScalarMap[int, int]
    temperature: _containers.ScalarMap[int, int]
    humidity: _containers.ScalarMap[int, int]
    ignition: int
    door_opened: int
    fuel_used: int
    fuel_rate: int
    engine_rpm: int
    engine_load: int
    crashes: _containers.ScalarMap[int, int]
    speeds: _containers.MessageMap[int, TripDurationStat]
    def __init__(self, cost: _Optional[int] = ..., records: _Optional[int] = ..., green_driving: _Optional[_Mapping[int, int]] = ..., temperature: _Optional[_Mapping[int, int]] = ..., humidity: _Optional[_Mapping[int, int]] = ..., ignition: _Optional[int] = ..., door_opened: _Optional[int] = ..., fuel_used: _Optional[int] = ..., fuel_rate: _Optional[int] = ..., engine_rpm: _Optional[int] = ..., engine_load: _Optional[int] = ..., crashes: _Optional[_Mapping[int, int]] = ..., speeds: _Optional[_Mapping[int, TripDurationStat]] = ...) -> None: ...

class Trip(_message.Message):
    __slots__ = ("id", "device_id", "mileage", "idling", "parking", "moving", "towing", "total_speed", "sum_speed", "max_speed", "compact", "started_at", "finished_at", "created_at", "updated_at", "points")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    IDLING_FIELD_NUMBER: _ClassVar[int]
    PARKING_FIELD_NUMBER: _ClassVar[int]
    MOVING_FIELD_NUMBER: _ClassVar[int]
    TOWING_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SPEED_FIELD_NUMBER: _ClassVar[int]
    SUM_SPEED_FIELD_NUMBER: _ClassVar[int]
    MAX_SPEED_FIELD_NUMBER: _ClassVar[int]
    COMPACT_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    id: int
    device_id: int
    mileage: int
    idling: int
    parking: int
    moving: int
    towing: int
    total_speed: int
    sum_speed: int
    max_speed: int
    compact: TripCompact
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    points: _containers.RepeatedCompositeFieldContainer[TripPoint]
    def __init__(self, id: _Optional[int] = ..., device_id: _Optional[int] = ..., mileage: _Optional[int] = ..., idling: _Optional[int] = ..., parking: _Optional[int] = ..., moving: _Optional[int] = ..., towing: _Optional[int] = ..., total_speed: _Optional[int] = ..., sum_speed: _Optional[int] = ..., max_speed: _Optional[int] = ..., compact: _Optional[_Union[TripCompact, _Mapping]] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., points: _Optional[_Iterable[_Union[TripPoint, _Mapping]]] = ...) -> None: ...

class TripCompact(_message.Message):
    __slots__ = ("cost", "records", "start", "finish", "green_driving", "temperature", "humidity", "i_button", "ignition", "door_opened", "fuel_used", "fuel_rate", "engine_rpm", "engine_load", "crashes", "speeds", "points")
    class GreenDrivingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
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
    class CrashesEntry(_message.Message):
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
        value: TripDurationStat
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[TripDurationStat, _Mapping]] = ...) -> None: ...
    COST_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    FINISH_FIELD_NUMBER: _ClassVar[int]
    GREEN_DRIVING_FIELD_NUMBER: _ClassVar[int]
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
    cost: int
    records: int
    start: TripPoint
    finish: TripPoint
    green_driving: _containers.ScalarMap[int, int]
    temperature: _containers.ScalarMap[int, int]
    humidity: _containers.ScalarMap[int, int]
    i_button: int
    ignition: int
    door_opened: int
    fuel_used: int
    fuel_rate: int
    engine_rpm: int
    engine_load: int
    crashes: _containers.ScalarMap[int, int]
    speeds: _containers.MessageMap[int, TripDurationStat]
    points: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, cost: _Optional[int] = ..., records: _Optional[int] = ..., start: _Optional[_Union[TripPoint, _Mapping]] = ..., finish: _Optional[_Union[TripPoint, _Mapping]] = ..., green_driving: _Optional[_Mapping[int, int]] = ..., temperature: _Optional[_Mapping[int, int]] = ..., humidity: _Optional[_Mapping[int, int]] = ..., i_button: _Optional[int] = ..., ignition: _Optional[int] = ..., door_opened: _Optional[int] = ..., fuel_used: _Optional[int] = ..., fuel_rate: _Optional[int] = ..., engine_rpm: _Optional[int] = ..., engine_load: _Optional[int] = ..., crashes: _Optional[_Mapping[int, int]] = ..., speeds: _Optional[_Mapping[int, TripDurationStat]] = ..., points: _Optional[_Iterable[int]] = ...) -> None: ...

class TripPoint(_message.Message):
    __slots__ = ("latitude", "longitude", "angle")
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    ANGLE_FIELD_NUMBER: _ClassVar[int]
    latitude: float
    longitude: float
    angle: int
    def __init__(self, latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., angle: _Optional[int] = ...) -> None: ...

class TripDurationStat(_message.Message):
    __slots__ = ("duration", "mileage")
    DURATION_FIELD_NUMBER: _ClassVar[int]
    MILEAGE_FIELD_NUMBER: _ClassVar[int]
    duration: int
    mileage: int
    def __init__(self, duration: _Optional[int] = ..., mileage: _Optional[int] = ...) -> None: ...

class FusionTrip(_message.Message):
    __slots__ = ("id", "device_id", "mileage", "idling", "parking", "moving", "towing", "speed_total", "speed_sum", "speed_max", "records", "harsh_acceleration", "harsh_break", "harsh_corner", "min_temp01", "max_temp01", "min_temp02", "max_temp02", "min_temp03", "max_temp03", "min_temp04", "max_temp04", "min_humidity", "max_humidity", "start_lat", "start_lng", "finish_lat", "finish_lng", "started_at", "finished_at", "created_at", "updated_at", "Logs", "Fug")
    ID_FIELD_NUMBER: _ClassVar[int]
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
    MIN_TEMP01_FIELD_NUMBER: _ClassVar[int]
    MAX_TEMP01_FIELD_NUMBER: _ClassVar[int]
    MIN_TEMP02_FIELD_NUMBER: _ClassVar[int]
    MAX_TEMP02_FIELD_NUMBER: _ClassVar[int]
    MIN_TEMP03_FIELD_NUMBER: _ClassVar[int]
    MAX_TEMP03_FIELD_NUMBER: _ClassVar[int]
    MIN_TEMP04_FIELD_NUMBER: _ClassVar[int]
    MAX_TEMP04_FIELD_NUMBER: _ClassVar[int]
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
    LOGS_FIELD_NUMBER: _ClassVar[int]
    FUG_FIELD_NUMBER: _ClassVar[int]
    id: int
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
    min_temp01: int
    max_temp01: int
    min_temp02: int
    max_temp02: int
    min_temp03: int
    max_temp03: int
    min_temp04: int
    max_temp04: int
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
    Logs: str
    Fug: int
    def __init__(self, id: _Optional[int] = ..., device_id: _Optional[int] = ..., mileage: _Optional[int] = ..., idling: _Optional[int] = ..., parking: _Optional[int] = ..., moving: _Optional[int] = ..., towing: _Optional[int] = ..., speed_total: _Optional[int] = ..., speed_sum: _Optional[int] = ..., speed_max: _Optional[int] = ..., records: _Optional[int] = ..., harsh_acceleration: _Optional[int] = ..., harsh_break: _Optional[int] = ..., harsh_corner: _Optional[int] = ..., min_temp01: _Optional[int] = ..., max_temp01: _Optional[int] = ..., min_temp02: _Optional[int] = ..., max_temp02: _Optional[int] = ..., min_temp03: _Optional[int] = ..., max_temp03: _Optional[int] = ..., min_temp04: _Optional[int] = ..., max_temp04: _Optional[int] = ..., min_humidity: _Optional[int] = ..., max_humidity: _Optional[int] = ..., start_lat: _Optional[float] = ..., start_lng: _Optional[float] = ..., finish_lat: _Optional[float] = ..., finish_lng: _Optional[float] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., Logs: _Optional[str] = ..., Fug: _Optional[int] = ...) -> None: ...

class TripTask(_message.Message):
    __slots__ = ("event_type", "trip", "monthly", "fusion", "additional")
    class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        None: _ClassVar[TripTask.EventType]
        Odyssey: _ClassVar[TripTask.EventType]
        Fusion: _ClassVar[TripTask.EventType]
        Monthly: _ClassVar[TripTask.EventType]
    None: TripTask.EventType
    Odyssey: TripTask.EventType
    Fusion: TripTask.EventType
    Monthly: TripTask.EventType
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRIP_FIELD_NUMBER: _ClassVar[int]
    MONTHLY_FIELD_NUMBER: _ClassVar[int]
    FUSION_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_FIELD_NUMBER: _ClassVar[int]
    event_type: TripTask.EventType
    trip: Trip
    monthly: Monthly
    fusion: FusionTrip
    additional: bytes
    def __init__(self, event_type: _Optional[_Union[TripTask.EventType, str]] = ..., trip: _Optional[_Union[Trip, _Mapping]] = ..., monthly: _Optional[_Union[Monthly, _Mapping]] = ..., fusion: _Optional[_Union[FusionTrip, _Mapping]] = ..., additional: _Optional[bytes] = ...) -> None: ...
