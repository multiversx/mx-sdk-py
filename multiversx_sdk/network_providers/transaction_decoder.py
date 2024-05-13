import binascii
from typing import Any, Dict, List, Optional, Protocol

from multiversx_sdk.core import TokenTransfer
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.tokens import Token
from multiversx_sdk.network_providers.interface import IAddress

DEFAULT_HRP = "erd"


class ITransactionToDecode(Protocol):
    sender: IAddress
    receiver: IAddress
    data: str
    value: int


class TransactionMetadata:
    def __init__(self) -> None:
        self.sender: str = ""
        self.receiver: str = ""
        self.value: int = 0
        self.function_name: Optional[str] = None
        self.function_args: Optional[List[str]] = None
        self.transfers: Optional[List[TokenTransfer]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "value": self.value,
            "function_name": self.function_name if self.function_name else "",
            "function_args": self.function_args if self.function_args else [],
            "transfers": self._transfers_to_dict()
        }

    def _transfers_to_dict(self) -> List[Dict[str, Any]]:
        if self.transfers:
            if not len(self.transfers):
                return []

            transfers: List[Dict[str, Any]] = []

            for transfer in self.transfers:
                transfers.append({
                    "value": transfer.amount,
                    "token": transfer.token.identifier,
                    "nonce": transfer.token.nonce
                })

            return transfers

        return []


class TransactionDecoder:
    def get_transaction_metadata(self, transaction: ITransactionToDecode) -> TransactionMetadata:
        metadata = self.get_normal_transaction_metadata(transaction)

        esdt_metadata = self.get_esdt_transaction_metadata(metadata)
        if esdt_metadata:
            return esdt_metadata

        nft_metadata = self.get_nft_transfer_metadata(metadata)
        if nft_metadata:
            return nft_metadata

        multi_metadata = self.get_multi_transfer_metadata(metadata)
        if multi_metadata:
            return multi_metadata

        return metadata

    def get_normal_transaction_metadata(self, transaction: ITransactionToDecode) -> TransactionMetadata:
        metadata = TransactionMetadata()
        metadata.sender = transaction.sender.to_bech32()
        metadata.receiver = transaction.receiver.to_bech32()
        metadata.value = transaction.value

        if transaction.data:
            data_components = transaction.data.split("@")

            args = data_components[1:]
            if all(self.is_smart_contract_call_argument(x) for x in args):
                metadata.function_name = data_components[0]
                metadata.function_args = args

        return metadata

    def get_esdt_transaction_metadata(self, metadata: TransactionMetadata) -> Optional[TransactionMetadata]:
        if metadata.function_name != "ESDTTransfer":
            return None

        args = metadata.function_args
        if not args:
            return None

        if len(args) < 2:
            return None

        identifier = self.hex_to_string(args[0])
        value = self.hex_to_number(args[1])

        result = TransactionMetadata()

        result.sender = metadata.sender
        result.receiver = metadata.receiver
        result.value = value
        result.transfers = []

        if len(args) > 2:
            result.function_name = self.hex_to_string(args[2])
            result.function_args = args[3:]

        token = Token(identifier)
        transfer = TokenTransfer(token, value)

        result.transfers.append(transfer)
        return result

    def get_nft_transfer_metadata(self, metadata: TransactionMetadata) -> Optional[TransactionMetadata]:
        if metadata.sender != metadata.receiver:
            return None

        if metadata.function_name != "ESDTNFTTransfer":
            return None

        args = metadata.function_args
        if not args:
            return None

        if len(args) < 4:
            return None

        if not self.is_address_valid(args[3]):
            return None

        collection_identifier = self.hex_to_string(args[0])
        nonce = args[1]
        value = self.hex_to_number(args[2])
        receiver = Address.new_from_hex(args[3], DEFAULT_HRP)

        result = TransactionMetadata()
        result.sender = metadata.sender
        result.receiver = receiver.to_bech32()
        result.value = value
        result.transfers = []

        if len(args) > 4:
            result.function_name = self.hex_to_string(args[4])
            result.function_args = args[5:]

        token = Token(collection_identifier, self.hex_to_number(nonce))
        transfer = TokenTransfer(token, value)
        result.transfers.append(transfer)

        return result

    def get_multi_transfer_metadata(self, metadata: TransactionMetadata) -> Optional[TransactionMetadata]:
        if metadata.sender != metadata.receiver:
            return None

        if metadata.function_name != "MultiESDTNFTTransfer":
            return None

        args = metadata.function_args
        if not args:
            return None

        if len(args) < 3:
            return None

        if not self.is_address_valid(args[0]):
            return None

        receiver = Address.new_from_hex(args[0], DEFAULT_HRP)
        transfer_count = self.hex_to_number(args[1])

        result = TransactionMetadata()
        if not result.transfers:
            result.transfers = []

        index = 2
        for _ in range(transfer_count):
            identifier = self.hex_to_string(args[index])
            index += 1
            nonce = args[index]
            index += 1
            value = self.hex_to_number(args[index])
            index += 1

            if nonce and self.hex_to_number(nonce) > 0:
                token = Token(identifier, self.hex_to_number(nonce))
                transfer = TokenTransfer(token, value)

                result.transfers.append(transfer)
            else:
                token = Token(identifier)
                transfer = TokenTransfer(token, value)

                result.transfers.append(transfer)

        result.sender = metadata.sender
        result.receiver = receiver.to_bech32()

        if len(args) > index:
            result.function_name = self.hex_to_string(args[index])
            index += 1
            result.function_args = args[index:]
            index += 1

        return result

    def is_address_valid(self, address: str) -> bool:
        return len(binascii.unhexlify(address)) == 32

    def is_smart_contract_call_argument(self, arg: str) -> bool:
        if not self.is_hex(arg):
            return False
        if len(arg) % 2 != 0:
            return False
        return True

    def is_hex(self, value: str) -> bool:
        try:
            bytes.fromhex(value)
            return True
        except ValueError:
            return False

    def hex_to_string(self, hex: str) -> str:
        return bytes.fromhex(hex).decode("ascii")

    def hex_to_number(self, hex: str) -> int:
        return int(hex or "00", 16)
