from erdpy_core import Address

from erdpy_wallet.interfaces import IAddress, IVerifiable
from erdpy_wallet.user_keys import UserPublicKey


class UserVerifier:
    def __init__(self, public_key: UserPublicKey) -> None:
        self.public_key = public_key

    @classmethod
    def from_address(cls, address: IAddress) -> 'UserVerifier':
        buffer: bytes = Address.from_bech32(address.bech32()).pubkey
        public_key = UserPublicKey(buffer)
        return UserVerifier(public_key)

    def verify(self, message: IVerifiable) -> bool:
        data = message.serialize_for_signing()
        return self.public_key.verify(data, message.signature)
