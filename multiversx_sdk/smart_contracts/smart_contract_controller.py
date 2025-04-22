from pathlib import Path
from typing import Any, Optional, Protocol, Sequence, Union

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.typesystem import is_list_of_bytes, is_list_of_typed_values
from multiversx_sdk.core import (
    Address,
    TokenTransfer,
    Transaction,
    TransactionOnNetwork,
)
from multiversx_sdk.core.base_controller import BaseController
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.network_providers.resources import AwaitingOptions
from multiversx_sdk.smart_contracts.errors import SmartContractQueryError
from multiversx_sdk.smart_contracts.smart_contract_query import (
    SmartContractQuery,
    SmartContractQueryResponse,
)
from multiversx_sdk.smart_contracts.smart_contract_transactions_factory import (
    SmartContractTransactionsFactory,
)
from multiversx_sdk.smart_contracts.smart_contract_transactions_outcome_parser import (
    SmartContractTransactionsOutcomeParser,
)
from multiversx_sdk.smart_contracts.smart_contract_transactions_outcome_parser_types import (
    ParsedSmartContractCallOutcome,
    SmartContractDeployOutcome,
)


# fmt: off
class INetworkProvider(Protocol):
    def query_contract(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        ...

    def await_transaction_completed(
        self, transaction_hash: Union[str, bytes], options: Optional[AwaitingOptions] = None
    ) -> TransactionOnNetwork:
        ...
# fmt: on


class SmartContractController(BaseController):
    def __init__(
        self,
        chain_id: str,
        network_provider: INetworkProvider,
        abi: Optional[Abi] = None,
    ) -> None:
        self.abi = abi
        self.factory = SmartContractTransactionsFactory(TransactionsFactoryConfig(chain_id), abi=self.abi)
        self.parser = SmartContractTransactionsOutcomeParser(abi=self.abi)
        self.network_provider = network_provider
        self.serializer = Serializer()

    def create_transaction_for_deploy(
        self,
        sender: IAccount,
        nonce: int,
        bytecode: Union[Path, bytes],
        gas_limit: int,
        arguments: Sequence[Any] = [],
        native_transfer_amount: int = 0,
        is_upgradeable: bool = True,
        is_readable: bool = True,
        is_payable: bool = False,
        is_payable_by_sc: bool = True,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_deploy(
            sender=sender.address,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=arguments,
            native_transfer_amount=native_transfer_amount,
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_sc,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_deploy(self, transaction_on_network: TransactionOnNetwork) -> SmartContractDeployOutcome:
        return self.parser.parse_deploy(transaction_on_network)

    def await_completed_deploy(self, transaction_hash: Union[str, bytes]) -> SmartContractDeployOutcome:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_deploy(transaction)

    def create_transaction_for_upgrade(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        bytecode: Union[Path, bytes],
        gas_limit: int,
        arguments: Sequence[Any] = [],
        native_transfer_amount: int = 0,
        is_upgradeable: bool = True,
        is_readable: bool = True,
        is_payable: bool = False,
        is_payable_by_sc: bool = True,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_upgrade(
            sender=sender.address,
            contract=contract,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=arguments,
            native_transfer_amount=native_transfer_amount,
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_sc,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_execute(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        gas_limit: int,
        function: str,
        arguments: Sequence[Any] = [],
        native_transfer_amount: int = 0,
        token_transfers: list[TokenTransfer] = [],
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            gas_limit=gas_limit,
            function=function,
            arguments=arguments,
            native_transfer_amount=native_transfer_amount,
            token_transfers=token_transfers,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_execute(
        self,
        transaction_on_network: TransactionOnNetwork,
        function: Optional[str] = None,
    ) -> ParsedSmartContractCallOutcome:
        return self.parser.parse_execute(transaction_on_network, function)

    def await_completed_execute(self, transaction_hash: Union[str, bytes]) -> ParsedSmartContractCallOutcome:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_execute(transaction, transaction.function)

    def query(
        self,
        contract: Address,
        function: str,
        arguments: list[Any],
        caller: Optional[Address] = None,
        value: Optional[int] = None,
    ) -> list[Any]:
        """It calls `create_query()`, `run_query()` and `parse_query_response()` in one go."""
        query = self.create_query(
            contract=contract,
            function=function,
            arguments=arguments,
            caller=caller,
            value=value,
        )

        query_response = self.run_query(query)
        self._raise_for_status(query_response)
        return self.parse_query_response(query_response)

    def _raise_for_status(self, query_response: SmartContractQueryResponse):
        is_ok = query_response.return_code == "ok"
        if not is_ok:
            raise SmartContractQueryError(query_response.return_code, query_response.return_message)

    def create_query(
        self,
        contract: Address,
        function: str,
        arguments: list[Any],
        caller: Optional[Address] = None,
        value: Optional[int] = None,
    ) -> SmartContractQuery:
        prepared_arguments = self._encode_arguments(function, arguments)

        return SmartContractQuery(
            contract=contract,
            function=function,
            arguments=prepared_arguments,
            caller=caller,
            value=value,
        )

    def _encode_arguments(self, function_name: str, args: list[Any]) -> list[bytes]:
        if self.abi:
            return self.abi.encode_endpoint_input_parameters(function_name, args)

        if is_list_of_typed_values(args):
            return self.serializer.serialize_to_parts(args)

        if is_list_of_bytes(args):
            return args

        raise Exception("Can't serialize arguments")

    def run_query(self, query: SmartContractQuery) -> SmartContractQueryResponse:
        return self.network_provider.query_contract(query)

    def parse_query_response(self, response: SmartContractQueryResponse) -> list[Any]:
        encoded_values = response.return_data_parts

        if self.abi:
            return self.abi.decode_endpoint_output_parameters(response.function, encoded_values)

        return encoded_values
