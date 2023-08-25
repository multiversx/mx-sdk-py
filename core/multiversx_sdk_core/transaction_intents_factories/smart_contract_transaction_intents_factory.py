from pathlib import Path
from typing import Any, List, Protocol, Union

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.code_metadata import CodeMetadata
from multiversx_sdk_core.constants import (CONTRACT_DEPLOY_ADDRESS,
                                           VM_TYPE_WASM_VM)
from multiversx_sdk_core.interfaces import IAddress
from multiversx_sdk_core.serializer import arg_to_string, args_to_strings
from multiversx_sdk_core.transaction_intents_factories.transaction_intent_builder import \
    TransactionIntentBuilder
from multiversx_sdk_core.transaction_intent import TransactionIntent


class IConfig(Protocol):
    chain_id: str
    min_gas_limit: int
    gas_limit_per_byte: int


class SmartContractTransactionIntentsFactory:
    def __init__(self, config: IConfig) -> None:
        self.config = config

    def create_transaction_intent_for_deploy(self,
                                             sender: IAddress,
                                             bytecode: Union[Path, bytes],
                                             gas_limit: int,
                                             arguments: List[Any] = [],
                                             is_upgradeable: bool = True,
                                             is_readable: bool = True,
                                             is_payable: bool = False,
                                             is_payable_by_sc: bool = True) -> TransactionIntent:
        if isinstance(bytecode, Path):
            bytecode = bytecode.read_bytes()

        metadata = CodeMetadata(is_upgradeable, is_readable, is_payable, is_payable_by_sc)

        parts = [
            arg_to_string(bytecode),
            arg_to_string(VM_TYPE_WASM_VM),
            str(metadata)
        ]

        parts += args_to_strings(arguments)

        intent = TransactionIntentBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.from_bech32(CONTRACT_DEPLOY_ADDRESS),
            data_parts=parts,
            execution_gas_limit=gas_limit
        ).build()

        return intent

    def create_transaction_intent_for_execute(self,
                                              sender: IAddress,
                                              contract_address: IAddress,
                                              function: str,
                                              gas_limit: int,
                                              arguments: List[Any] = []) -> TransactionIntent:
        parts = [function] + args_to_strings(arguments)

        intent = TransactionIntentBuilder(
            config=self.config,
            sender=sender,
            receiver=contract_address,
            data_parts=parts,
            execution_gas_limit=gas_limit
        ).build()

        return intent

    def create_transaction_intent_for_upgrade(self,
                                              sender: IAddress,
                                              contract: IAddress,
                                              bytecode: Union[Path, bytes],
                                              gas_limit: int,
                                              arguments: List[Any] = [],
                                              is_upgradeable: bool = True,
                                              is_readable: bool = True,
                                              is_payable: bool = False,
                                              is_payable_by_sc: bool = True
                                              ) -> TransactionIntent:
        if isinstance(bytecode, Path):
            bytecode = bytecode.read_bytes()

        metadata = CodeMetadata(is_upgradeable, is_readable, is_payable, is_payable_by_sc)

        parts = [
            "upgradeContract",
            arg_to_string(bytecode),
            str(metadata)
        ]

        parts += args_to_strings(arguments)

        intent = TransactionIntentBuilder(
            config=self.config,
            sender=sender,
            receiver=contract,
            data_parts=parts,
            execution_gas_limit=gas_limit
        ).build()

        return intent
