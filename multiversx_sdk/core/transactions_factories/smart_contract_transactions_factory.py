from pathlib import Path
from typing import Any, List, Protocol, Sequence, Union

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.code_metadata import CodeMetadata
from multiversx_sdk.core.constants import (CONTRACT_DEPLOY_ADDRESS,
                                           VM_TYPE_WASM_VM)
from multiversx_sdk.core.errors import BadUsageError
from multiversx_sdk.core.interfaces import IAddress, ITokenTransfer
from multiversx_sdk.core.serializer import arg_to_string, args_to_strings
from multiversx_sdk.core.tokens import TokenComputer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factories.token_transfers_data_builder import \
    TokenTransfersDataBuilder
from multiversx_sdk.core.transactions_factories.transaction_builder import \
    TransactionBuilder


class IConfig(Protocol):
    chain_id: str
    min_gas_limit: int
    gas_limit_per_byte: int
    gas_limit_claim_developer_rewards: int
    gas_limit_change_owner_address: int


class SmartContractTransactionsFactory:
    def __init__(self, config: IConfig) -> None:
        self.config = config
        self.token_computer = TokenComputer()
        self._data_args_builder = TokenTransfersDataBuilder(self.token_computer)

    def create_transaction_for_deploy(self,
                                      sender: IAddress,
                                      bytecode: Union[Path, bytes],
                                      gas_limit: int,
                                      arguments: Sequence[Any] = [],
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

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_bech32(CONTRACT_DEPLOY_ADDRESS),
            data_parts=parts,
            gas_limit=gas_limit,
            add_data_movement_gas=False,
            amount=native_transfer_amount
        ).build()

    def create_transaction_for_execute(self,
                                       sender: IAddress,
                                       contract: IAddress,
                                       function: str,
                                       gas_limit: int,
                                       arguments: Sequence[Any] = [],
                                       native_transfer_amount: int = 0,
                                       token_transfers: Sequence[ITokenTransfer] = []) -> Transaction:
        number_of_tokens = len(token_transfers)
        receiver = contract

        if native_transfer_amount and number_of_tokens:
            raise BadUsageError("Can't send both native token and custom tokens(ESDT/NFT)")

        data_parts: List[str] = []

        if len(token_transfers) == 1:
            transfer = token_transfers[0]

            if self.token_computer.is_fungible(transfer.token):
                data_parts = self._data_args_builder.build_args_for_esdt_transfer(transfer=transfer)
            else:
                data_parts = self._data_args_builder.build_args_for_single_esdt_nft_transfer(
                    transfer=transfer, receiver=receiver)
                receiver = sender
        elif len(token_transfers) > 1:
            data_parts = self._data_args_builder.build_args_for_multi_esdt_nft_transfer(
                receiver=receiver, transfers=token_transfers)
            receiver = sender

        data_parts.append(function) if not data_parts else data_parts.append(arg_to_string(function))
        data_parts.extend(args_to_strings(arguments))

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=receiver,
            data_parts=data_parts,
            gas_limit=gas_limit,
            add_data_movement_gas=False,
            amount=native_transfer_amount
        ).build()

    def create_transaction_for_upgrade(self,
                                       sender: IAddress,
                                       contract: IAddress,
                                       bytecode: Union[Path, bytes],
                                       gas_limit: int,
                                       arguments: Sequence[Any] = [],
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

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=contract,
            data_parts=parts,
            gas_limit=gas_limit,
            add_data_movement_gas=False,
            amount=native_transfer_amount
        ).build()

    def create_transaction_for_claiming_developer_rewards(self,
                                                          sender: IAddress,
                                                          contract: IAddress) -> Transaction:
        data_parts = ["ClaimDeveloperRewards"]

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=contract,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_claim_developer_rewards,
            add_data_movement_gas=False
        ).build()

    def create_transaction_for_changing_owner_address(self,
                                                      sender: IAddress,
                                                      contract: IAddress,
                                                      new_owner: IAddress) -> Transaction:
        data_parts = ["ChangeOwnerAddress", new_owner.to_hex()]

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=contract,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_change_owner_address,
            add_data_movement_gas=False,
        ).build()
