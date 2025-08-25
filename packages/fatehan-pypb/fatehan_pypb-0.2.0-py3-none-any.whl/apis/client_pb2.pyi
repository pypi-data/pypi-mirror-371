import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from notifies import notify_pb2 as _notify_pb2
from identities import identities_pb2 as _identities_pb2
from financial import financial_pb2 as _financial_pb2
from devices import devices_pb2 as _devices_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MessageOnly(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class UserPagination(_message.Message):
    __slots__ = ("current_page", "first_page_url", "last_page_url", "next_page_url", "prev_page_url", "path", "last_page", "per_page", "to", "data")
    CURRENT_PAGE_FIELD_NUMBER: _ClassVar[int]
    FIRST_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    current_page: int
    first_page_url: str
    last_page_url: str
    next_page_url: str
    prev_page_url: str
    path: str
    last_page: int
    per_page: int
    to: int
    data: _containers.RepeatedCompositeFieldContainer[_identities_pb2.User]
    def __init__(self, current_page: _Optional[int] = ..., first_page_url: _Optional[str] = ..., last_page_url: _Optional[str] = ..., next_page_url: _Optional[str] = ..., prev_page_url: _Optional[str] = ..., path: _Optional[str] = ..., last_page: _Optional[int] = ..., per_page: _Optional[int] = ..., to: _Optional[int] = ..., data: _Optional[_Iterable[_Union[_identities_pb2.User, _Mapping]]] = ..., **kwargs) -> None: ...

class VersionCheck(_message.Message):
    __slots__ = ("status", "message", "current_version", "force_update", "partner_version", "user_version")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    FORCE_UPDATE_FIELD_NUMBER: _ClassVar[int]
    PARTNER_VERSION_FIELD_NUMBER: _ClassVar[int]
    USER_VERSION_FIELD_NUMBER: _ClassVar[int]
    status: bool
    message: str
    current_version: str
    force_update: bool
    partner_version: str
    user_version: str
    def __init__(self, status: bool = ..., message: _Optional[str] = ..., current_version: _Optional[str] = ..., force_update: bool = ..., partner_version: _Optional[str] = ..., user_version: _Optional[str] = ...) -> None: ...

class Me(_message.Message):
    __slots__ = ("user", "person", "currencies", "permissions", "device", "device_count")
    USER_FIELD_NUMBER: _ClassVar[int]
    PERSON_FIELD_NUMBER: _ClassVar[int]
    CURRENCIES_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_COUNT_FIELD_NUMBER: _ClassVar[int]
    user: _identities_pb2.User
    person: _containers.RepeatedCompositeFieldContainer[_identities_pb2.Person]
    currencies: _containers.RepeatedCompositeFieldContainer[_financial_pb2.Currency]
    permissions: _containers.RepeatedCompositeFieldContainer[_identities_pb2.Permission]
    device: _devices_pb2.Device
    device_count: int
    def __init__(self, user: _Optional[_Union[_identities_pb2.User, _Mapping]] = ..., person: _Optional[_Iterable[_Union[_identities_pb2.Person, _Mapping]]] = ..., currencies: _Optional[_Iterable[_Union[_financial_pb2.Currency, _Mapping]]] = ..., permissions: _Optional[_Iterable[_Union[_identities_pb2.Permission, _Mapping]]] = ..., device: _Optional[_Union[_devices_pb2.Device, _Mapping]] = ..., device_count: _Optional[int] = ...) -> None: ...

class DevicePagination(_message.Message):
    __slots__ = ("current_page", "first_page_url", "last_page_url", "next_page_url", "prev_page_url", "path", "last_page", "per_page", "to", "data")
    CURRENT_PAGE_FIELD_NUMBER: _ClassVar[int]
    FIRST_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    current_page: int
    first_page_url: str
    last_page_url: str
    next_page_url: str
    prev_page_url: str
    path: str
    last_page: int
    per_page: int
    to: int
    data: _containers.RepeatedCompositeFieldContainer[_devices_pb2.Device]
    def __init__(self, current_page: _Optional[int] = ..., first_page_url: _Optional[str] = ..., last_page_url: _Optional[str] = ..., next_page_url: _Optional[str] = ..., prev_page_url: _Optional[str] = ..., path: _Optional[str] = ..., last_page: _Optional[int] = ..., per_page: _Optional[int] = ..., to: _Optional[int] = ..., data: _Optional[_Iterable[_Union[_devices_pb2.Device, _Mapping]]] = ..., **kwargs) -> None: ...

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

class ConfigList(_message.Message):
    __slots__ = ("configs",)
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    configs: _containers.RepeatedCompositeFieldContainer[Config]
    def __init__(self, configs: _Optional[_Iterable[_Union[Config, _Mapping]]] = ...) -> None: ...

class TransactionPagination(_message.Message):
    __slots__ = ("current_page", "first_page_url", "last_page_url", "next_page_url", "prev_page_url", "path", "last_page", "per_page", "to", "data")
    CURRENT_PAGE_FIELD_NUMBER: _ClassVar[int]
    FIRST_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    current_page: int
    first_page_url: str
    last_page_url: str
    next_page_url: str
    prev_page_url: str
    path: str
    last_page: int
    per_page: int
    to: int
    data: _containers.RepeatedCompositeFieldContainer[Transaction]
    def __init__(self, current_page: _Optional[int] = ..., first_page_url: _Optional[str] = ..., last_page_url: _Optional[str] = ..., next_page_url: _Optional[str] = ..., prev_page_url: _Optional[str] = ..., path: _Optional[str] = ..., last_page: _Optional[int] = ..., per_page: _Optional[int] = ..., to: _Optional[int] = ..., data: _Optional[_Iterable[_Union[Transaction, _Mapping]]] = ..., **kwargs) -> None: ...

class Transaction(_message.Message):
    __slots__ = ("id", "organization_id", "from_user_id", "created_by", "updated_by", "transaction_reason", "picture", "description", "from_currency_id", "to_currency_id", "price", "type", "created_at", "updated_at", "currency", "organization")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_USER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_REASON_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FROM_CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    TO_CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    from_user_id: int
    created_by: int
    updated_by: int
    transaction_reason: str
    picture: str
    description: str
    from_currency_id: int
    to_currency_id: int
    price: str
    type: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    currency: _financial_pb2.Currency
    organization: _identities_pb2.Organization
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., from_user_id: _Optional[int] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., transaction_reason: _Optional[str] = ..., picture: _Optional[str] = ..., description: _Optional[str] = ..., from_currency_id: _Optional[int] = ..., to_currency_id: _Optional[int] = ..., price: _Optional[str] = ..., type: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., currency: _Optional[_Union[_financial_pb2.Currency, _Mapping]] = ..., organization: _Optional[_Union[_identities_pb2.Organization, _Mapping]] = ...) -> None: ...

class PaymentGateway(_message.Message):
    __slots__ = ("id", "organization_id", "created_by", "updated_by", "gateway", "name", "default", "status", "config", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    created_by: int
    updated_by: int
    gateway: str
    name: str
    default: bool
    status: bool
    config: _containers.RepeatedCompositeFieldContainer[Config]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., gateway: _Optional[str] = ..., name: _Optional[str] = ..., default: bool = ..., status: bool = ..., config: _Optional[_Iterable[_Union[Config, _Mapping]]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Partner(_message.Message):
    __slots__ = ("id", "name", "domains")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DOMAINS_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    domains: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., domains: _Optional[_Iterable[str]] = ...) -> None: ...

class ProductType(_message.Message):
    __slots__ = ("id", "name", "description", "months", "key_type", "picture", "created_by", "updated_by", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MONTHS_FIELD_NUMBER: _ClassVar[int]
    KEY_TYPE_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    description: str
    months: int
    key_type: str
    picture: str
    created_by: int
    updated_by: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., months: _Optional[int] = ..., key_type: _Optional[str] = ..., picture: _Optional[str] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class OrderPagination(_message.Message):
    __slots__ = ("current_page", "first_page_url", "last_page_url", "next_page_url", "prev_page_url", "path", "last_page", "per_page", "to", "data")
    CURRENT_PAGE_FIELD_NUMBER: _ClassVar[int]
    FIRST_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    current_page: int
    first_page_url: str
    last_page_url: str
    next_page_url: str
    prev_page_url: str
    path: str
    last_page: int
    per_page: int
    to: int
    data: _containers.RepeatedCompositeFieldContainer[Order]
    def __init__(self, current_page: _Optional[int] = ..., first_page_url: _Optional[str] = ..., last_page_url: _Optional[str] = ..., next_page_url: _Optional[str] = ..., prev_page_url: _Optional[str] = ..., path: _Optional[str] = ..., last_page: _Optional[int] = ..., per_page: _Optional[int] = ..., to: _Optional[int] = ..., data: _Optional[_Iterable[_Union[Order, _Mapping]]] = ..., **kwargs) -> None: ...

class Order(_message.Message):
    __slots__ = ("id", "uuid", "organization_id", "created_by", "payment_gateway_id", "currency_id", "partner_id", "total_price", "tax", "tax_percent", "discount", "subtotal", "payment_url", "transaction_id", "ref_id", "paid_at", "months", "status", "created_at", "updated_at", "products", "partner", "payment_gateway", "currency", "person")
    ID_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PARTNER_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_FIELD_NUMBER: _ClassVar[int]
    TAX_PERCENT_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    SUBTOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_URL_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    PAID_AT_FIELD_NUMBER: _ClassVar[int]
    MONTHS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    PARTNER_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_GATEWAY_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    PERSON_FIELD_NUMBER: _ClassVar[int]
    id: int
    uuid: str
    organization_id: int
    created_by: int
    payment_gateway_id: int
    currency_id: int
    partner_id: int
    total_price: float
    tax: float
    tax_percent: int
    discount: float
    subtotal: float
    payment_url: str
    transaction_id: str
    ref_id: str
    paid_at: _timestamp_pb2.Timestamp
    months: int
    status: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    products: _containers.RepeatedCompositeFieldContainer[OrderProduct]
    partner: Partner
    payment_gateway: PaymentGateway
    currency: _financial_pb2.Currency
    person: _identities_pb2.Person
    def __init__(self, id: _Optional[int] = ..., uuid: _Optional[str] = ..., organization_id: _Optional[int] = ..., created_by: _Optional[int] = ..., payment_gateway_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., partner_id: _Optional[int] = ..., total_price: _Optional[float] = ..., tax: _Optional[float] = ..., tax_percent: _Optional[int] = ..., discount: _Optional[float] = ..., subtotal: _Optional[float] = ..., payment_url: _Optional[str] = ..., transaction_id: _Optional[str] = ..., ref_id: _Optional[str] = ..., paid_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., months: _Optional[int] = ..., status: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., products: _Optional[_Iterable[_Union[OrderProduct, _Mapping]]] = ..., partner: _Optional[_Union[Partner, _Mapping]] = ..., payment_gateway: _Optional[_Union[PaymentGateway, _Mapping]] = ..., currency: _Optional[_Union[_financial_pb2.Currency, _Mapping]] = ..., person: _Optional[_Union[_identities_pb2.Person, _Mapping]] = ...) -> None: ...

class OrderProduct(_message.Message):
    __slots__ = ("id", "order_id", "product_id", "product_type", "product_name", "product_detail", "currency_id", "discount_percent", "tax_price", "discount", "price", "months", "created_at", "updated_at", "product")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_DETAIL_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_PERCENT_FIELD_NUMBER: _ClassVar[int]
    TAX_PRICE_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    MONTHS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    id: int
    order_id: int
    product_id: int
    product_type: str
    product_name: str
    product_detail: str
    currency_id: int
    discount_percent: int
    tax_price: float
    discount: float
    price: float
    months: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    product: Product
    def __init__(self, id: _Optional[int] = ..., order_id: _Optional[int] = ..., product_id: _Optional[int] = ..., product_type: _Optional[str] = ..., product_name: _Optional[str] = ..., product_detail: _Optional[str] = ..., currency_id: _Optional[int] = ..., discount_percent: _Optional[int] = ..., tax_price: _Optional[float] = ..., discount: _Optional[float] = ..., price: _Optional[float] = ..., months: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., product: _Optional[_Union[Product, _Mapping]] = ...) -> None: ...

class Product(_message.Message):
    __slots__ = ("id", "organization_id", "product_type_id", "created_by", "updated_by", "name", "display_name", "description", "properties", "picture", "slug", "uuid", "object_type", "object_id", "currency_id", "price", "created_at", "updated_at", "components", "currency", "product_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: int
    organization_id: int
    product_type_id: int
    created_by: int
    updated_by: int
    name: str
    display_name: str
    description: str
    properties: str
    picture: str
    slug: str
    uuid: str
    object_type: str
    object_id: int
    currency_id: int
    price: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    components: _containers.RepeatedCompositeFieldContainer[Product]
    currency: _financial_pb2.Currency
    product_type: ProductType
    def __init__(self, id: _Optional[int] = ..., organization_id: _Optional[int] = ..., product_type_id: _Optional[int] = ..., created_by: _Optional[int] = ..., updated_by: _Optional[int] = ..., name: _Optional[str] = ..., display_name: _Optional[str] = ..., description: _Optional[str] = ..., properties: _Optional[str] = ..., picture: _Optional[str] = ..., slug: _Optional[str] = ..., uuid: _Optional[str] = ..., object_type: _Optional[str] = ..., object_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., price: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., components: _Optional[_Iterable[_Union[Product, _Mapping]]] = ..., currency: _Optional[_Union[_financial_pb2.Currency, _Mapping]] = ..., product_type: _Optional[_Union[ProductType, _Mapping]] = ...) -> None: ...

class Channel(_message.Message):
    __slots__ = ("name", "count")
    NAME_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    name: str
    count: int
    def __init__(self, name: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class Statistics(_message.Message):
    __slots__ = ("total", "read", "unread", "channels_used")
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    READ_FIELD_NUMBER: _ClassVar[int]
    UNREAD_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_USED_FIELD_NUMBER: _ClassVar[int]
    total: int
    read: int
    unread: int
    channels_used: _containers.RepeatedCompositeFieldContainer[Channel]
    def __init__(self, total: _Optional[int] = ..., read: _Optional[int] = ..., unread: _Optional[int] = ..., channels_used: _Optional[_Iterable[_Union[Channel, _Mapping]]] = ...) -> None: ...

class TopRepeatedNotification(_message.Message):
    __slots__ = ("title", "count")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    title: str
    count: int
    def __init__(self, title: _Optional[str] = ..., count: _Optional[int] = ...) -> None: ...

class NotificationFull(_message.Message):
    __slots__ = ("uuid", "user_id", "object_id", "object_type", "title", "body", "alert_id", "user_alert_id", "alert", "via", "image", "sound", "read_at", "created_at", "updated_at", "alert_model", "user_alert", "data", "channels")
    class RawData(_message.Message):
        __slots__ = ("latitude", "longitude", "area_id", "area_name", "device_id", "alert_value", "gps_time")
        LATITUDE_FIELD_NUMBER: _ClassVar[int]
        LONGITUDE_FIELD_NUMBER: _ClassVar[int]
        AREA_ID_FIELD_NUMBER: _ClassVar[int]
        AREA_NAME_FIELD_NUMBER: _ClassVar[int]
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        ALERT_VALUE_FIELD_NUMBER: _ClassVar[int]
        GPS_TIME_FIELD_NUMBER: _ClassVar[int]
        latitude: float
        longitude: float
        area_id: int
        area_name: str
        device_id: int
        alert_value: int
        gps_time: _timestamp_pb2.Timestamp
        def __init__(self, latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., area_id: _Optional[int] = ..., area_name: _Optional[str] = ..., device_id: _Optional[int] = ..., alert_value: _Optional[int] = ..., gps_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    UUID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    ALERT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ALERT_ID_FIELD_NUMBER: _ClassVar[int]
    ALERT_FIELD_NUMBER: _ClassVar[int]
    VIA_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    SOUND_FIELD_NUMBER: _ClassVar[int]
    READ_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ALERT_MODEL_FIELD_NUMBER: _ClassVar[int]
    USER_ALERT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    user_id: int
    object_id: int
    object_type: str
    title: str
    body: str
    alert_id: int
    user_alert_id: int
    alert: int
    via: _containers.RepeatedScalarFieldContainer[int]
    image: str
    sound: int
    read_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    alert_model: _notify_pb2.AlertModel
    user_alert: _notify_pb2.UserDeviceAlert
    data: NotificationFull.RawData
    channels: _containers.RepeatedCompositeFieldContainer[Channel]
    def __init__(self, uuid: _Optional[str] = ..., user_id: _Optional[int] = ..., object_id: _Optional[int] = ..., object_type: _Optional[str] = ..., title: _Optional[str] = ..., body: _Optional[str] = ..., alert_id: _Optional[int] = ..., user_alert_id: _Optional[int] = ..., alert: _Optional[int] = ..., via: _Optional[_Iterable[int]] = ..., image: _Optional[str] = ..., sound: _Optional[int] = ..., read_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., alert_model: _Optional[_Union[_notify_pb2.AlertModel, _Mapping]] = ..., user_alert: _Optional[_Union[_notify_pb2.UserDeviceAlert, _Mapping]] = ..., data: _Optional[_Union[NotificationFull.RawData, _Mapping]] = ..., channels: _Optional[_Iterable[_Union[Channel, _Mapping]]] = ...) -> None: ...

class NotificationPagination(_message.Message):
    __slots__ = ("current_page", "first_page_url", "last_page_url", "next_page_url", "prev_page_url", "path", "last_page", "per_page", "to", "data")
    CURRENT_PAGE_FIELD_NUMBER: _ClassVar[int]
    FIRST_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    current_page: int
    first_page_url: str
    last_page_url: str
    next_page_url: str
    prev_page_url: str
    path: str
    last_page: int
    per_page: int
    to: int
    data: _containers.RepeatedCompositeFieldContainer[NotificationFull]
    def __init__(self, current_page: _Optional[int] = ..., first_page_url: _Optional[str] = ..., last_page_url: _Optional[str] = ..., next_page_url: _Optional[str] = ..., prev_page_url: _Optional[str] = ..., path: _Optional[str] = ..., last_page: _Optional[int] = ..., per_page: _Optional[int] = ..., to: _Optional[int] = ..., data: _Optional[_Iterable[_Union[NotificationFull, _Mapping]]] = ..., **kwargs) -> None: ...
