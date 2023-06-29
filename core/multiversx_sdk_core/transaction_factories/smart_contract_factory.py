from pathlib import Path
from typing import Any, List, Optional, Protocol

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.code_metadata import CodeMetadata
from multiversx_sdk_core.constants import (ARGS_SEPARATOR,
                                           CONTRACT_DEPLOY_ADDRESS,
                                           TRANSACTION_OPTIONS_DEFAULT,
                                           TRANSACTION_VERSION_DEFAULT,
                                           VM_TYPE_WASM_VM)
from multiversx_sdk_core.interfaces import (IAddress, IChainID, IGasLimit,
                                            IGasPrice, INonce,
                                            ITransactionValue)
from multiversx_sdk_core.serializer import arg_to_string, args_to_strings
from multiversx_sdk_core.transaction import Transaction
from multiversx_sdk_core.transaction_payload import TransactionPayload


class IConfig(Protocol):
    chain_id: IChainID


class SmartContractFactory:
    def __init__(self, config: IConfig) -> None:
        self.config = config

    def create_transaction_for_deploy(self,
                                      deployer: IAddress,
                                      bytecode_path: Path,
                                      gas_limit: IGasLimit,
                                      arguments: List[Any] = [],
                                      nonce: Optional[INonce] = None,
                                      value: Optional[ITransactionValue] = None,
                                      guardian: Optional[IAddress] = None,
                                      gas_price: Optional[IGasPrice] = None,
                                      is_upgradeable: bool = True,
                                      is_readable: bool = True,
                                      is_payable: bool = True,
                                      is_payable_by_sc: bool = True) -> Transaction:
        bytecode = bytecode_path.read_bytes()
        metadata = CodeMetadata(is_upgradeable, is_readable, is_payable, is_payable_by_sc)

        parts = [
            arg_to_string(bytecode),
            arg_to_string(VM_TYPE_WASM_VM),
            str(metadata)
        ]

        parts += args_to_strings(arguments)

        transaction = self.create_transaction(
            sender=deployer,
            receiver=Address.from_bech32(CONTRACT_DEPLOY_ADDRESS),
            data_parts=parts,
            gas_limit=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            value=value,
            guardian=guardian
        )

        return transaction

    def create_transaction_for_execute(self,
                                       sender: IAddress,
                                       contract_address: IAddress,
                                       function: str,
                                       gas_limit: IGasLimit,
                                       arguments: List[Any] = [],
                                       nonce: Optional[INonce] = None,
                                       guardian: Optional[IAddress] = None,
                                       value: Optional[ITransactionValue] = None) -> Transaction:
        parts = [function] + args_to_strings(arguments)

        transaction = self.create_transaction(
            sender=sender,
            receiver=contract_address,
            data_parts=parts,
            gas_limit=gas_limit,
            nonce=nonce,
            guardian=guardian,
            value=value
        )

        return transaction

    def create_transaction_for_upgrade(self,
                                       sender: IAddress,
                                       contract: IAddress,
                                       bytecode_path: Path,
                                       gas_limit: IGasLimit,
                                       arguments: List[Any] = [],
                                       nonce: Optional[INonce] = None,
                                       guardian: Optional[IAddress] = None,
                                       is_upgradeable: bool = True,
                                       is_readable: bool = True,
                                       is_payable: bool = True,
                                       is_payable_by_sc: bool = True
                                       ) -> Transaction:
        bytecode = bytecode_path.read_bytes()
        metadata = CodeMetadata(is_upgradeable, is_readable, is_payable, is_payable_by_sc)

        parts = [
            "upgradeContract",
            arg_to_string(bytecode),
            str(metadata)
        ]

        parts += args_to_strings(arguments)

        transaction = self.create_transaction(
            sender=sender,
            receiver=contract,
            data_parts=parts,
            gas_limit=gas_limit,
            nonce=nonce,
            guardian=guardian
        )

        return transaction

    def create_transaction(
            self,
            sender: IAddress,
            receiver: IAddress,
            data_parts: List[str],
            gas_limit: IGasLimit,
            nonce: Optional[INonce],
            value: Optional[ITransactionValue] = None,
            guardian: Optional[IAddress] = None,
            gas_price: Optional[IGasPrice] = None) -> Transaction:
        data = self._build_transaction_payload(data_parts)
        version = TRANSACTION_VERSION_DEFAULT
        options = TRANSACTION_OPTIONS_DEFAULT

        return Transaction(
            chain_id=self.config.chain_id,
            sender=sender,
            receiver=receiver,
            gas_limit=gas_limit,
            gas_price=gas_price,
            value=value,
            nonce=nonce,
            data=data,
            version=version,
            options=options,
            guardian=guardian
        )

    def _build_transaction_payload(self, parts: List[str]) -> TransactionPayload:
        data = ARGS_SEPARATOR.join(parts)
        return TransactionPayload.from_str(data)
