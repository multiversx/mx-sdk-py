from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

from multiversx_sdk.adapters.query_runner_adapter import QueryRunnerAdapter
from multiversx_sdk.converters.transactions_converter import \
    TransactionsConverter
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.message import Message, MessageComputer
from multiversx_sdk.core.smart_contract_queries_controller import \
    SmartContractQueriesController
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transactions_factories.smart_contract_transactions_factory import \
    SmartContractTransactionsFactory
from multiversx_sdk.core.transactions_factories.transactions_factory_config import \
    TransactionsFactoryConfig
from multiversx_sdk.core.transactions_factories.transfer_transactions_factory import \
    TransferTransactionsFactory
from multiversx_sdk.core.transactions_outcome_parsers.resources import \
    TransactionOutcome
from multiversx_sdk.core.transactions_outcome_parsers.smart_contract_transactions_outcome_parser import \
    SmartContractTransactionsOutcomeParser
from multiversx_sdk.core.transactions_outcome_parsers.smart_contract_transactions_outcome_parser_types import \
    SmartContractDeployOutcome
from multiversx_sdk.facades.errors import UnsuportedFileTypeError
from multiversx_sdk.network_providers.api_network_provider import \
    ApiNetworkProvider
from multiversx_sdk.network_providers.proxy_network_provider import \
    ProxyNetworkProvider
from multiversx_sdk.network_providers.transaction_awaiter import \
    TransactionAwaiter
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork
from multiversx_sdk.wallet.user_signer import UserSigner


class MainFacade:
    def __init__(self, network_provider: Union[ApiNetworkProvider, ProxyNetworkProvider]) -> None:
        self.provider = network_provider
        self.chain_id = self.provider.get_network_config().chain_id
        self.factories_config = TransactionsFactoryConfig(self.chain_id)

    def load_signer(self, wallet: Path, password: Optional[str] = None, index: Optional[int] = None) -> UserSigner:
        if wallet.suffix == ".pem":
            address_index = index if index is not None else 0
            return UserSigner.from_pem_file(wallet, address_index)
        elif wallet.suffix == ".json":
            wallet_password = password if password is not None else ""
            return UserSigner.from_wallet(wallet, wallet_password)
        else:
            raise UnsuportedFileTypeError(wallet.suffix)

    def sign_transaction(self, transaction: Transaction, signer: UserSigner):
        tx_computer = TransactionComputer()
        transaction.signature = signer.sign(tx_computer.compute_bytes_for_signing(transaction))  # type: ignore

    def sign_message(self, message: Message, signer: UserSigner):
        message_computer = MessageComputer()
        message.signature = signer.sign(message_computer.compute_bytes_for_signing(message))  # type: ignore

    def recall_account_nonce(self, address: Address) -> int:
        return self.provider.get_account(address).nonce

    def apply_nonce_on_transaction(self, transaction: Transaction):
        sender = Address.new_from_bech32(transaction.sender)
        transaction.nonce = self.recall_account_nonce(sender)

    def send_transaction(self, transaction: Transaction) -> str:
        return self.provider.send_transaction(transaction)

    def create_transaction_for_native_token_transfer(self,
                                                     sender: Address,
                                                     receiver: Address,
                                                     native_amount: int,
                                                     data: Optional[bytes] = None) -> Transaction:
        factory = TransferTransactionsFactory(self.factories_config)
        return factory.create_transaction_for_native_token_transfer(
            sender=sender,
            receiver=receiver,
            native_amount=native_amount,
            data=data.decode() if data else None
        )

    def create_transaction_for_esdt_token_transfer(self,
                                                   sender: Address,
                                                   receiver: Address,
                                                   token_transfers: Sequence[TokenTransfer]) -> Transaction:
        factory = TransferTransactionsFactory(self.factories_config)
        return factory.create_transaction_for_esdt_token_transfer(
            sender=sender,
            receiver=receiver,
            token_transfers=token_transfers
        )

    def create_transaction_for_contract_deploy(self,
                                               sender: Address,
                                               bytecode: Union[Path, bytes],
                                               arguments: List[Any],
                                               gas_limit: int,
                                               abi: Optional[Any] = None,
                                               native_transfer_amount: int = 0,
                                               is_upgradeable: bool = True,
                                               is_readable: bool = True,
                                               is_payable: bool = False,
                                               is_payable_by_sc: bool = True) -> Transaction:
        factory = SmartContractTransactionsFactory(self.factories_config)
        return factory.create_transaction_for_deploy(
            sender=sender,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=arguments,
            native_transfer_amount=native_transfer_amount,
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_sc
        )

    def await_completed_contract_deploy(self, tx_hash: str) -> SmartContractDeployOutcome:
        transaction = self.await_transaction_completion(tx_hash)
        tx_converter = TransactionsConverter()
        transaction_outcome = tx_converter.transaction_on_network_to_outcome(transaction)
        return self.parse_contract_deploy(transaction_outcome)

    def await_transaction_completion(self, tx_hash: str) -> TransactionOnNetwork:
        provider = ProviderWrapper(self.provider)
        transaction_awaiter = TransactionAwaiter(provider)
        return transaction_awaiter.await_completed(tx_hash)

    def parse_contract_deploy(self, transaction_outcome: TransactionOutcome) -> SmartContractDeployOutcome:
        tx_parser = SmartContractTransactionsOutcomeParser()
        return tx_parser.parse_deploy(transaction_outcome)

    def create_transaction_for_contract_call(self,
                                             sender: Address,
                                             contract: Address,
                                             function: str,
                                             arguments: List[Any],
                                             gas_limit: int,
                                             native_transfer_amount: Optional[int] = 0,
                                             token_transfers: Optional[List[TokenTransfer]] = None
                                             ) -> Transaction:
        pass

    def query_contract(self,
                       contract: Address,
                       function: str,
                       arguments: List[Any],
                       abi: Optional[Any] = None,
                       caller: Optional[Address] = None,
                       value: Optional[int] = None,
                       ) -> List[Any]:
        query_runner = QueryRunnerAdapter(self.provider)
        controller = SmartContractQueriesController(query_runner)
        return controller.query(
            contract=contract.to_bech32(),
            function=function,
            arguments=arguments,
            caller=caller.to_bech32() if caller else None,
            value=value
        )


class ProviderWrapper:
    def __init__(self, provider: Union[ApiNetworkProvider, ProxyNetworkProvider]) -> None:
        self.provider = provider

    def get_transaction(self, tx_hash: str) -> TransactionOnNetwork:
        if isinstance(self.provider, ProxyNetworkProvider):
            return self.provider.get_transaction(tx_hash, True)
        return self.provider.get_transaction(tx_hash)
