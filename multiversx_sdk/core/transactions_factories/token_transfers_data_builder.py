from typing import List, Protocol

from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.serializer import arg_to_string, args_to_strings
from multiversx_sdk.core.tokens import TokenTransfer


class ITokenComputer(Protocol):
    def extract_identifier_from_extended_identifier(self, identifier: str) -> str:
        ...


class TokenTransfersDataBuilder:
    def __init__(self, token_computer: ITokenComputer) -> None:
        self.token_computer = token_computer

    def build_args_for_esdt_transfer(self, transfer: TokenTransfer) -> List[str]:
        args = ["ESDTTransfer"]
        args.extend(args_to_strings([transfer.token.identifier, transfer.amount]))

        return args

    def build_args_for_single_esdt_nft_transfer(self, transfer: TokenTransfer, receiver: IAddress) -> List[str]:
        args = ["ESDTNFTTransfer"]
        token = transfer.token
        identifier = self.token_computer.extract_identifier_from_extended_identifier(token.identifier)
        args.extend(args_to_strings([identifier, token.nonce, transfer.amount]))
        args.append(receiver.to_hex())

        return args

    def build_args_for_multi_esdt_nft_transfer(self, receiver: IAddress, transfers: List[TokenTransfer]) -> List[str]:
        args = ["MultiESDTNFTTransfer", receiver.to_hex(), arg_to_string(len(transfers))]

        for transfer in transfers:
            identifier = self.token_computer.extract_identifier_from_extended_identifier(transfer.token.identifier)
            args.extend(args_to_strings([identifier, transfer.token.nonce, transfer.amount]))

        return args
