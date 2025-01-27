from multiversx_sdk.abi import BigUIntValue, Serializer
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.core import Address, TokenComputer, TokenTransfer


class TokenTransfersDataBuilder:
    """
    **FOR INTERNAL USE ONLY.**
    Used for the transactions factories.
    """

    def __init__(self, token_computer: TokenComputer) -> None:
        self.token_computer = token_computer
        self.serializer = Serializer()

    def build_args_for_esdt_transfer(self, transfer: TokenTransfer) -> list[str]:
        args = ["ESDTTransfer"]

        serialized_args = self.serializer.serialize_to_parts(
            [StringValue(transfer.token.identifier), BigUIntValue(transfer.amount)]
        )
        args.extend([arg.hex() for arg in serialized_args])

        return args

    def build_args_for_single_esdt_nft_transfer(self, transfer: TokenTransfer, receiver: Address) -> list[str]:
        args = ["ESDTNFTTransfer"]
        token = transfer.token
        identifier = self.token_computer.extract_identifier_from_extended_identifier(token.identifier)

        serialized_args = self.serializer.serialize_to_parts(
            [
                StringValue(identifier),
                BigUIntValue(token.nonce),
                BigUIntValue(transfer.amount),
            ]
        )
        args.extend([arg.hex() for arg in serialized_args])
        args.append(receiver.to_hex())

        return args

    def build_args_for_multi_esdt_nft_transfer(self, receiver: Address, transfers: list[TokenTransfer]) -> list[str]:
        serialized_num_of_transfers = self.serializer.serialize([BigUIntValue(len(transfers))])
        args = ["MultiESDTNFTTransfer", receiver.to_hex(), serialized_num_of_transfers]

        for transfer in transfers:
            identifier = self.token_computer.extract_identifier_from_extended_identifier(transfer.token.identifier)
            serialized_args = self.serializer.serialize_to_parts(
                [
                    StringValue(identifier),
                    BigUIntValue(transfer.token.nonce),
                    BigUIntValue(transfer.amount),
                ]
            )
            args.extend([arg.hex() for arg in serialized_args])

        return args
