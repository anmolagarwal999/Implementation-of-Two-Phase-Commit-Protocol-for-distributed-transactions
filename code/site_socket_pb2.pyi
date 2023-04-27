from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BoolMessage(_message.Message):
    __slots__ = ["val"]
    VAL_FIELD_NUMBER: _ClassVar[int]
    val: bool
    def __init__(self, val: bool = ...) -> None: ...

class GlobalVerdictMessage(_message.Message):
    __slots__ = ["global_verdict", "txn_id"]
    class GLOBAL_VERDICT_ENUM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    GLOBAL_ABORT: GlobalVerdictMessage.GLOBAL_VERDICT_ENUM
    GLOBAL_COMMIT: GlobalVerdictMessage.GLOBAL_VERDICT_ENUM
    GLOBAL_VERDICT_FIELD_NUMBER: _ClassVar[int]
    TXN_ID_FIELD_NUMBER: _ClassVar[int]
    global_verdict: GlobalVerdictMessage.GLOBAL_VERDICT_ENUM
    txn_id: str
    def __init__(self, txn_id: _Optional[str] = ..., global_verdict: _Optional[_Union[GlobalVerdictMessage.GLOBAL_VERDICT_ENUM, str]] = ...) -> None: ...

class PersonOrders(_message.Message):
    __slots__ = ["PersonName", "items_ordered"]
    ITEMS_ORDERED_FIELD_NUMBER: _ClassVar[int]
    PERSONNAME_FIELD_NUMBER: _ClassVar[int]
    PersonName: str
    items_ordered: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, PersonName: _Optional[str] = ..., items_ordered: _Optional[_Iterable[int]] = ...) -> None: ...

class TxnGlobalMessage(_message.Message):
    __slots__ = ["txn_json"]
    TXN_JSON_FIELD_NUMBER: _ClassVar[int]
    txn_json: str
    def __init__(self, txn_json: _Optional[str] = ...) -> None: ...

class TxnIDMessage(_message.Message):
    __slots__ = ["txn_id"]
    TXN_ID_FIELD_NUMBER: _ClassVar[int]
    txn_id: str
    def __init__(self, txn_id: _Optional[str] = ...) -> None: ...

class TxnLocalDetails(_message.Message):
    __slots__ = ["num_people_involved", "other_sites_involved", "people_order_details", "txn_id"]
    NUM_PEOPLE_INVOLVED_FIELD_NUMBER: _ClassVar[int]
    OTHER_SITES_INVOLVED_FIELD_NUMBER: _ClassVar[int]
    PEOPLE_ORDER_DETAILS_FIELD_NUMBER: _ClassVar[int]
    TXN_ID_FIELD_NUMBER: _ClassVar[int]
    num_people_involved: int
    other_sites_involved: _containers.RepeatedScalarFieldContainer[int]
    people_order_details: _containers.RepeatedCompositeFieldContainer[PersonOrders]
    txn_id: str
    def __init__(self, txn_id: _Optional[str] = ..., num_people_involved: _Optional[int] = ..., people_order_details: _Optional[_Iterable[_Union[PersonOrders, _Mapping]]] = ..., other_sites_involved: _Optional[_Iterable[int]] = ...) -> None: ...

class VerdictMessage(_message.Message):
    __slots__ = ["global_verdict_recv", "have_sent_local_verdict", "local_verdict"]
    class VERDICT_ENUM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class VERDICT_ENUM_GLOBAL(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    ABORT: VerdictMessage.VERDICT_ENUM
    COMMIT: VerdictMessage.VERDICT_ENUM
    GLOBAL_ABORT: VerdictMessage.VERDICT_ENUM_GLOBAL
    GLOBAL_COMMIT: VerdictMessage.VERDICT_ENUM_GLOBAL
    GLOBAL_UNDECIDED: VerdictMessage.VERDICT_ENUM_GLOBAL
    GLOBAL_VERDICT_RECV_FIELD_NUMBER: _ClassVar[int]
    HAVE_SENT_LOCAL_VERDICT_FIELD_NUMBER: _ClassVar[int]
    LOCAL_VERDICT_FIELD_NUMBER: _ClassVar[int]
    UNDECIDED: VerdictMessage.VERDICT_ENUM
    global_verdict_recv: VerdictMessage.VERDICT_ENUM_GLOBAL
    have_sent_local_verdict: bool
    local_verdict: VerdictMessage.VERDICT_ENUM
    def __init__(self, local_verdict: _Optional[_Union[VerdictMessage.VERDICT_ENUM, str]] = ..., have_sent_local_verdict: bool = ..., global_verdict_recv: _Optional[_Union[VerdictMessage.VERDICT_ENUM_GLOBAL, str]] = ...) -> None: ...
