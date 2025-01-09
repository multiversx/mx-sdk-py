from multiversx_sdk.core.address import Address
from multiversx_sdk.core.message import Message, MessageComputer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.ledger.ledger_app import LedgerApp


class LedgerAccount:
    def __init__(self, address_index: int = 0) -> None:
        self.address_index = address_index
        self.address = self._get_address()
        self.nonce = 0

    def set_address(self, address_index: int = 0):
        """Sets the working address for the device. Also sets the `address_index` and `address` properties of the class."""
        app = LedgerApp()
        app.set_address(address_index)

        self.address_index = address_index
        bech32_address = app.get_address(address_index)
        self.address = Address.new_from_bech32(bech32_address)

        app.close()

    def sign_transaction(self, transaction: Transaction) -> bytes:
        transaction_computer = TransactionComputer()

        if not transaction_computer.has_options_set_for_hash_signing(transaction):
            raise Exception(
                "Invalid transaction options. Set the least significant bit of the `options` property to `1`."
            )

        app = LedgerApp()
        app.set_address(self.address_index)

        hash = transaction_computer.compute_hash_for_signing(transaction)
        signature = app.sign_transaction(hash)

        app.close()
        return bytes.fromhex(signature)

    def sign_message(self, message: Message) -> bytes:
        app = LedgerApp()
        app.set_address(self.address_index)

        message_computer = MessageComputer()
        serialized_message = message_computer.compute_bytes_for_signing(message)
        signature = app.sign_message(serialized_message)
        app.close()

        return bytes.fromhex(signature)

    def get_nonce_then_increment(self) -> int:
        nonce = self.nonce
        self.nonce += 1
        return nonce

    def _get_address(self) -> Address:
        app = LedgerApp()
        address = app.get_address(self.address_index)
        app.close()
        return Address.new_from_bech32(address)
