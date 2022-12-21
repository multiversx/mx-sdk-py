from decimal import ROUND_DOWN, Context, Decimal, localcontext
from typing import Union

from erdpy_core.constants import EGLD_NUM_DECIMALS, EGLD_TOKEN_IDENTIFIER
from erdpy_core.interfaces import INonce, ITokenIdentifier


class TokenPayment:
    def __init__(self, token_identifier: ITokenIdentifier, token_nonce: INonce, amount_as_integer: int, num_decimals: int) -> None:
        self.token_identifier: ITokenIdentifier = token_identifier
        self.token_nonce: INonce = token_nonce
        self.amount_as_integer: int = amount_as_integer
        self.num_decimals = num_decimals

    def is_egld(self):
        return self.token_identifier == EGLD_TOKEN_IDENTIFIER

    def is_fungible(self):
        return self.token_nonce == 0

    @classmethod
    def egld_from_amount(cls, amount: Union[Decimal, str, int]) -> 'TokenPayment':
        amount = Decimal(amount)
        amount_as_integer = cls._amount_to_integer(amount, EGLD_NUM_DECIMALS)
        return cls.egld_from_integer(amount_as_integer)

    @classmethod
    def egld_from_integer(cls, amount_as_integer: int) -> 'TokenPayment':
        return cls(EGLD_TOKEN_IDENTIFIER, 0, amount_as_integer, EGLD_NUM_DECIMALS)

    @classmethod
    def fungible_from_amount(cls, token_identifier: ITokenIdentifier, amount: Union[Decimal, str, int], num_decimals: int) -> 'TokenPayment':
        amount = Decimal(amount)
        amount_as_integer = cls._amount_to_integer(amount, num_decimals)
        return cls.fungible_from_integer(token_identifier, amount_as_integer, num_decimals)

    @classmethod
    def fungible_from_integer(cls, token_identifier: ITokenIdentifier, amount_as_integer: int, num_decimals: int) -> 'TokenPayment':
        return cls(token_identifier, 0, amount_as_integer, num_decimals)

    @classmethod
    def non_fungible(cls, token_identifier: ITokenIdentifier, nonce: INonce) -> 'TokenPayment':
        return cls(token_identifier, nonce, 1, 0)

    @classmethod
    def semi_fungible(cls, token_identifier: ITokenIdentifier, nonce: INonce, quantity: int) -> 'TokenPayment':
        return cls(token_identifier, nonce, quantity, 0)

    @classmethod
    def meta_esdt_from_amount(cls, token_identifier: ITokenIdentifier, nonce: int, amount: Union[Decimal, str, int], num_decimals: int) -> 'TokenPayment':
        amount = Decimal(amount)
        amount_as_integer = cls._amount_to_integer(amount, num_decimals)
        return cls.meta_esdt_from_integer(token_identifier, nonce, amount_as_integer, num_decimals)

    @classmethod
    def meta_esdt_from_integer(cls, token_identifier: ITokenIdentifier, nonce: int, amount_as_integer: int, num_decimals: int) -> 'TokenPayment':
        return cls(token_identifier, nonce, amount_as_integer, num_decimals)

    def to_amount_string(self, normalize: bool = False) -> str:
        with localcontext() as ctx:
            self._adjust_decimal_context(ctx)
            amount = Decimal(self.amount_as_integer).scaleb(-self.num_decimals)

            if normalize:
                amount = amount.normalize()

            return f"{amount:f}"

    @classmethod
    def _amount_to_integer(cls, amount: Decimal, num_decimals: int) -> int:
        with localcontext() as ctx:
            cls._adjust_decimal_context(ctx)
            amount_as_integer = int(amount.scaleb(num_decimals))
            return amount_as_integer

    @ classmethod
    def _adjust_decimal_context(cls, context: Context):
        context.prec = 128
        context.rounding = ROUND_DOWN

    def __str__(self) -> str:
        return str(self.amount_as_integer)

    def __repr__(self) -> str:
        return str(self.amount_as_integer)
