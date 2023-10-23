from typing import List

from multiversx_sdk_core.codec import decode_unsigned_number
from multiversx_sdk_core.constants import TOKEN_RANDOM_SEQUENCE_LENGTH
from multiversx_sdk_core.errors import InvalidTokenIdentifierError


class Token:
    def __init__(self, identifier: str = "", nonce: int = 0) -> None:
        self.identifier = identifier
        self.nonce = nonce


class TokenTransfer:
    def __init__(self, token: Token, amount: int) -> None:
        """`amount` should always be in atomic units: 1.000000 "USDC-c76f1f" = "1000000"""
        self.token = token
        self.amount = amount


# the rest of the methods will be implemented in a future PR
class TokenComputer:
    def __init__(self) -> None:
        pass

    def is_fungible(self, token: Token) -> bool:
        return token.nonce == 0

    def extract_nonce_from_extended_identifier(self, identifier: str) -> int:
        parts = identifier.split("-")

        self._check_if_extended_identifier_was_provided(parts)
        self._check_lenght_of_random_sequence(parts[1])

        hex_nonce = bytes.fromhex(parts[2])
        return decode_unsigned_number(hex_nonce)

    def extract_identifier_from_extended_identifier(self, identifier: str) -> str:
        parts = identifier.split("-")

        self._check_if_extended_identifier_was_provided(parts)
        self._check_lenght_of_random_sequence(parts[1])

        return parts[0] + "-" + parts[1]

    def _check_if_extended_identifier_was_provided(self, token_parts: List[str]) -> None:
        EXTENDED_IDENTIFIER_LENGTH_IF_SPLITTED = 3

        if len(token_parts) != EXTENDED_IDENTIFIER_LENGTH_IF_SPLITTED:
            raise InvalidTokenIdentifierError("You have not provided the extended identifier")

    def _check_lenght_of_random_sequence(self, random_sequence: str) -> None:
        if len(random_sequence) != TOKEN_RANDOM_SEQUENCE_LENGTH:
            raise InvalidTokenIdentifierError("The identifier is not valid. The random sequence does not have the right length")

    def ensure_identifier_has_correct_structure(self, identifier: str) -> str:
        if identifier.count("-") == 1:
            self._check_lenght_of_random_sequence(identifier.split("-")[1])
            return identifier

        return self.extract_identifier_from_extended_identifier(identifier)
