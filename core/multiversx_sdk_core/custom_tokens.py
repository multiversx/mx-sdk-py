from multiversx_sdk_core.codec import decode_unsigned_number
from multiversx_sdk_core.errors import InvalidTokenIdentifierError


class Token:
    def __init__(self, identifier: str = "", nonce: int = 0) -> None:
        self.identifier = identifier
        self.nonce = nonce


class TokenTransfer:
    def __init__(self, token: Token, amount: int) -> None:
        """`amount` should always be in atomic units: 1 EGLD = 1000000000000000000"""
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

        if len(parts) != 3:
            raise InvalidTokenIdentifierError("You have not provided the extended identifier")

        # check length of random sequence
        if len(parts[1]) != 6:
            raise InvalidTokenIdentifierError("The identifier is not valid. The random sequence does not have the right length")

        hex_nonce = bytes.fromhex(parts[2])
        return decode_unsigned_number(hex_nonce)

    def extract_identifier_from_extended_identifier(self, identifier: str) -> str:
        parts = identifier.split("-")

        if len(parts) != 3:
            raise InvalidTokenIdentifierError("You have not provided the extended identifier")

        # check length of random sequence
        if len(parts[1]) != 6:
            raise InvalidTokenIdentifierError("The identifier is not valid. The random sequence does not have the right length")

        return parts[0] + "-" + parts[1]
