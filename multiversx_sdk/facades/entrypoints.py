
from typing import Any, Optional, Union

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.controllers.account_controller import \
    AccountController
from multiversx_sdk.core.controllers.delegation_controller import \
    DelegationController
from multiversx_sdk.core.controllers.relayed_controller import \
    RelayedController
from multiversx_sdk.core.controllers.smart_contract_controller import \
    SmartContractController
from multiversx_sdk.core.controllers.token_management_controller import \
    TokenManagementController
from multiversx_sdk.core.controllers.transfers_controller import \
    TransfersController
from multiversx_sdk.core.message import Message, MessageComputer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transactions_factories.transactions_factory_config import \
    TransactionsFactoryConfig
from multiversx_sdk.facades.config import (DevnetConfig, MainnetConfig,
                                           TestnetConfig)
from multiversx_sdk.facades.errors import InvalidNetworkProviderKindError
from multiversx_sdk.network_providers.api_network_provider import \
    ApiNetworkProvider
from multiversx_sdk.network_providers.proxy_network_provider import \
    ProxyNetworkProvider
from multiversx_sdk.network_providers.transaction_awaiter import \
    TransactionAwaiter
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork
from multiversx_sdk.wallet.user_signer import UserSigner
from multiversx_sdk.wallet.user_verifer import UserVerifier


class NetworkEntrypoint:
    def __init__(self,
                 url: str,
                 kind: str,
                 chain_id: str) -> None:
        if kind == "proxy":
            self.provider = ProxyNetworkProvider(url)
        elif kind == "api":
            self.provider = ApiNetworkProvider(url)
        else:
            raise InvalidNetworkProviderKindError()

        self.chain_id = chain_id
        self.factories_config = TransactionsFactoryConfig(self.chain_id)

    def sign_transaction(self, transaction: Transaction, signer: UserSigner):
        tx_computer = TransactionComputer()
        transaction.signature = signer.sign(tx_computer.compute_bytes_for_signing(transaction))

    def verify_transaction_signature(self, transaction: Transaction) -> bool:
        verifier = UserVerifier.from_address(Address.new_from_bech32(transaction.sender))
        tx_computer = TransactionComputer()

        return verifier.verify(
            data=tx_computer.compute_bytes_for_verifying(transaction),
            signature=transaction.signature
        )

    def sign_message(self, message: Message, signer: UserSigner):
        message_computer = MessageComputer()
        message.signature = signer.sign(message_computer.compute_bytes_for_signing(message))

    def verify_message_signature(self, message: Message) -> bool:
        if message.address is None:
            raise Exception("`address` property of Message is not set")

        verifier = UserVerifier.from_address(message.address)
        message_computer = MessageComputer()

        return verifier.verify(
            data=message_computer.compute_bytes_for_verifying(message),
            signature=message.signature
        )

    def recall_account_nonce(self, address: Address) -> int:
        return self.provider.get_account(address).nonce

    def send_transaction(self, transaction: Transaction) -> str:
        return self.provider.send_transaction(transaction)

    def await_completed_transaction(self, tx_hash: str) -> TransactionOnNetwork:
        provider = ProviderWrapper(self.provider)
        transaction_awaiter = TransactionAwaiter(provider)
        return transaction_awaiter.await_completed(tx_hash)

    def get_network_provider(self) -> Union[ApiNetworkProvider, ProxyNetworkProvider]:
        return self.provider

    # access to individual controllers
    def get_delegation_controller(self) -> DelegationController:
        return DelegationController(self.provider)

    def get_account_controller(self) -> AccountController:
        return AccountController(self.provider)

    def get_relayed_controller(self) -> RelayedController:
        return RelayedController(self.provider)

    def get_smart_contract_controller(self, abi: Any) -> SmartContractController:
        return SmartContractController(self.provider, abi)

    def get_token_management_controller(self) -> TokenManagementController:
        return TokenManagementController(self.provider)

    def get_transfers_controller(self) -> TransfersController:
        return TransfersController(self.provider)


class TestnetEntrypoint(NetworkEntrypoint):
    def __init__(self, url: Optional[str] = None, kind: Optional[str] = None) -> None:
        if url is None:
            url = TestnetConfig.api

        if kind is None:
            kind = TestnetConfig.kind
        super().__init__(url, kind, TestnetConfig.chain_id)


class DevnetEntrypoint(NetworkEntrypoint):
    def __init__(self, url: Optional[str] = None, kind: Optional[str] = None) -> None:
        if url is None:
            url = DevnetConfig.api

        if kind is None:
            kind = DevnetConfig.kind
        super().__init__(url, kind, DevnetConfig.chain_id)


class MainnetEntrypoint(NetworkEntrypoint):
    def __init__(self, url: Optional[str] = None, kind: Optional[str] = None) -> None:
        if url is None:
            url = MainnetConfig.api

        if kind is None:
            kind = MainnetConfig.kind
        super().__init__(url, kind, MainnetConfig.chain_id)


class ProviderWrapper:
    def __init__(self, provider: Union[ApiNetworkProvider, ProxyNetworkProvider]) -> None:
        self.provider = provider

    def get_transaction(self, tx_hash: str) -> TransactionOnNetwork:
        if isinstance(self.provider, ProxyNetworkProvider):
            return self.provider.get_transaction(tx_hash, True)
        return self.provider.get_transaction(tx_hash)
