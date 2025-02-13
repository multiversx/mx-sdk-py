from typing import Any, Union

from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.core.constants import (
    EGLD_IDENTIFIER_FOR_MULTI_ESDTNFT_TRANSFER,
    TOKEN_RANDOM_SEQUENCE_LENGTH,
)
from multiversx_sdk.core.errors import BadUsageError, InvalidTokenIdentifierError


class Token:
    def __init__(self, identifier: str, nonce: int = 0) -> None:
        self.identifier = identifier
        self.nonce = nonce

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Token):
            return False
        return self.identifier == other.identifier and self.nonce == other.nonce

    def __str__(self) -> str:
        return TokenComputer().compute_extended_identifier(self)


class TokenTransfer:
    def __init__(self, token: Token, amount: int) -> None:
        """`amount` should always be in atomic units: 1.000000 "USDC-c76f1f" = "1000000"""
        self.token = token
        self.amount = amount

    @staticmethod
    def new_from_native_amount(amount: int) -> "TokenTransfer":
        native_token = Token(EGLD_IDENTIFIER_FOR_MULTI_ESDTNFT_TRANSFER)
        return TokenTransfer(native_token, amount)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TokenTransfer):
            return False
        return self.token == other.token and self.amount == other.amount

    def __str__(self) -> str:
        return f"{self.amount} {self.token}"


class TokenIdentifierParts:
    def __init__(
        self,
        ticker: str,
        random_sequence: str,
        nonce: int,
        prefix: Union[str, None] = None,
    ) -> None:
        self.ticker = ticker
        self.random_sequence = random_sequence
        self.nonce = nonce
        self.prefix = prefix


class TokenComputer:
    def __init__(self) -> None:
        self._serializer = Serializer()

    def is_fungible(self, token: Token) -> bool:
        return token.nonce == 0

    def extract_nonce_from_extended_identifier(self, identifier: str) -> int:
        parts = identifier.split("-")
        prefix, ticker, random_sequence = self._split_identifier_into_components(parts)
        self._validate_extended_identifier(prefix, ticker, random_sequence, parts)

        # in case the identifier of a fungible token is provided (2 parts or 3 with prefix), return 0
        if len(parts) == 2 or (prefix and len(parts) == 3):
            return 0

        # else, the last part is the nonce
        nonce_value = BigUIntValue()
        self._serializer.deserialize(parts[-1], [nonce_value])
        return nonce_value.get_payload()

    def _split_identifier_into_components(self, token_parts: list[str]) -> tuple[Union[str, None], str, str]:
        """
        The first element is the prefix, can be 'str' or None.
        The second element is the ticker.
        The third element is the random sequence.
        """

        if len(token_parts) >= 3 and len(token_parts[2]) == TOKEN_RANDOM_SEQUENCE_LENGTH:
            return token_parts[0], token_parts[1], token_parts[2]
        return None, token_parts[0], token_parts[1]

    def _validate_extended_identifier(
        self,
        prefix: Union[str, None],
        ticker: str,
        random_sequence: str,
        parts: list[str],
    ) -> None:
        self._check_if_extended_identifier_was_provided(prefix, parts)
        self._ensure_token_prefix_validity(prefix)
        self._ensure_token_ticker_validity(ticker)
        self._check_length_of_random_sequence(random_sequence)

    def extract_identifier_from_extended_identifier(self, identifier: str) -> str:
        parts = identifier.split("-")
        prefix, ticker, random_sequence = self._split_identifier_into_components(parts)
        self._validate_extended_identifier(prefix, ticker, random_sequence, parts)

        if prefix:
            return f"{prefix}-{ticker}-{random_sequence}"
        return f"{ticker}-{random_sequence}"

    def extract_ticker_from_identifier(self, identifier: str) -> str:
        parts = identifier.split("-")
        prefix, ticker, random_sequence = self._split_identifier_into_components(parts)
        self._validate_extended_identifier(prefix, ticker, random_sequence, parts)

        return ticker

    def parse_extended_identifier_parts(self, identifier: str) -> TokenIdentifierParts:
        parts = identifier.split("-")
        prefix, ticker, random_sequence = self._split_identifier_into_components(parts)
        self._validate_extended_identifier(prefix, ticker, random_sequence, parts)

        nonce = self.extract_nonce_from_extended_identifier(identifier)

        return TokenIdentifierParts(ticker, random_sequence, nonce, prefix)

    def compute_extended_identifier_from_identifier_and_nonce(self, identifier: str, nonce: int) -> str:
        parts = identifier.split("-")
        prefix, ticker, random_sequence = self._split_identifier_into_components(parts)
        self._validate_extended_identifier(prefix, ticker, random_sequence, parts)

        if nonce < 0:
            raise BadUsageError("The token nonce can't be less than 0")

        if nonce == 0:
            return identifier

        nonce_hex = self._serializer.serialize([BigUIntValue(nonce)])
        return f"{identifier}-{nonce_hex}"

    def compute_extended_identifier_from_parts(self, parts: TokenIdentifierParts) -> str:
        if parts.prefix:
            identifier = f"{parts.prefix}-{parts.ticker}-{parts.random_sequence}"
        else:
            identifier = f"{parts.ticker}-{parts.random_sequence}"

        return self.compute_extended_identifier_from_identifier_and_nonce(identifier, parts.nonce)

    def compute_extended_identifier(self, token: Token) -> str:
        parts = token.identifier.split("-")
        prefix, ticker, random_sequence = self._split_identifier_into_components(parts)
        self._validate_extended_identifier(prefix, ticker, random_sequence, parts)

        if token.nonce < 0:
            raise BadUsageError("The token nonce can't be less than 0")

        if token.nonce == 0:
            return token.identifier

        nonce_as_hex = self._serializer.serialize([BigUIntValue(token.nonce)])
        return f"{token.identifier}-{nonce_as_hex}"

    def _check_if_extended_identifier_was_provided(self, token_prefx: Union[str, None], token_parts: list[str]) -> None:
        # this is for the identifiers of fungible tokens
        MIN_EXTENDED_IDENTIFIER_LENGTH_IF_SPLIT = 2
        # this is for the identifiers of nft, sft and meta-esdt
        MAX_EXTENDED_IDENTIFIER_LENGTH_IF_SPLIT = 3 if not token_prefx else 4

        if (
            len(token_parts) < MIN_EXTENDED_IDENTIFIER_LENGTH_IF_SPLIT
            or len(token_parts) > MAX_EXTENDED_IDENTIFIER_LENGTH_IF_SPLIT
        ):
            raise InvalidTokenIdentifierError("Invalid extended token identifier provided")

    def _ensure_token_ticker_validity(self, ticker: str) -> None:
        MIN_TICKER_LENGTH = 3
        MAX_TICKER_LENGTH = 10

        if len(ticker) < MIN_TICKER_LENGTH or len(ticker) > MAX_TICKER_LENGTH:
            raise InvalidTokenIdentifierError(
                f"The token ticker should be between {MIN_TICKER_LENGTH} and {MAX_TICKER_LENGTH} characters"
            )

        if not ticker.isalnum():
            raise InvalidTokenIdentifierError("The token ticker should only contain alphanumeric characters")

    def _check_length_of_random_sequence(self, random_sequence: str) -> None:
        if len(random_sequence) != TOKEN_RANDOM_SEQUENCE_LENGTH:
            raise InvalidTokenIdentifierError(
                "The identifier is not valid. The random sequence does not have the right length"
            )

    def _ensure_token_prefix_validity(self, prefix: Union[str, None]) -> None:
        MIN_TOKEN_PREFIX_LENGTH = 1
        MAX_TOKEN_PREFIX_LENGTH = 4

        if prefix is None:
            return

        if len(prefix) < MIN_TOKEN_PREFIX_LENGTH or len(prefix) > MAX_TOKEN_PREFIX_LENGTH:
            raise Exception("Token prefix is invalid, it does not have the right length")
