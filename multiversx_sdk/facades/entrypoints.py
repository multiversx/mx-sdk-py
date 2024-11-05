from typing import Any, List, Optional, Protocol, Tuple, Union

from multiversx_sdk.controllers.account_controller import AccountController
from multiversx_sdk.controllers.delegation_controller import \
    DelegationController
from multiversx_sdk.controllers.relayed_controller import RelayedController
from multiversx_sdk.controllers.smart_contract_controller import \
    SmartContractController
from multiversx_sdk.controllers.token_management_controller import \
    TokenManagementController
from multiversx_sdk.controllers.transfers_controller import TransfersController
from multiversx_sdk.core.account import Account
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.message import Message, MessageComputer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.facades.config import (DevnetEntrypointConfig,
                                           MainnetEntrypointConfig,
                                           TestnetEntrypointConfig)
from multiversx_sdk.facades.errors import InvalidNetworkProviderKindError
from multiversx_sdk.network_providers.api_network_provider import \
    ApiNetworkProvider
from multiversx_sdk.network_providers.proxy_network_provider import \
    ProxyNetworkProvider
from multiversx_sdk.wallet.user_verifer import UserVerifier


class IAbi(Protocol):
    def encode_endpoint_input_parameters(self, endpoint_name: str, values: List[Any]) -> List[bytes]:
        ...

    def encode_constructor_input_parameters(self, values: List[Any]) -> List[bytes]:
        ...

    def encode_upgrade_constructor_input_parameters(self, values: List[Any]) -> List[bytes]:
        ...

    def decode_endpoint_output_parameters(self, endpoint_name: str, encoded_values: List[bytes]) -> List[Any]:
        ...


class NetworkEntrypoint:
    def __init__(self,
                 network_provider_url: str,
                 network_provider_kind: str,
                 chain_id: str) -> None:
        if network_provider_kind == "proxy":
            self.network_provider = ProxyNetworkProvider(network_provider_url)
        elif network_provider_kind == "api":
            self.network_provider = ApiNetworkProvider(network_provider_url)
        else:
            raise InvalidNetworkProviderKindError()

        self.chain_id = chain_id

    def sign_transaction(self, transaction: Transaction, account: Account):
        """Signs the transactions and applies the signature on the transaction."""
        tx_computer = TransactionComputer()
        transaction.signature = account.sign(tx_computer.compute_bytes_for_signing(transaction))

    def verify_transaction_signature(self, transaction: Transaction) -> bool:
        verifier = UserVerifier.from_address(transaction.sender)
        tx_computer = TransactionComputer()

        return verifier.verify(
            data=tx_computer.compute_bytes_for_verifying(transaction),
            signature=transaction.signature
        )

    def sign_message(self, message: Message, account: Account):
        """Signs the message and applies the signature on the message."""
        message_computer = MessageComputer()
        message.signature = account.sign(message_computer.compute_bytes_for_signing(message))

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
        return self.network_provider.get_account(address).nonce

    def send_transactions(self, transactions: list[Transaction]) -> Tuple[int, list[bytes]]:
        """
        Sends multiple transactions.

        Args:
            transactions (list[Transaction]): An iterable containing multiple transactions (e.g. a list of transactions).

        Returns:
            Tuple (int, list[bytes]): The integer indicates the total number of transactions sent, while the list contains the transactions hashes. If a transaction is not sent, the hash is empty.
        """
        return self.network_provider.send_transactions(transactions)

    def send_transaction(self, transaction: Transaction) -> bytes:
        return self.network_provider.send_transaction(transaction)

    def await_completed_transaction(self, tx_hash: Union[str, bytes]) -> TransactionOnNetwork:
        return self.network_provider.await_transaction_completed(tx_hash)

    def create_network_provider(self) -> Union[ApiNetworkProvider, ProxyNetworkProvider]:
        return self.network_provider

    def create_delegation_controller(self) -> DelegationController:
        return DelegationController(self.chain_id, self.network_provider)

    def create_account_controller(self) -> AccountController:
        return AccountController(self.chain_id)

    def create_relayed_controller(self) -> RelayedController:
        return RelayedController(self.chain_id)

    def create_smart_contract_controller(self, abi: Optional[IAbi] = None) -> SmartContractController:
        return SmartContractController(self.chain_id, self.network_provider, abi)

    def create_token_management_controller(self) -> TokenManagementController:
        return TokenManagementController(self.chain_id, self.network_provider)

    def create_transfers_controller(self) -> TransfersController:
        return TransfersController(self.chain_id)


class TestnetEntrypoint(NetworkEntrypoint):
    def __init__(self, url: Optional[str] = None, kind: Optional[str] = None) -> None:
        url = url or TestnetEntrypointConfig.network_provider_url

        kind = kind or TestnetEntrypointConfig.network_provider_kind

        super().__init__(url, kind, TestnetEntrypointConfig.chain_id)


class DevnetEntrypoint(NetworkEntrypoint):
    def __init__(self, url: Optional[str] = None, kind: Optional[str] = None) -> None:
        url = url or DevnetEntrypointConfig.network_provider_url

        kind = kind or DevnetEntrypointConfig.network_provider_kind

        super().__init__(url, kind, DevnetEntrypointConfig.chain_id)


class MainnetEntrypoint(NetworkEntrypoint):
    def __init__(self, url: Optional[str] = None, kind: Optional[str] = None) -> None:
        url = url or MainnetEntrypointConfig.network_provider_url

        kind = kind or MainnetEntrypointConfig.network_provider_kind

        super().__init__(url, kind, MainnetEntrypointConfig.chain_id)
