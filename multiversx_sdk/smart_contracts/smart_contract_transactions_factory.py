from pathlib import Path
from typing import Any, Optional, Sequence, Union

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.abi.bytes_value import BytesValue
from multiversx_sdk.abi.code_metadata_value import CodeMetadataValue
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.abi.typesystem import is_list_of_bytes, is_list_of_typed_values
from multiversx_sdk.builders.token_transfers_data_builder import (
    TokenTransfersDataBuilder,
)
from multiversx_sdk.builders.transaction_builder import TransactionBuilder
from multiversx_sdk.core import (
    Address,
    CodeMetadata,
    TokenComputer,
    TokenTransfer,
    Transaction,
)
from multiversx_sdk.core.constants import CONTRACT_DEPLOY_ADDRESS_HEX, VM_TYPE_WASM_VM
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.smart_contracts.errors import ArgumentSerializationError


class SmartContractTransactionsFactory:
    def __init__(self, config: TransactionsFactoryConfig, abi: Optional[Abi] = None) -> None:
        self.config = config
        self.abi = abi
        self.serializer = Serializer()
        self.token_computer = TokenComputer()
        self._data_args_builder = TokenTransfersDataBuilder(self.token_computer)

    def create_transaction_for_deploy(
        self,
        sender: Address,
        bytecode: Union[Path, bytes],
        gas_limit: int,
        arguments: Sequence[Any] = [],
        native_transfer_amount: int = 0,
        is_upgradeable: bool = True,
        is_readable: bool = True,
        is_payable: bool = False,
        is_payable_by_sc: bool = True,
    ) -> Transaction:
        if isinstance(bytecode, Path):
            bytecode = bytecode.read_bytes()

        metadata = CodeMetadata(is_upgradeable, is_readable, is_payable, is_payable_by_sc)

        serialized_parts = self.serializer.serialize_to_parts(
            [
                BytesValue(bytecode),
                BytesValue(VM_TYPE_WASM_VM),
                CodeMetadataValue.new_from_code_metadata(metadata),
            ]
        )

        prepared_arg = self._encode_deploy_arguments(list(arguments))
        parts = [arg.hex() for arg in serialized_parts + prepared_arg]

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(CONTRACT_DEPLOY_ADDRESS_HEX),
            data_parts=parts,
            gas_limit=gas_limit,
            add_data_movement_gas=False,
            amount=native_transfer_amount,
        ).build()

    def create_transaction_for_execute(
        self,
        sender: Address,
        contract: Address,
        function: str,
        gas_limit: int,
        arguments: Sequence[Any] = [],
        native_transfer_amount: int = 0,
        token_transfers: list[TokenTransfer] = [],
    ) -> Transaction:
        number_of_tokens = len(token_transfers)
        receiver = contract

        if native_transfer_amount and number_of_tokens:
            native_tranfer = TokenTransfer.new_from_native_amount(native_transfer_amount)
            token_transfers = list(token_transfers) + [native_tranfer]

            native_transfer_amount = 0
            number_of_tokens += 1

        data_parts: list[str] = []

        if number_of_tokens == 1:
            transfer = token_transfers[0]

            if self.token_computer.is_fungible(transfer.token):
                data_parts = self._data_args_builder.build_args_for_esdt_transfer(transfer=transfer)
            else:
                data_parts = self._data_args_builder.build_args_for_single_esdt_nft_transfer(
                    transfer=transfer, receiver=receiver
                )
                receiver = sender
        elif number_of_tokens > 1:
            data_parts = self._data_args_builder.build_args_for_multi_esdt_nft_transfer(
                receiver=receiver, transfers=token_transfers
            )
            receiver = sender

        prepared_arguments = self._encode_execute_arguments(function, list(arguments))

        (
            data_parts.append(function)
            if not data_parts
            else data_parts.append(self.serializer.serialize([StringValue(function)]))
        )
        data_parts += [arg.hex() for arg in prepared_arguments]

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=receiver,
            data_parts=data_parts,
            gas_limit=gas_limit,
            add_data_movement_gas=False,
            amount=native_transfer_amount,
        ).build()

    def create_transaction_for_upgrade(
        self,
        sender: Address,
        contract: Address,
        bytecode: Union[Path, bytes],
        gas_limit: int,
        arguments: Sequence[Any] = [],
        native_transfer_amount: int = 0,
        is_upgradeable: bool = True,
        is_readable: bool = True,
        is_payable: bool = False,
        is_payable_by_sc: bool = True,
    ) -> Transaction:
        if isinstance(bytecode, Path):
            bytecode = bytecode.read_bytes()

        metadata = CodeMetadata(is_upgradeable, is_readable, is_payable, is_payable_by_sc)

        parts = ["upgradeContract"]
        serialized_parts = self.serializer.serialize_to_parts(
            [BytesValue(bytecode), CodeMetadataValue.new_from_code_metadata(metadata)]
        )

        prepared_arguments = self._encode_upgrade_arguments(list(arguments))
        parts += [arg.hex() for arg in serialized_parts + prepared_arguments]

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=contract,
            data_parts=parts,
            gas_limit=gas_limit,
            add_data_movement_gas=False,
            amount=native_transfer_amount,
        ).build()

    def create_transaction_for_claiming_developer_rewards(self, sender: Address, contract: Address) -> Transaction:
        data_parts = ["ClaimDeveloperRewards"]

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=contract,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_claim_developer_rewards,
            add_data_movement_gas=False,
        ).build()

    def create_transaction_for_changing_owner_address(
        self, sender: Address, contract: Address, new_owner: Address
    ) -> Transaction:
        data_parts = ["ChangeOwnerAddress", new_owner.to_hex()]

        return TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=contract,
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_change_owner_address,
            add_data_movement_gas=False,
        ).build()

    def _encode_deploy_arguments(self, args: list[Any]) -> list[bytes]:
        if self.abi:
            return self.abi.encode_constructor_input_parameters(args)

        if is_list_of_typed_values(args):
            return self.serializer.serialize_to_parts(args)

        if is_list_of_bytes(args):
            return args

        raise ArgumentSerializationError()

    def _encode_execute_arguments(self, function_name: str, args: list[Any]) -> list[bytes]:
        if self.abi:
            return self.abi.encode_endpoint_input_parameters(function_name, args)

        if is_list_of_typed_values(args):
            return self.serializer.serialize_to_parts(args)

        if is_list_of_bytes(args):
            return args

        raise ArgumentSerializationError()

    def _encode_upgrade_arguments(self, args: list[Any]) -> list[bytes]:
        if self.abi:
            return self.abi.encode_upgrade_constructor_input_parameters(args)

        if is_list_of_typed_values(args):
            return self.serializer.serialize_to_parts(args)

        if is_list_of_bytes(args):
            return args

        raise ArgumentSerializationError()
