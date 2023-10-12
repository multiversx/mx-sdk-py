from pathlib import Path
from typing import Any, List, Protocol, Union

from multiversx_sdk_core import Transaction
from multiversx_sdk_core.address import Address
from multiversx_sdk_core.code_metadata import CodeMetadata
from multiversx_sdk_core.constants import (CONTRACT_DEPLOY_ADDRESS,
                                           VM_TYPE_WASM_VM)
from multiversx_sdk_core.errors import BadUsageError
from multiversx_sdk_core.interfaces import IAddress
from multiversx_sdk_core.serializer import arg_to_string, args_to_strings
from multiversx_sdk_core.tokens import TokenComputer, TokenTransfer
from multiversx_sdk_core.transaction_factories.token_transfers_data_builder import \
    TokenTransfersDataBuilder
from multiversx_sdk_core.transaction_factories.transaction_builder import \
    TransactionBuilder


class IConfig(Protocol):
    chain_id: str
    min_gas_limit: int
    gas_limit_per_byte: int


class SmartContractTransactionsFactory:
    def __init__(self, config: IConfig) -> None:
        self.config = config
        self._data_args_builder = TokenTransfersDataBuilder()

    def create_transaction_for_deploy(self,
                                      sender: IAddress,
                                      bytecode: Union[Path, bytes],
                                      gas_limit: int,
                                      arguments: List[Any] = [],
                                      native_transfer_amount: int = 0,
                                      is_upgradeable: bool = True,
                                      is_readable: bool = True,
                                      is_payable: bool = False,
                                      is_payable_by_sc: bool = True) -> Transaction:
        if isinstance(bytecode, Path):
            bytecode = bytecode.read_bytes()

        metadata = CodeMetadata(is_upgradeable, is_readable, is_payable, is_payable_by_sc)

        parts = [
            arg_to_string(bytecode),
            arg_to_string(VM_TYPE_WASM_VM),
            str(metadata)
        ]

        parts += args_to_strings(arguments)

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.from_bech32(CONTRACT_DEPLOY_ADDRESS),
            data_parts=parts,
            gas_limit=gas_limit,
            add_data_movement_gas=False,
            amount=native_transfer_amount
        ).build()

        return transaction

    def create_transaction_for_execute(self,
                                       sender: IAddress,
                                       contract: IAddress,
                                       function: str,
                                       gas_limit: int,
                                       arguments: List[Any] = [],
                                       native_transfer_amount: int = 0,
                                       token_transfers: List[TokenTransfer] = []) -> Transaction:
        number_of_tokens = len(token_transfers)

        if native_transfer_amount and number_of_tokens:
            raise BadUsageError("Can't send both native token and ESDT/NFT tokens")

        token_computer = TokenComputer()
        transfer_args: List[str] = []

        if len(token_transfers) == 1:
            transfer = token_transfers[0]

            if token_computer.is_fungible(transfer.token):
                transfer_args = self._data_args_builder.build_args_for_esdt_transfer(
                    transfer=transfer, function=function, arguments=arguments
                )
            else:
                transfer_args = self._data_args_builder.build_args_for_single_esdt_nft_transfer(
                    transfer=transfer, receiver=contract, function=function, arguments=arguments
                )
                contract = sender
        elif len(token_transfers) > 1:
            transfer_args = self._data_args_builder.build_args_for_multi_esdt_nft_transfer(
                receiver=contract, transfers=token_transfers, function=function, arguments=arguments
            )
            contract = sender
        else:
            transfer_args.append(function)
            transfer_args.extend(args_to_strings(arguments))

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=contract,
            data_parts=transfer_args,
            gas_limit=gas_limit,
            add_data_movement_gas=False,
            amount=native_transfer_amount
        ).build()

        return transaction

    def create_transaction_for_upgrade(self,
                                       sender: IAddress,
                                       contract: IAddress,
                                       bytecode: Union[Path, bytes],
                                       gas_limit: int,
                                       arguments: List[Any] = [],
                                       native_transfer_amount: int = 0,
                                       is_upgradeable: bool = True,
                                       is_readable: bool = True,
                                       is_payable: bool = False,
                                       is_payable_by_sc: bool = True) -> Transaction:
        if isinstance(bytecode, Path):
            bytecode = bytecode.read_bytes()

        metadata = CodeMetadata(is_upgradeable, is_readable, is_payable, is_payable_by_sc)

        parts = [
            "upgradeContract",
            arg_to_string(bytecode),
            str(metadata)
        ]

        parts += args_to_strings(arguments)

        intent = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=contract,
            data_parts=parts,
            gas_limit=gas_limit,
            add_data_movement_gas=False,
            amount=native_transfer_amount
        ).build()

        return intent
