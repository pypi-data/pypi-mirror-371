import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("id", "email", "telegram_id", "phone", "status", "created_by", "updated_by", "created_at", "updated_at", "persons", "token")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    TELEGRAM_ID_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PERSONS_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    id: int
    email: str
    telegram_id: str
    phone: str
    status: int
    created_by: int
    updated_by: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    persons: _containers.RepeatedCompositeFieldContainer[Person]
    token: str
    def __init__(self, id: _Optional[int] = ..., email: _Optional[str] = ..., telegram_id: _Optional[str] = ..., phone: _Optional[str] = ..., status: _Optional[int] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., persons: _Optional[_Iterable[_Union[Person, _Mapping]]] = ..., token: _Optional[str] = ...) -> None: ...

class Person(_message.Message):
    __slots__ = ("id", "type", "organization_id", "role_id", "user_id", "partner_id", "created_by", "updated_by", "is_complete", "name", "image", "national_id", "economical_id", "identification_number", "postal_code", "address", "birth_date", "contact_mobile", "contact_phone", "created_at", "updated_at", "organization")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PARTNER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    IS_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    NATIONAL_ID_FIELD_NUMBER: _ClassVar[int]
    ECONOMICAL_ID_FIELD_NUMBER: _ClassVar[int]
    IDENTIFICATION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    POSTAL_CODE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    BIRTH_DATE_FIELD_NUMBER: _ClassVar[int]
    CONTACT_MOBILE_FIELD_NUMBER: _ClassVar[int]
    CONTACT_PHONE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    id: int
    type: int
    organization_id: int
    role_id: int
    user_id: int
    partner_id: int
    created_by: int
    updated_by: int
    is_complete: int
    name: str
    image: str
    national_id: str
    economical_id: str
    identification_number: str
    postal_code: str
    address: str
    birth_date: _timestamp_pb2.Timestamp
    contact_mobile: str
    contact_phone: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    organization: Organization
    def __init__(self, id: _Optional[int] = ..., type: _Optional[int] = ..., organization_id: _Optional[int] = ..., role_id: _Optional[int] = ..., user_id: _Optional[int] = ..., partner_id: _Optional[int] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., is_complete: _Optional[int] = ..., name: _Optional[str] = ..., image: _Optional[str] = ..., national_id: _Optional[str] = ..., economical_id: _Optional[str] = ..., identification_number: _Optional[str] = ..., postal_code: _Optional[str] = ..., address: _Optional[str] = ..., birth_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., contact_mobile: _Optional[str] = ..., contact_phone: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., organization: _Optional[_Union[Organization, _Mapping]] = ...) -> None: ...

class Organization(_message.Message):
    __slots__ = ("id", "name", "number", "picture", "status", "is_partner", "metadata", "domains", "generation", "parent_id", "level", "owner_id", "created_by", "deleted_at", "created_at", "updated_at")
    class MetaData(_message.Message):
        __slots__ = ("fax", "lat", "long", "zoom", "about", "email", "rules", "mobile", "address", "mobile2", "website", "is_legal", "telegram", "instagram", "telephone", "company_id", "telephone2", "national_id", "postal_code", "economical_id", "registration_date")
        FAX_FIELD_NUMBER: _ClassVar[int]
        LAT_FIELD_NUMBER: _ClassVar[int]
        LONG_FIELD_NUMBER: _ClassVar[int]
        ZOOM_FIELD_NUMBER: _ClassVar[int]
        ABOUT_FIELD_NUMBER: _ClassVar[int]
        EMAIL_FIELD_NUMBER: _ClassVar[int]
        RULES_FIELD_NUMBER: _ClassVar[int]
        MOBILE_FIELD_NUMBER: _ClassVar[int]
        ADDRESS_FIELD_NUMBER: _ClassVar[int]
        MOBILE2_FIELD_NUMBER: _ClassVar[int]
        WEBSITE_FIELD_NUMBER: _ClassVar[int]
        IS_LEGAL_FIELD_NUMBER: _ClassVar[int]
        TELEGRAM_FIELD_NUMBER: _ClassVar[int]
        INSTAGRAM_FIELD_NUMBER: _ClassVar[int]
        TELEPHONE_FIELD_NUMBER: _ClassVar[int]
        COMPANY_ID_FIELD_NUMBER: _ClassVar[int]
        TELEPHONE2_FIELD_NUMBER: _ClassVar[int]
        NATIONAL_ID_FIELD_NUMBER: _ClassVar[int]
        POSTAL_CODE_FIELD_NUMBER: _ClassVar[int]
        ECONOMICAL_ID_FIELD_NUMBER: _ClassVar[int]
        REGISTRATION_DATE_FIELD_NUMBER: _ClassVar[int]
        fax: str
        lat: float
        long: float
        zoom: int
        about: str
        email: str
        rules: str
        mobile: str
        address: str
        mobile2: str
        website: str
        is_legal: int
        telegram: str
        instagram: str
        telephone: str
        company_id: int
        telephone2: str
        national_id: str
        postal_code: str
        economical_id: str
        registration_date: str
        def __init__(self, fax: _Optional[str] = ..., lat: _Optional[float] = ..., long: _Optional[float] = ..., zoom: _Optional[int] = ..., about: _Optional[str] = ..., email: _Optional[str] = ..., rules: _Optional[str] = ..., mobile: _Optional[str] = ..., address: _Optional[str] = ..., mobile2: _Optional[str] = ..., website: _Optional[str] = ..., is_legal: _Optional[int] = ..., telegram: _Optional[str] = ..., instagram: _Optional[str] = ..., telephone: _Optional[str] = ..., company_id: _Optional[int] = ..., telephone2: _Optional[str] = ..., national_id: _Optional[str] = ..., postal_code: _Optional[str] = ..., economical_id: _Optional[str] = ..., registration_date: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IS_PARTNER_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    DOMAINS_FIELD_NUMBER: _ClassVar[int]
    GENERATION_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    number: str
    picture: str
    status: bool
    is_partner: bool
    metadata: Organization.MetaData
    domains: _containers.RepeatedScalarFieldContainer[str]
    generation: str
    parent_id: int
    level: int
    owner_id: int
    created_by: int
    deleted_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., number: _Optional[str] = ..., picture: _Optional[str] = ..., status: bool = ..., is_partner: bool = ..., metadata: _Optional[_Union[Organization.MetaData, _Mapping]] = ..., domains: _Optional[_Iterable[str]] = ..., generation: _Optional[str] = ..., parent_id: _Optional[int] = ..., level: _Optional[int] = ..., owner_id: _Optional[int] = ..., created_by: _Optional[int] = ..., deleted_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Permission(_message.Message):
    __slots__ = ("id", "name", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Driver(_message.Message):
    __slots__ = ("id", "organization_id", "created_by", "updated_by", "person_id", "driver_identify", "license_number", "hiring_date", "monthly_salary", "license_type", "license_expire", "commission_percentage", "status", "mobile_number", "phone_number", "address", "postal_code", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    PERSON_ID_FIELD_NUMBER: _ClassVar[int]
    DRIVER_IDENTIFY_FIELD_NUMBER: _ClassVar[int]
    LICENSE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    HIRING_DATE_FIELD_NUMBER: _ClassVar[int]
    MONTHLY_SALARY_FIELD_NUMBER: _ClassVar[int]
    LICENSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    LICENSE_EXPIRE_FIELD_NUMBER: _ClassVar[int]
    COMMISSION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MOBILE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    POSTAL_CODE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    created_by: int
    updated_by: int
    person_id: int
    driver_identify: str
    license_number: str
    hiring_date: str
    monthly_salary: int
    license_type: int
    license_expire: str
    commission_percentage: int
    status: bool
    mobile_number: str
    phone_number: str
    address: str
    postal_code: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., person_id: _Optional[int] = ..., driver_identify: _Optional[str] = ..., license_number: _Optional[str] = ..., hiring_date: _Optional[str] = ..., monthly_salary: _Optional[int] = ..., license_type: _Optional[int] = ..., license_expire: _Optional[str] = ..., commission_percentage: _Optional[int] = ..., status: bool = ..., mobile_number: _Optional[str] = ..., phone_number: _Optional[str] = ..., address: _Optional[str] = ..., postal_code: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
