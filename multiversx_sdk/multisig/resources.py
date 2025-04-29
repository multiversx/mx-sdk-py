from typing import Optional, cast

from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.fields import Field
from multiversx_sdk.abi.interface import ISingleValue
from multiversx_sdk.abi.small_int_values import U64Value
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.abi.struct_value import StructValue
from multiversx_sdk.core.address import Address


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


class Action:
    discriminant: int

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__
