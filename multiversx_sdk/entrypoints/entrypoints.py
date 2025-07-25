from typing import Optional, Union

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.account_management import AccountController
from multiversx_sdk.account_management.account_transactions_factory import (
    AccountTransactionsFactory,
)
from multiversx_sdk.accounts.account import Account
from multiversx_sdk.core import (
    Address,
    Message,
    MessageComputer,
    Transaction,
    TransactionComputer,
    TransactionOnNetwork,
)
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.delegation import DelegationController
from multiversx_sdk.delegation.delegation_transactions_factory import (
    DelegationTransactionsFactory,
)
from multiversx_sdk.entrypoints.config import (
    DevnetEntrypointConfig,
    LocalnetEntrypointConfig,
    MainnetEntrypointConfig,
    TestnetEntrypointConfig,
)
from multiversx_sdk.entrypoints.errors import InvalidNetworkProviderKindError
from multiversx_sdk.gas_estimator.gas_limit_estimator import GasLimitEstimator
from multiversx_sdk.governance.governance_controller import GovernanceController
from multiversx_sdk.governance.governance_transactions_factory import (
    GovernanceTransactionsFactory,
)
from multiversx_sdk.multisig.multisig_controller import MultisigController
from multiversx_sdk.multisig.multisig_transactions_factory import (
    MultisigTransactionsFactory,
)
from multiversx_sdk.network_providers import ApiNetworkProvider, ProxyNetworkProvider
from multiversx_sdk.network_providers.interface import INetworkProvider
from multiversx_sdk.smart_contracts.smart_contract_controller import (
    SmartContractController,
)
from multiversx_sdk.smart_contracts.smart_contract_transactions_factory import (
    SmartContractTransactionsFactory,
)
from multiversx_sdk.token_management.token_management_controller import (
    TokenManagementController,
)
from multiversx_sdk.token_management.token_management_transactions_factory import (
    TokenManagementTransactionsFactory,
)
from multiversx_sdk.transfers.transfer_transactions_factory import (
    TransferTransactionsFactory,
)
from multiversx_sdk.transfers.transfers_controller import TransfersController
from multiversx_sdk.wallet.user_keys import UserSecretKey
from multiversx_sdk.wallet.user_verifer import UserVerifier


class NetworkEntrypoint:
    def __init__(
        self,
        network_provider_url: Optional[str] = None,
        network_provider_kind: Optional[str] = None,
        chain_id: Optional[str] = None,
        network_provider: Optional[INetworkProvider] = None,
        with_gas_limit_estimator: Optional[bool] = None,
        gas_limit_multiplier: Optional[float] = None,
    ) -> None:
        self.chain_id = chain_id
        self.with_gas_limit_estimator = with_gas_limit_estimator
        self.gas_limit_multiplier = gas_limit_multiplier

        if network_provider:
            self.network_provider = network_provider
            return

        if not network_provider_url:
            raise Exception("network provider url not provided")

        if network_provider_kind == "proxy":
            self.network_provider = ProxyNetworkProvider(network_provider_url)
        elif network_provider_kind == "api":
            self.network_provider = ApiNetworkProvider(network_provider_url)
        else:
            raise InvalidNetworkProviderKindError()

    @classmethod
    def new_from_network_provider(
        cls, network_provider: INetworkProvider, chain_id: Optional[str] = None
    ) -> "NetworkEntrypoint":
        return cls(chain_id=chain_id, network_provider=network_provider)

    def create_account(self) -> Account:
        """Generates a new secret key and instantiates an account."""
        secret_key = UserSecretKey.generate()
        return Account(secret_key)

    def get_airdrop(self, address: Address) -> None:
        """Get xEGLD tokens on Devnet or Testnet."""
        raise NotImplementedError("The faucet is unavailable at the moment.")

    def verify_transaction_signature(self, transaction: Transaction) -> bool:
        verifier = UserVerifier.from_address(transaction.sender)
        tx_computer = TransactionComputer()

        return verifier.verify(
            data=tx_computer.compute_bytes_for_verifying(transaction),
            signature=transaction.signature,
        )

    def verify_message_signature(self, message: Message) -> bool:
        if message.address is None:
            raise Exception("`address` property of Message is not set")

        verifier = UserVerifier.from_address(message.address)
        message_computer = MessageComputer()

        return verifier.verify(
            data=message_computer.compute_bytes_for_verifying(message),
            signature=message.signature,
        )

    def recall_account_nonce(self, address: Address) -> int:
        return self.network_provider.get_account(address).nonce

    def send_transactions(self, transactions: list[Transaction]) -> tuple[int, list[bytes]]:
        """
        Sends multiple transactions.

        Args:
            transactions (list[Transaction]): An iterable containing multiple transactions (e.g. a list of transactions).

        Returns:
            tuple (int, list[bytes]): The integer indicates the total number of transactions sent, while the list contains the transactions hashes. If a transaction is not sent, the hash is empty.
        """
        return self.network_provider.send_transactions(transactions)

    def send_transaction(self, transaction: Transaction) -> bytes:
        return self.network_provider.send_transaction(transaction)

    def await_transaction_completed(self, tx_hash: Union[str, bytes]) -> TransactionOnNetwork:
        return self.network_provider.await_transaction_completed(tx_hash)

    def get_transaction(self, tx_hash: Union[str, bytes]) -> TransactionOnNetwork:
        return self.network_provider.get_transaction(tx_hash)

    def create_network_provider(
        self,
    ) -> INetworkProvider:
        return self.network_provider

    def create_gas_limit_estimator(self) -> GasLimitEstimator:
        return GasLimitEstimator(network_provider=self.network_provider, gas_multiplier=self.gas_limit_multiplier)

    def create_delegation_controller(self) -> DelegationController:
        return DelegationController(
            self._get_chain_id(),
            self.network_provider,
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_delegation_transactions_factory(self) -> DelegationTransactionsFactory:
        return DelegationTransactionsFactory(
            TransactionsFactoryConfig(self._get_chain_id()),
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_account_controller(self) -> AccountController:
        return AccountController(
            self._get_chain_id(),
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_account_transactions_factory(self) -> AccountTransactionsFactory:
        return AccountTransactionsFactory(
            TransactionsFactoryConfig(self._get_chain_id()),
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_smart_contract_controller(self, abi: Optional[Abi] = None) -> SmartContractController:
        return SmartContractController(
            self._get_chain_id(),
            self.network_provider,
            abi,
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_smart_contract_transactions_factory(self, abi: Optional[Abi] = None) -> SmartContractTransactionsFactory:
        return SmartContractTransactionsFactory(
            config=TransactionsFactoryConfig(self._get_chain_id()),
            abi=abi,
            gas_limit_estimator=self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_token_management_controller(self) -> TokenManagementController:
        return TokenManagementController(
            self._get_chain_id(),
            self.network_provider,
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_token_management_transactions_factory(
        self,
    ) -> TokenManagementTransactionsFactory:
        return TokenManagementTransactionsFactory(
            TransactionsFactoryConfig(self._get_chain_id()),
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_transfers_controller(self) -> TransfersController:
        return TransfersController(
            self._get_chain_id(),
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_transfers_transactions_factory(self) -> TransferTransactionsFactory:
        return TransferTransactionsFactory(
            TransactionsFactoryConfig(self._get_chain_id()),
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_multisig_controller(self, abi: Abi, address_hrp: Optional[str] = None) -> MultisigController:
        return MultisigController(
            self._get_chain_id(),
            self.network_provider,
            abi,
            address_hrp,
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_multisig_transactions_factory(self, abi: Abi) -> MultisigTransactionsFactory:
        return MultisigTransactionsFactory(
            TransactionsFactoryConfig(self._get_chain_id()),
            abi,
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_governance_controller(self, address_hrp: Optional[str] = None) -> GovernanceController:
        return GovernanceController(
            self._get_chain_id(),
            self.network_provider,
            address_hrp,
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def create_governance_transactions_factory(self) -> GovernanceTransactionsFactory:
        return GovernanceTransactionsFactory(
            TransactionsFactoryConfig(self._get_chain_id()),
            self.create_gas_limit_estimator() if self.with_gas_limit_estimator else None,
        )

    def _get_chain_id(self) -> str:
        if self.chain_id:
            return self.chain_id

        self.chain_id = self.network_provider.get_network_config().chain_id
        return self.chain_id


class TestnetEntrypoint(NetworkEntrypoint):
    def __init__(
        self,
        url: Optional[str] = None,
        kind: Optional[str] = None,
        with_gas_limit_estimator: Optional[bool] = None,
        gas_limit_multiplier: Optional[float] = None,
    ) -> None:
        url = url or TestnetEntrypointConfig.network_provider_url

        kind = kind or TestnetEntrypointConfig.network_provider_kind

        super().__init__(
            network_provider_url=url,
            network_provider_kind=kind,
            chain_id=TestnetEntrypointConfig.chain_id,
            with_gas_limit_estimator=with_gas_limit_estimator,
            gas_limit_multiplier=gas_limit_multiplier,
        )


class DevnetEntrypoint(NetworkEntrypoint):
    def __init__(
        self,
        url: Optional[str] = None,
        kind: Optional[str] = None,
        with_gas_limit_estimator: Optional[bool] = None,
        gas_limit_multiplier: Optional[float] = None,
    ) -> None:
        url = url or DevnetEntrypointConfig.network_provider_url

        kind = kind or DevnetEntrypointConfig.network_provider_kind

        super().__init__(
            network_provider_url=url,
            network_provider_kind=kind,
            chain_id=DevnetEntrypointConfig.chain_id,
            with_gas_limit_estimator=with_gas_limit_estimator,
            gas_limit_multiplier=gas_limit_multiplier,
        )


class MainnetEntrypoint(NetworkEntrypoint):
    def __init__(
        self,
        url: Optional[str] = None,
        kind: Optional[str] = None,
        with_gas_limit_estimator: Optional[bool] = None,
        gas_limit_multiplier: Optional[float] = None,
    ) -> None:
        url = url or MainnetEntrypointConfig.network_provider_url

        kind = kind or MainnetEntrypointConfig.network_provider_kind

        super().__init__(
            network_provider_url=url,
            network_provider_kind=kind,
            chain_id=MainnetEntrypointConfig.chain_id,
            with_gas_limit_estimator=with_gas_limit_estimator,
            gas_limit_multiplier=gas_limit_multiplier,
        )


class LocalnetEntrypoint(NetworkEntrypoint):
    def __init__(
        self,
        url: Optional[str] = None,
        kind: Optional[str] = None,
        with_gas_limit_estimator: Optional[bool] = None,
        gas_limit_multiplier: Optional[float] = None,
    ) -> None:
        url = url or LocalnetEntrypointConfig.network_provider_url

        kind = kind or LocalnetEntrypointConfig.network_provider_kind

        super().__init__(
            network_provider_url=url,
            network_provider_kind=kind,
            chain_id=LocalnetEntrypointConfig.chain_id,
            with_gas_limit_estimator=with_gas_limit_estimator,
            gas_limit_multiplier=gas_limit_multiplier,
        )
