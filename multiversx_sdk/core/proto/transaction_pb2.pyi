from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Transaction(_message.Message):
    __slots__ = ["ChainID", "Data", "GasLimit", "GasPrice", "GuardAddr", "GuardSignature", "Nonce", "Options", "RcvAddr", "RcvUserName", "Relayer", "RelayerSignature", "Signature", "SndAddr", "SndUserName", "Value", "Version"]
    CHAINID_FIELD_NUMBER: _ClassVar[int]
    ChainID: bytes
    DATA_FIELD_NUMBER: _ClassVar[int]
    Data: bytes
    GASLIMIT_FIELD_NUMBER: _ClassVar[int]
    GASPRICE_FIELD_NUMBER: _ClassVar[int]
    GUARDADDR_FIELD_NUMBER: _ClassVar[int]
    GUARDSIGNATURE_FIELD_NUMBER: _ClassVar[int]
    GasLimit: int
    GasPrice: int
    GuardAddr: bytes
    GuardSignature: bytes
    NONCE_FIELD_NUMBER: _ClassVar[int]
    Nonce: int
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    Options: int
    RCVADDR_FIELD_NUMBER: _ClassVar[int]
    RCVUSERNAME_FIELD_NUMBER: _ClassVar[int]
    RELAYERSIGNATURE_FIELD_NUMBER: _ClassVar[int]
    RELAYER_FIELD_NUMBER: _ClassVar[int]
    RcvAddr: bytes
    RcvUserName: bytes
    Relayer: bytes
    RelayerSignature: bytes
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    SNDADDR_FIELD_NUMBER: _ClassVar[int]
    SNDUSERNAME_FIELD_NUMBER: _ClassVar[int]
    Signature: bytes
    SndAddr: bytes
    SndUserName: bytes
    VALUE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    Value: bytes
    Version: int
    def __init__(self, Nonce: _Optional[int] = ..., Value: _Optional[bytes] = ..., RcvAddr: _Optional[bytes] = ..., RcvUserName: _Optional[bytes] = ..., SndAddr: _Optional[bytes] = ..., SndUserName: _Optional[bytes] = ..., GasPrice: _Optional[int] = ..., GasLimit: _Optional[int] = ..., Data: _Optional[bytes] = ..., ChainID: _Optional[bytes] = ..., Version: _Optional[int] = ..., Signature: _Optional[bytes] = ..., Options: _Optional[int] = ..., GuardAddr: _Optional[bytes] = ..., GuardSignature: _Optional[bytes] = ..., Relayer: _Optional[bytes] = ..., RelayerSignature: _Optional[bytes] = ...) -> None: ...
