from typing import Any, List

from multiversx_sdk_core.interfaces import IAddress
from multiversx_sdk_core.serializer import arg_to_string, args_to_strings
from multiversx_sdk_core.tokens import TokenComputer, TokenTransfer


class TokenTransfersDataBuilder:
    def __init__(self) -> None:
        pass

    def build_args_for_esdt_transfer(self,
                                     transfer: TokenTransfer,
                                     function: str = "",
                                     arguments: List[Any] = []) -> List[str]:
        args: List[str] = ["ESDTTransfer"]
        args.extend(args_to_strings([transfer.token.identifier, transfer.amount]))

        if function:
            args.append(arg_to_string(function))
            args.extend(args_to_strings(arguments))

        return args

    def build_args_for_single_esdt_nft_transfer(self,
                                                transfer: TokenTransfer,
                                                receiver: IAddress,
                                                function: str = "",
                                                arguments: List[Any] = []) -> List[str]:
        args: List[str] = ["ESDTNFTTransfer"]
        token = transfer.token
        identifier = self._ensure_identifier_has_correct_structure(token.identifier)
        args.extend(args_to_strings([identifier, token.nonce, transfer.amount, receiver]))

        if function:
            args.append(arg_to_string(function))
            args.extend(args_to_strings(arguments))

        return args

    def build_args_for_multi_esdt_nft_transfer(self,
                                               receiver: IAddress,
                                               transfers: List[TokenTransfer],
                                               function: str = "",
                                               arguments: List[Any] = []) -> List[str]:
        args: List[str] = ["MultiESDTNFTTransfer", arg_to_string(receiver), arg_to_string(len(transfers))]

        for transfer in transfers:
            identifier = self._ensure_identifier_has_correct_structure(transfer.token.identifier)
            args.extend(args_to_strings([identifier, transfer.token.nonce, transfer.amount]))

        if function:
            args.append(arg_to_string(function))
            args.extend(args_to_strings(arguments))

        return args

    def _ensure_identifier_has_correct_structure(self, identifier: str) -> str:
        if identifier.count("-") == 1:
            return identifier

        token_computer = TokenComputer()
        return token_computer.extract_identifier_from_extended_identifier(identifier)
