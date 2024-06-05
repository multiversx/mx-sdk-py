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
from multiversx_sdk.core.transactions_outcome_parsers.smart_contract_transactions_outcome_parser import \
    SmartContractTransactionsOutcomeParser
from multiversx_sdk.core.transactions_outcome_parsers.smart_contract_transactions_outcome_parser_types import \
    SmartContractDeployOutcome
from multiversx_sdk.facades.errors import (BadUsageError,
                                           UnsuportedFileTypeError)
from multiversx_sdk.network_providers.api_network_provider import \
    ApiNetworkProvider
from multiversx_sdk.network_providers.proxy_network_provider import \
    ProxyNetworkProvider
from multiversx_sdk.network_providers.transaction_awaiter import \
    TransactionAwaiter
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork
from multiversx_sdk.wallet.user_signer import UserSigner


class Account:
    def __init__(self, signer: UserSigner) -> None:
        self.signer = signer
        self.address = signer.get_pubkey().to_address("erd")
        self.nonce = 0

    @classmethod
    def from_file(cls, file_path: Path, password: Optional[str] = None, index: Optional[int] = None) -> "Account":
        if file_path.suffix == ".pem":
            address_index = index if index is not None else 0
            signer = UserSigner.from_pem_file(file_path, address_index)
            return Account(signer)
        elif file_path.suffix == ".json":
            wallet_password = password if password is not None else ""
            signer = UserSigner.from_wallet(file_path, wallet_password)
            return Account(signer)
        else:
            raise UnsuportedFileTypeError(file_path.suffix)

    def sign(self, data: bytes) -> bytes:
        return self.signer.sign(data)

    def get_nonce_then_increment(self) -> int:
        nonce = self.nonce
        self.nonce += 1
        return nonce


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

    def send_transaction(self, transaction: Transaction) -> str:
        return self.provider.send_transaction(transaction)

    def await_transaction_completion(self, tx_hash: str) -> TransactionOnNetwork:
        provider = ProviderWrapper(self.provider)
        transaction_awaiter = TransactionAwaiter(provider)
        return transaction_awaiter.await_completed(tx_hash)

    def create_transaction_for_transfer(self,
                                        sender: Account,
                                        receiver: Address,
                                        nonce: Optional[int] = None,
                                        native_transfer_amount: Optional[int] = None,
                                        token_transfers: Optional[Sequence[TokenTransfer]] = None,
                                        data: Optional[bytes] = None) -> Transaction:
        if native_transfer_amount and token_transfers:
            raise BadUsageError("Can't send both native token and esdt tokens.")

        factory = TransferTransactionsFactory(self.factories_config)

        if native_transfer_amount:
            transaction = factory.create_transaction_for_native_token_transfer(
                sender=sender.address,
                receiver=receiver,
                native_amount=native_transfer_amount,
                data=data.decode() if data else None
            )
        elif token_transfers:
            if data:
                raise BadUsageError("Can't set data field when sending esdt tokens.")

            transaction = factory.create_transaction_for_esdt_token_transfer(
                sender=sender.address,
                receiver=receiver,
                token_transfers=token_transfers
            )
        else:
            raise BadUsageError("No native token amount provided or no token transfers provided.")

        transaction.nonce = nonce if nonce else self.recall_account_nonce(sender.address)

        tx_computer = TransactionComputer()
        transaction.signature = sender.sign(tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_contract_deploy(self,
                                               sender: Account,
                                               bytecode: Union[Path, bytes],
                                               arguments: List[Any],
                                               gas_limit: int,
                                               abi: Optional[Any] = None,
                                               nonce: Optional[int] = None,
                                               native_transfer_amount: int = 0,
                                               is_upgradeable: bool = True,
                                               is_readable: bool = True,
                                               is_payable: bool = False,
                                               is_payable_by_sc: bool = True) -> Transaction:
        factory = SmartContractTransactionsFactory(self.factories_config)
        transaction = factory.create_transaction_for_deploy(
            sender=sender.address,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=arguments,
            native_transfer_amount=native_transfer_amount,
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_sc
        )

        transaction.nonce = nonce if nonce else self.recall_account_nonce(sender.address)

        tx_computer = TransactionComputer()
        transaction.signature = sender.sign(tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_contract_deploy(self, transaction_on_network: TransactionOnNetwork) -> SmartContractDeployOutcome:
        tx_converter = TransactionsConverter()
        transaction_outcome = tx_converter.transaction_on_network_to_outcome(transaction_on_network)

        tx_parser = SmartContractTransactionsOutcomeParser()
        return tx_parser.parse_deploy(transaction_outcome)

    def await_completed_contract_deploy(self, tx_hash: str) -> SmartContractDeployOutcome:
        transaction = self.await_transaction_completion(tx_hash)
        return self.parse_contract_deploy(transaction)

    def create_transaction_for_contract_call(self,
                                             sender: Account,
                                             contract: Address,
                                             function: str,
                                             gas_limit: int,
                                             nonce: Optional[int] = None,
                                             abi: Optional[Any] = None,
                                             arguments: Optional[Sequence[Any]] = None,
                                             native_transfer_amount: Optional[int] = None,
                                             token_transfers: Optional[Sequence[TokenTransfer]] = None
                                             ) -> Transaction:
        factory = SmartContractTransactionsFactory(self.factories_config)
        transaction = factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function=function,
            gas_limit=gas_limit,
            arguments=arguments if arguments else [],
            native_transfer_amount=native_transfer_amount if native_transfer_amount else 0,
            token_transfers=token_transfers if token_transfers else []
        )

        transaction.nonce = nonce if nonce else self.recall_account_nonce(sender.address)

        tx_computer = TransactionComputer()
        transaction.signature = sender.sign(tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_contract_call(self,
                            transaction_on_network: TransactionOnNetwork,
                            abi: Optional[Any] = None,
                            function: Optional[str] = None):
        pass

    def await_completed_contract_call(self,
                                      tx_hash: str,
                                      abi: Optional[Any] = None):
        transaction = self.await_transaction_completion(tx_hash)
        return self.parse_contract_call(transaction)

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


class TestnetEntrypoint(MainFacade):
    def __init__(self, url: str) -> None:
        super().__init__(ApiNetworkProvider(url))


class ProviderWrapper:
    def __init__(self, provider: Union[ApiNetworkProvider, ProxyNetworkProvider]) -> None:
        self.provider = provider

    def get_transaction(self, tx_hash: str) -> TransactionOnNetwork:
        if isinstance(self.provider, ProxyNetworkProvider):
            return self.provider.get_transaction(tx_hash, True)
        return self.provider.get_transaction(tx_hash)


if __name__ == '__main__':
    facade = TestnetEntrypoint("https://testnet-api.multiversx.com")
    alice = Account.from_file(Path("multiversx_sdk/testutils/testwallets/alice.pem"))
    alice.nonce = facade.recall_account_nonce(alice.address)

    tx = facade.create_transaction_for_transfer(
        sender=alice,
        receiver=Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"),
        native_transfer_amount=10000000,
    )

    hash = facade.send_transaction(tx)
    facade.await_transaction_completion(hash)
