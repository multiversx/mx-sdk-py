from enum import Enum
from typing import Any, Optional, cast

from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.fields import Field
from multiversx_sdk.abi.interface import ISingleValue
from multiversx_sdk.abi.small_int_values import U64Value
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.abi.struct_value import StructValue
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.config import LibraryConfig


class ProposeTransferExecuteInput:
    def __init__(
        self,
        to: Address,
        native_transfer_amount: int,
        function_call: list[bytes],
        opt_gas_limit: Optional[int] = None,
    ) -> None:
        self.to = to
        self.egld_amount = native_transfer_amount
        self.function_call = function_call
        self.opt_gas_limit = opt_gas_limit


class ProposeTransferExecuteEsdtInput:
    def __init__(
        self,
        to: Address,
        tokens: list["EsdtTokenPayment"],
        function_call: list[bytes],
        opt_gas_limit: Optional[int] = None,
    ) -> None:
        self.to = to
        self.tokens = cast(list[ISingleValue], tokens)
        self.function_call = function_call
        self.opt_gas_limit = opt_gas_limit


class ProposeAsyncCallInput:
    def __init__(
        self,
        to: Address,
        function_call: list[bytes],
        opt_gas_limit: Optional[int] = None,
    ) -> None:
        self.to = to
        self.function_call = function_call
        self.opt_gas_limit = opt_gas_limit or 0


class EsdtTokenPayment(StructValue):
    def __init__(self, token_identifier: str, token_nonce: int, amount: int) -> None:
        super().__init__(
            [
                Field("token_identifier", StringValue(token_identifier)),
                Field("token_nonce", U64Value(token_nonce)),
                Field("amount", BigUIntValue(amount)),
            ],
        )


class UserRole(Enum):
    NONE = 0
    PROPOSER = 1
    BOARD_MEMBER = 2


class ActionFullInfo:
    def __init__(self, action_id: int, group_id: int, action_data: "Action", signers: list[Address]) -> None:
        self.action_id = action_id
        self.group_id = group_id
        self.action_data = action_data
        self.signers = signers

    @classmethod
    def new_from_object(cls, object: Any) -> "ActionFullInfo":
        signers = [Address(value, LibraryConfig.default_address_hrp) for value in object.signers]
        action_data = create_action_from_object(object.action_data)
        return cls(object.action_id, object.group_id, action_data, signers)

    def __repr__(self) -> str:
        return f"ActionFullInfo(action_id={self.action_id}, group_id={self.group_id}, action_data={self.action_data}, signers={self.signers})"


def create_action_from_object(object: Any) -> "Action":
    discriminant = int(object)

    if discriminant == AddBoardMember.discriminant:
        return AddBoardMember.new_from_object(object)
    elif discriminant == AddProposer.discriminant:
        return AddProposer.new_from_object(object)
    elif discriminant == RemoveUser.discriminant:
        return RemoveUser.new_from_object(object)
    elif discriminant == ChangeQuorum.discriminant:
        return ChangeQuorum.new_from_object(object)
    elif discriminant == SendTransferExecuteEgld.discriminant:
        return SendTransferExecuteEgld.new_from_object(object)
    elif discriminant == SendTransferExecuteEsdt.discriminant:
        return SendTransferExecuteEsdt.new_from_object(object)
    elif discriminant == SendAsyncCall.discriminant:
        return SendAsyncCall.new_from_object(object)
    elif discriminant == SCDeployFromSource.discriminant:
        return SCDeployFromSource.new_from_object(object)
    elif discriminant == SCUpgradeFromSource.discriminant:
        return SCUpgradeFromSource.new_from_object(object)
    else:
        raise ValueError(f"Unknown action discriminant: {discriminant}")


class Action:
    discriminant: int

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__

    def __int__(self) -> int:
        return self.discriminant


class AddBoardMember(Action):
    discriminant = 1

    def __init__(self, address: Address) -> None:
        self.address = address

    @classmethod
    def new_from_object(cls, object: Any) -> "AddBoardMember":
        field_0 = getattr(object, "0")
        public_key = field_0
        address = Address(public_key, LibraryConfig.default_address_hrp)
        return cls(address)


class AddProposer(Action):
    discriminant = 2

    def __init__(self, address: Address) -> None:
        self.address = address

    @classmethod
    def new_from_object(cls, object: Any) -> "AddProposer":
        field_0 = getattr(object, "0")
        public_key = field_0
        address = Address(public_key, LibraryConfig.default_address_hrp)
        return cls(address)


class RemoveUser(Action):
    discriminant = 3

    def __init__(self, address: Address) -> None:
        self.address = address

    @classmethod
    def new_from_object(cls, object: Any) -> "RemoveUser":
        field_0 = getattr(object, "0")
        public_key = field_0
        address = Address(public_key, LibraryConfig.default_address_hrp)
        return cls(address)


class ChangeQuorum(Action):
    discriminant = 4

    def __init__(self, quorum: int) -> None:
        self.quorum = quorum

    @classmethod
    def new_from_object(cls, object: Any) -> "ChangeQuorum":
        field_0 = getattr(object, "0")
        quorum = field_0
        return cls(quorum)


class SendTransferExecuteEgld(Action):
    discriminant = 5

    def __init__(self, data: "CallActionData") -> None:
        self.data = data

    @classmethod
    def new_from_object(cls, object: Any) -> "SendTransferExecuteEgld":
        field_0 = getattr(object, "0")
        data = CallActionData.new_from_object(field_0)
        return cls(data)


class CallActionData:
    def __init__(
        self,
        to: Address,
        egld_amount: int,
        endpoint_name: str,
        arguments: list[bytes],
        opt_gas_limit: Optional[int] = None,
    ):
        self.to = to
        self.egld_amount = egld_amount
        self.endpoint_name = endpoint_name
        self.arguments = arguments
        self.opt_gas_limit = opt_gas_limit

    @classmethod
    def new_from_object(cls, object: Any) -> "CallActionData":
        to = Address(object.to, LibraryConfig.default_address_hrp)
        egld_amount = object.egld_amount
        endpoint_name = object.endpoint_name.decode()
        arguments = object.arguments
        opt_gas_limit = object.opt_gas_limit
        return cls(to, egld_amount, endpoint_name, arguments, opt_gas_limit)


class SendTransferExecuteEsdt(Action):
    discriminant = 6

    def __init__(self, data: "EsdtTransferExecuteData") -> None:
        self.data = data

    @classmethod
    def new_from_object(cls, object: Any) -> "SendTransferExecuteEsdt":
        field_0 = getattr(object, "0")
        data = EsdtTransferExecuteData.new_from_object(field_0)
        return cls(data)


class EsdtTransferExecuteData:
    def __init__(
        self,
        to: Address,
        tokens: list[EsdtTokenPayment],
        opt_gas_limit: Optional[int],
        endpoint_name: str,
        arguments: list[bytes],
    ) -> None:
        self.to = to
        self.tokens = tokens
        self.opt_gas_limit = opt_gas_limit
        self.endpoint_name = endpoint_name
        self.arguments = arguments

    @classmethod
    def new_from_object(cls, object: Any) -> "EsdtTransferExecuteData":
        to = Address(object.to, LibraryConfig.default_address_hrp)
        tokens = [EsdtTokenPayment(token.token_identifier, token.token_nonce, token.amount) for token in object.tokens]
        opt_gas_limit = object.opt_gas_limit
        endpoint_name = bytes.fromhex(object.endpoint_name.decode()).decode()
        arguments = object.arguments
        return cls(to, tokens, opt_gas_limit, endpoint_name, arguments)


class SendAsyncCall(Action):
    discriminant = 7

    def __init__(self, data: "CallActionData") -> None:
        self.data = data

    @classmethod
    def new_from_object(cls, object: Any) -> "SendAsyncCall":
        field_0 = getattr(object, "0")
        data = CallActionData.new_from_object(field_0)
        return cls(data)


class SCDeployFromSource(Action):
    discriminant = 8

    def __init__(self, amount: int, source: Address, code_metadata: bytes, arguments: list[bytes]) -> None:
        self.amount = amount
        self.source = source
        self.code_metadata = code_metadata
        self.arguments = arguments

    @classmethod
    def new_from_object(cls, object: Any) -> "SCDeployFromSource":
        amount = object.amount
        source = Address(object.source, LibraryConfig.default_address_hrp)
        code_metadata = object.code_metadata
        arguments = object.arguments
        return cls(amount, source, code_metadata, arguments)


class SCUpgradeFromSource(Action):
    discriminant = 9

    def __init__(
        self, sc_address: Address, amount: int, source: Address, code_metadata: bytes, arguments: list[bytes]
    ) -> None:
        self.sc_address = sc_address
        self.amount = amount
        self.source = source
        self.code_metadata = code_metadata
        self.arguments = arguments

    @classmethod
    def new_from_object(cls, object: Any) -> "SCUpgradeFromSource":
        sc_address = Address(object.sc_address, LibraryConfig.default_address_hrp)
        amount = object.amount
        source = Address(object.source, LibraryConfig.default_address_hrp)
        code_metadata = object.code_metadata
        arguments = object.arguments
        return cls(sc_address, amount, source, code_metadata, arguments)
