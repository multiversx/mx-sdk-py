from typing import Optional, Protocol, Sequence


class IAddress(Protocol):
    def to_bech32(self) -> str:
        ...

    def to_hex(self) -> str:
        ...


class ITransaction(Protocol):
    sender: str
    receiver: str
    gas_limit: int
    chain_id: str
    nonce: int
    value: int
    sender_username: str
    receiver_username: str
    gas_price: int
    data: bytes
    version: int
    options: int
    guardian: str
    signature: bytes
    guardian_signature: bytes
    relayer: str

    @property
    def inner_transactions(self) -> Sequence["ITransaction"]:
        ...


class IMessage(Protocol):
    data: bytes
    signature: bytes
    address: Optional[IAddress]
    version: int
    signer: str


INonce = int
IGasPrice = int
IGasLimit = int
IChainID = str
ITransactionVersion = int
ITransactionOptions = int
ISignature = bytes
ITokenIdentifier = str
IGasPerDataByte = int


class ITokenPayment(Protocol):
    token_identifier: ITokenIdentifier
    token_nonce: INonce
    amount_as_integer: int

    def is_egld(self) -> bool:
        ...

    def is_fungible(self) -> bool:
        ...


class ITransactionValue(Protocol):
    def __str__(self) -> str:
        ...


class ITransactionPayload(Protocol):
    data: bytes

    def encoded(self) -> str:
        ...

    def length(self) -> int:
        ...


class ICodeMetadata(Protocol):
    def serialize(self) -> bytes:
        ...


class INetworkConfig(Protocol):
    min_gas_limit: IGasLimit
    gas_per_data_byte: IGasPerDataByte
    gas_price_modifier: float
    chain_id: IChainID


class IValidatorPublicKey(Protocol):
    def hex(self) -> str:
        ...
