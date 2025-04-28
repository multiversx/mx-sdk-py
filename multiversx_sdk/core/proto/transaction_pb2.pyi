from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Transaction(_message.Message):
    __slots__ = ("Nonce", "Value", "RcvAddr", "RcvUserName", "SndAddr", "SndUserName", "GasPrice", "GasLimit", "Data", "ChainID", "Version", "Signature", "Options", "GuardAddr", "GuardSignature", "Relayer", "RelayerSignature")
    NONCE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    RCVADDR_FIELD_NUMBER: _ClassVar[int]
    RCVUSERNAME_FIELD_NUMBER: _ClassVar[int]
    SNDADDR_FIELD_NUMBER: _ClassVar[int]
    SNDUSERNAME_FIELD_NUMBER: _ClassVar[int]
    GASPRICE_FIELD_NUMBER: _ClassVar[int]
    GASLIMIT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CHAINID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    GUARDADDR_FIELD_NUMBER: _ClassVar[int]
    GUARDSIGNATURE_FIELD_NUMBER: _ClassVar[int]
    RELAYER_FIELD_NUMBER: _ClassVar[int]
    RELAYERSIGNATURE_FIELD_NUMBER: _ClassVar[int]
    Nonce: int
    Value: bytes
    RcvAddr: bytes
    RcvUserName: bytes
    SndAddr: bytes
    SndUserName: bytes
    GasPrice: int
    GasLimit: int
    Data: bytes
    ChainID: bytes
    Version: int
    Signature: bytes
    Options: int
    GuardAddr: bytes
    GuardSignature: bytes
    Relayer: bytes
    RelayerSignature: bytes
    def __init__(self, Nonce: _Optional[int] = ..., Value: _Optional[bytes] = ..., RcvAddr: _Optional[bytes] = ..., RcvUserName: _Optional[bytes] = ..., SndAddr: _Optional[bytes] = ..., SndUserName: _Optional[bytes] = ..., GasPrice: _Optional[int] = ..., GasLimit: _Optional[int] = ..., Data: _Optional[bytes] = ..., ChainID: _Optional[bytes] = ..., Version: _Optional[int] = ..., Signature: _Optional[bytes] = ..., Options: _Optional[int] = ..., GuardAddr: _Optional[bytes] = ..., GuardSignature: _Optional[bytes] = ..., Relayer: _Optional[bytes] = ..., RelayerSignature: _Optional[bytes] = ...) -> None: ...
