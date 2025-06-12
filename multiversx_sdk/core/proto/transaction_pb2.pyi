from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Transaction(_message.Message):
    __slots__ = ["ChainID", "Data", "GasLimit", "GasPrice", "GuardAddr", "GuardSignature", "Nonce", "Options", "RcvAddr", "RcvUserName", "Relayer", "RelayerSignature", "Signature", "SndAddr", "SndUserName", "Value", "Version"]
    CHAINID_FIELD_NUMBER: ClassVar[int]
    ChainID: bytes
    DATA_FIELD_NUMBER: ClassVar[int]
    Data: bytes
    GASLIMIT_FIELD_NUMBER: ClassVar[int]
    GASPRICE_FIELD_NUMBER: ClassVar[int]
    GUARDADDR_FIELD_NUMBER: ClassVar[int]
    GUARDSIGNATURE_FIELD_NUMBER: ClassVar[int]
    GasLimit: int
    GasPrice: int
    GuardAddr: bytes
    GuardSignature: bytes
    NONCE_FIELD_NUMBER: ClassVar[int]
    Nonce: int
    OPTIONS_FIELD_NUMBER: ClassVar[int]
    Options: int
    RCVADDR_FIELD_NUMBER: ClassVar[int]
    RCVUSERNAME_FIELD_NUMBER: ClassVar[int]
    RELAYERSIGNATURE_FIELD_NUMBER: ClassVar[int]
    RELAYER_FIELD_NUMBER: ClassVar[int]
    RcvAddr: bytes
    RcvUserName: bytes
    Relayer: bytes
    RelayerSignature: bytes
    SIGNATURE_FIELD_NUMBER: ClassVar[int]
    SNDADDR_FIELD_NUMBER: ClassVar[int]
    SNDUSERNAME_FIELD_NUMBER: ClassVar[int]
    Signature: bytes
    SndAddr: bytes
    SndUserName: bytes
    VALUE_FIELD_NUMBER: ClassVar[int]
    VERSION_FIELD_NUMBER: ClassVar[int]
    Value: bytes
    Version: int
    def __init__(self, Nonce: Optional[int] = ..., Value: Optional[bytes] = ..., RcvAddr: Optional[bytes] = ..., RcvUserName: Optional[bytes] = ..., SndAddr: Optional[bytes] = ..., SndUserName: Optional[bytes] = ..., GasPrice: Optional[int] = ..., GasLimit: Optional[int] = ..., Data: Optional[bytes] = ..., ChainID: Optional[bytes] = ..., Version: Optional[int] = ..., Signature: Optional[bytes] = ..., Options: Optional[int] = ..., GuardAddr: Optional[bytes] = ..., GuardSignature: Optional[bytes] = ..., Relayer: Optional[bytes] = ..., RelayerSignature: Optional[bytes] = ...) -> None: ...
