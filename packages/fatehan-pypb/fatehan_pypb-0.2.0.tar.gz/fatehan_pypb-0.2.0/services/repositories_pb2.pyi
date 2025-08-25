from identities import identities_pb2 as _identities_pb2
from financial import financial_pb2 as _financial_pb2
from devices import devices_pb2 as _devices_pb2
from packets import dataModel_pb2 as _dataModel_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeviceRepo(_message.Message):
    __slots__ = ("device", "icon", "tracker", "car_repo", "device_status", "user_device_io", "owner_repo", "organization", "subscribed")
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    TRACKER_FIELD_NUMBER: _ClassVar[int]
    CAR_REPO_FIELD_NUMBER: _ClassVar[int]
    DEVICE_STATUS_FIELD_NUMBER: _ClassVar[int]
    USER_DEVICE_IO_FIELD_NUMBER: _ClassVar[int]
    OWNER_REPO_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBED_FIELD_NUMBER: _ClassVar[int]
    device: _devices_pb2.Device
    icon: _devices_pb2.DeviceIcon
    tracker: _devices_pb2.Tracker
    car_repo: CarRepo
    device_status: _dataModel_pb2.DeviceStatus
    user_device_io: _containers.RepeatedCompositeFieldContainer[_devices_pb2.SystemIo]
    owner_repo: UserRepo
    organization: _identities_pb2.Organization
    subscribed: bool
    def __init__(self, device: _Optional[_Union[_devices_pb2.Device, _Mapping]] = ..., icon: _Optional[_Union[_devices_pb2.DeviceIcon, _Mapping]] = ..., tracker: _Optional[_Union[_devices_pb2.Tracker, _Mapping]] = ..., car_repo: _Optional[_Union[CarRepo, _Mapping]] = ..., device_status: _Optional[_Union[_dataModel_pb2.DeviceStatus, _Mapping]] = ..., user_device_io: _Optional[_Iterable[_Union[_devices_pb2.SystemIo, _Mapping]]] = ..., owner_repo: _Optional[_Union[UserRepo, _Mapping]] = ..., organization: _Optional[_Union[_identities_pb2.Organization, _Mapping]] = ..., subscribed: bool = ...) -> None: ...

class CarRepo(_message.Message):
    __slots__ = ("car", "driver_repo", "car_model_repo")
    CAR_FIELD_NUMBER: _ClassVar[int]
    DRIVER_REPO_FIELD_NUMBER: _ClassVar[int]
    CAR_MODEL_REPO_FIELD_NUMBER: _ClassVar[int]
    car: _devices_pb2.Car
    driver_repo: DriverRepo
    car_model_repo: CarModelRepo
    def __init__(self, car: _Optional[_Union[_devices_pb2.Car, _Mapping]] = ..., driver_repo: _Optional[_Union[DriverRepo, _Mapping]] = ..., car_model_repo: _Optional[_Union[CarModelRepo, _Mapping]] = ...) -> None: ...

class PersonRepo(_message.Message):
    __slots__ = ("person", "wallet", "organization")
    PERSON_FIELD_NUMBER: _ClassVar[int]
    WALLET_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    person: _identities_pb2.Person
    wallet: _financial_pb2.Wallet
    organization: _identities_pb2.Organization
    def __init__(self, person: _Optional[_Union[_identities_pb2.Person, _Mapping]] = ..., wallet: _Optional[_Union[_financial_pb2.Wallet, _Mapping]] = ..., organization: _Optional[_Union[_identities_pb2.Organization, _Mapping]] = ...) -> None: ...

class UserRepo(_message.Message):
    __slots__ = ("user", "persons")
    USER_FIELD_NUMBER: _ClassVar[int]
    PERSONS_FIELD_NUMBER: _ClassVar[int]
    user: _identities_pb2.User
    persons: _containers.RepeatedCompositeFieldContainer[_identities_pb2.Person]
    def __init__(self, user: _Optional[_Union[_identities_pb2.User, _Mapping]] = ..., persons: _Optional[_Iterable[_Union[_identities_pb2.Person, _Mapping]]] = ...) -> None: ...

class DriverRepo(_message.Message):
    __slots__ = ("driver", "person")
    DRIVER_FIELD_NUMBER: _ClassVar[int]
    PERSON_FIELD_NUMBER: _ClassVar[int]
    driver: _identities_pb2.Driver
    person: _identities_pb2.Person
    def __init__(self, driver: _Optional[_Union[_identities_pb2.Driver, _Mapping]] = ..., person: _Optional[_Union[_identities_pb2.Person, _Mapping]] = ...) -> None: ...

class CarModelRepo(_message.Message):
    __slots__ = ("car_model", "car_brand")
    CAR_MODEL_FIELD_NUMBER: _ClassVar[int]
    CAR_BRAND_FIELD_NUMBER: _ClassVar[int]
    car_model: _devices_pb2.CarModel
    car_brand: _devices_pb2.CarBrand
    def __init__(self, car_model: _Optional[_Union[_devices_pb2.CarModel, _Mapping]] = ..., car_brand: _Optional[_Union[_devices_pb2.CarBrand, _Mapping]] = ...) -> None: ...
