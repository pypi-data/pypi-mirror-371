from areas import area_pb2 as _area_pb2
from identities import identities_pb2 as _identities_pb2
from financial import financial_pb2 as _financial_pb2
from services import repositories_pb2 as _repositories_pb2
from models import models_pb2 as _models_pb2
from activities import workflow_pb2 as _workflow_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WorkflowResponse(_message.Message):
    __slots__ = ("current_page", "to", "last_page", "per_page", "cost", "total", "data")
    CURRENT_PAGE_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    current_page: int
    to: int
    last_page: int
    per_page: int
    cost: int
    total: int
    data: _containers.RepeatedCompositeFieldContainer[_workflow_pb2.Workflow]
    def __init__(self, current_page: _Optional[int] = ..., to: _Optional[int] = ..., last_page: _Optional[int] = ..., per_page: _Optional[int] = ..., cost: _Optional[int] = ..., total: _Optional[int] = ..., data: _Optional[_Iterable[_Union[_workflow_pb2.Workflow, _Mapping]]] = ..., **kwargs) -> None: ...

class WorkflowRequest(_message.Message):
    __slots__ = ("disable_pagination", "page", "page_size", "organization_id", "query_filter", "sort", "order")
    class QueryFilterEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FilterScope
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FilterScope, _Mapping]] = ...) -> None: ...
    DISABLE_PAGINATION_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_FILTER_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    disable_pagination: bool
    page: int
    page_size: int
    organization_id: int
    query_filter: _containers.MessageMap[str, FilterScope]
    sort: str
    order: str
    def __init__(self, disable_pagination: bool = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., organization_id: _Optional[int] = ..., query_filter: _Optional[_Mapping[str, FilterScope]] = ..., sort: _Optional[str] = ..., order: _Optional[str] = ...) -> None: ...

class ConfigRequest(_message.Message):
    __slots__ = ("domain", "partner_id")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    PARTNER_ID_FIELD_NUMBER: _ClassVar[int]
    domain: str
    partner_id: int
    def __init__(self, domain: _Optional[str] = ..., partner_id: _Optional[int] = ...) -> None: ...

class ConfigResponse(_message.Message):
    __slots__ = ("cost", "records", "list")
    COST_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    cost: int
    records: int
    list: _containers.RepeatedCompositeFieldContainer[_models_pb2.Config]
    def __init__(self, cost: _Optional[int] = ..., records: _Optional[int] = ..., list: _Optional[_Iterable[_Union[_models_pb2.Config, _Mapping]]] = ...) -> None: ...

class DeviceRequest(_message.Message):
    __slots__ = ("disable_pagination", "page", "page_size", "organization_id", "tracker_id", "search", "include_device_status", "query_filter", "sort", "order")
    class QueryFilterEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FilterScope
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FilterScope, _Mapping]] = ...) -> None: ...
    DISABLE_PAGINATION_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    TRACKER_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_DEVICE_STATUS_FIELD_NUMBER: _ClassVar[int]
    QUERY_FILTER_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    disable_pagination: bool
    page: int
    page_size: int
    organization_id: int
    tracker_id: int
    search: str
    include_device_status: bool
    query_filter: _containers.MessageMap[str, FilterScope]
    sort: str
    order: str
    def __init__(self, disable_pagination: bool = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., organization_id: _Optional[int] = ..., tracker_id: _Optional[int] = ..., search: _Optional[str] = ..., include_device_status: bool = ..., query_filter: _Optional[_Mapping[str, FilterScope]] = ..., sort: _Optional[str] = ..., order: _Optional[str] = ...) -> None: ...

class DeviceResponse(_message.Message):
    __slots__ = ("current_page", "to", "last_page", "per_page", "cost", "total", "data")
    CURRENT_PAGE_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    current_page: int
    to: int
    last_page: int
    per_page: int
    cost: int
    total: int
    data: _containers.RepeatedCompositeFieldContainer[_repositories_pb2.DeviceRepo]
    def __init__(self, current_page: _Optional[int] = ..., to: _Optional[int] = ..., last_page: _Optional[int] = ..., per_page: _Optional[int] = ..., cost: _Optional[int] = ..., total: _Optional[int] = ..., data: _Optional[_Iterable[_Union[_repositories_pb2.DeviceRepo, _Mapping]]] = ..., **kwargs) -> None: ...

class MeRequest(_message.Message):
    __slots__ = ("device_id",)
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    device_id: int
    def __init__(self, device_id: _Optional[int] = ...) -> None: ...

class MeResponse(_message.Message):
    __slots__ = ("user", "person", "currencies", "permissions", "device", "device_count", "cost")
    USER_FIELD_NUMBER: _ClassVar[int]
    PERSON_FIELD_NUMBER: _ClassVar[int]
    CURRENCIES_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_COUNT_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    user: _identities_pb2.User
    person: _containers.RepeatedCompositeFieldContainer[_repositories_pb2.PersonRepo]
    currencies: _containers.RepeatedCompositeFieldContainer[_financial_pb2.Currency]
    permissions: _containers.RepeatedCompositeFieldContainer[_identities_pb2.Permission]
    device: _repositories_pb2.DeviceRepo
    device_count: int
    cost: int
    def __init__(self, user: _Optional[_Union[_identities_pb2.User, _Mapping]] = ..., person: _Optional[_Iterable[_Union[_repositories_pb2.PersonRepo, _Mapping]]] = ..., currencies: _Optional[_Iterable[_Union[_financial_pb2.Currency, _Mapping]]] = ..., permissions: _Optional[_Iterable[_Union[_identities_pb2.Permission, _Mapping]]] = ..., device: _Optional[_Union[_repositories_pb2.DeviceRepo, _Mapping]] = ..., device_count: _Optional[int] = ..., cost: _Optional[int] = ...) -> None: ...

class AreaIndexRequest(_message.Message):
    __slots__ = ("disable_pagination", "page", "page_size", "organization_ids", "area_ids")
    DISABLE_PAGINATION_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_IDS_FIELD_NUMBER: _ClassVar[int]
    AREA_IDS_FIELD_NUMBER: _ClassVar[int]
    disable_pagination: bool
    page: int
    page_size: int
    organization_ids: _containers.RepeatedScalarFieldContainer[int]
    area_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, disable_pagination: bool = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., organization_ids: _Optional[_Iterable[int]] = ..., area_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class AreaIndexResponse(_message.Message):
    __slots__ = ("current_page", "to", "last_page", "per_page", "cost", "total", "data")
    CURRENT_PAGE_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    LAST_PAGE_FIELD_NUMBER: _ClassVar[int]
    PER_PAGE_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    current_page: int
    to: int
    last_page: int
    per_page: int
    cost: int
    total: int
    data: _containers.RepeatedCompositeFieldContainer[_area_pb2.Area]
    def __init__(self, current_page: _Optional[int] = ..., to: _Optional[int] = ..., last_page: _Optional[int] = ..., per_page: _Optional[int] = ..., cost: _Optional[int] = ..., total: _Optional[int] = ..., data: _Optional[_Iterable[_Union[_area_pb2.Area, _Mapping]]] = ..., **kwargs) -> None: ...

class FilterConditions(_message.Message):
    __slots__ = ("filter_type", "type", "filter")
    FILTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    filter_type: str
    type: str
    filter: str
    def __init__(self, filter_type: _Optional[str] = ..., type: _Optional[str] = ..., filter: _Optional[str] = ...) -> None: ...

class FilterScope(_message.Message):
    __slots__ = ("filter_type", "operator", "conditions", "filter", "date_from", "date_to", "type")
    FILTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    DATE_FROM_FIELD_NUMBER: _ClassVar[int]
    DATE_TO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    filter_type: str
    operator: str
    conditions: _containers.RepeatedCompositeFieldContainer[FilterConditions]
    filter: str
    date_from: str
    date_to: str
    type: str
    def __init__(self, filter_type: _Optional[str] = ..., operator: _Optional[str] = ..., conditions: _Optional[_Iterable[_Union[FilterConditions, _Mapping]]] = ..., filter: _Optional[str] = ..., date_from: _Optional[str] = ..., date_to: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...
