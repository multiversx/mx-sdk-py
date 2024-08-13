from typing import List, Protocol, Sequence, Union

from multiversx_sdk.converters.transactions_converter import \
    TransactionsConverter
from multiversx_sdk.core.controllers.network_provider_wrapper import \
    ProviderWrapper
from multiversx_sdk.core.interfaces import IAddress, IValidatorPublicKey
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transactions_factories.delegation_transactions_factory import \
    DelegationTransactionsFactory
from multiversx_sdk.core.transactions_factories.transactions_factory_config import \
    TransactionsFactoryConfig
from multiversx_sdk.core.transactions_outcome_parsers.delegation_transactions_outcome_parser import \
    DelegationTransactionsOutcomeParser
from multiversx_sdk.core.transactions_outcome_parsers.delegation_transactions_outcome_parser_types import \
    CreateNewDelegationContractOutcome
from multiversx_sdk.network_providers.transaction_awaiter import \
    TransactionAwaiter
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork


class INetworkConfig(Protocol):
    chain_id: str


class INetworkProvider(Protocol):
    def get_network_config(self) -> INetworkConfig:
        ...


class IAccount(Protocol):
    address: IAddress

    def sign(self, data: bytes) -> bytes:
        ...


class DelegationController:
    def __init__(self, network_provider: INetworkProvider) -> None:
        self.chain_id: Union[str, None] = None
        self.factory: Union[DelegationTransactionsFactory, None] = None
        self.parser = DelegationTransactionsOutcomeParser()
        self.provider = network_provider
        self.tx_computer = TransactionComputer()

    def create_transaction_for_new_delegation_contract(self,
                                                       sender: IAccount,
                                                       nonce: int,
                                                       total_delegation_cap: int,
                                                       service_fee: int,
                                                       amount: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_new_delegation_contract(  # type: ignore
            sender=sender.address,
            total_delegation_cap=total_delegation_cap,
            service_fee=service_fee,
            amount=amount
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_create_new_delegation_contract(self,
                                             transaction_on_network: TransactionOnNetwork) -> List[CreateNewDelegationContractOutcome]:
        tx_converter = TransactionsConverter()
        tx_outcome = tx_converter.transaction_on_network_to_outcome(transaction_on_network)

        return self.parser.parse_create_new_delegation_contract(tx_outcome)

    def await_completed_create_new_delegation_contract(self, tx_hash: str) -> List[CreateNewDelegationContractOutcome]:
        provider = ProviderWrapper(self.provider)
        transaction_awaiter = TransactionAwaiter(provider)
        transaction = transaction_awaiter.await_completed(tx_hash)
        return self.parse_create_new_delegation_contract(transaction)

    def create_transaction_for_adding_nodes(self,
                                            sender: IAccount,
                                            nonce: int,
                                            delegation_contract: IAddress,
                                            public_keys: Sequence[IValidatorPublicKey],
                                            signed_messages: Sequence[bytes]) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_adding_nodes(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            signed_messages=signed_messages
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_removing_nodes(self,
                                              sender: IAccount,
                                              nonce: int,
                                              delegation_contract: IAddress,
                                              public_keys: Sequence[IValidatorPublicKey]) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_removing_nodes(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_staking_nodes(self,
                                             sender: IAccount,
                                             nonce: int,
                                             delegation_contract: IAddress,
                                             public_keys: Sequence[IValidatorPublicKey]) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_staking_nodes(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_unbonding_nodes(self,
                                               sender: IAccount,
                                               nonce: int,
                                               delegation_contract: IAddress,
                                               public_keys: Sequence[IValidatorPublicKey]) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_unbonding_nodes(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_unstaking_nodes(self,
                                               sender: IAccount,
                                               nonce: int,
                                               delegation_contract: IAddress,
                                               public_keys: Sequence[IValidatorPublicKey]) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_unstaking_nodes(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_unjailing_nodes(self,
                                               sender: IAccount,
                                               nonce: int,
                                               delegation_contract: IAddress,
                                               public_keys: Sequence[IValidatorPublicKey],
                                               amount: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_unjailing_nodes(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            amount=amount
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_changing_service_fee(self,
                                                    sender: IAccount,
                                                    nonce: int,
                                                    delegation_contract: IAddress,
                                                    service_fee: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_changing_service_fee(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract,
            service_fee=service_fee
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_modifying_delegation_cap(self,
                                                        sender: IAccount,
                                                        nonce: int,
                                                        delegation_contract: IAddress,
                                                        delegation_cap: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_modifying_delegation_cap(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract,
            delegation_cap=delegation_cap
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_setting_automatic_activation(self,
                                                            sender: IAccount,
                                                            nonce: int,
                                                            delegation_contract: IAddress) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_setting_automatic_activation(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_unsetting_automatic_activation(self,
                                                              sender: IAccount,
                                                              nonce: int,
                                                              delegation_contract: IAddress) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_unsetting_automatic_activation(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_setting_cap_check_on_redelegate_rewards(self,
                                                                       sender: IAccount,
                                                                       nonce: int,
                                                                       delegation_contract: IAddress) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_setting_cap_check_on_redelegate_rewards(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_unsetting_cap_check_on_redelegate_rewards(self,
                                                                         sender: IAccount,
                                                                         nonce: int,
                                                                         delegation_contract: IAddress) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_unsetting_cap_check_on_redelegate_rewards(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_setting_metadata(self,
                                                sender: IAccount,
                                                nonce: int,
                                                delegation_contract: IAddress,
                                                name: str,
                                                website: str,
                                                identifier: str) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_setting_metadata(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract,
            name=name,
            website=website,
            identifier=identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_delegating(self,
                                          sender: IAccount,
                                          nonce: int,
                                          delegation_contract: IAddress,
                                          amount: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_delegating(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract,
            amount=amount
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_claiming_rewards(self,
                                                sender: IAccount,
                                                nonce: int,
                                                delegation_contract: IAddress) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_claiming_rewards(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_redelegating_rewards(self,
                                                    sender: IAccount,
                                                    nonce: int,
                                                    delegation_contract: IAddress) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_redelegating_rewards(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_undelegating(self,
                                            sender: IAccount,
                                            nonce: int,
                                            delegation_contract: IAddress,
                                            amount: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_undelegating(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract,
            amount=amount
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_withdrawing(self,
                                           sender: IAccount,
                                           nonce: int,
                                           delegation_contract: IAddress) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_withdrawing(  # type: ignore
            sender=sender.address,
            delegation_contract=delegation_contract
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def _ensure_factory_is_initialized(self):
        if self.factory is None:
            self.chain_id = self.provider.get_network_config().chain_id
            config = TransactionsFactoryConfig(self.chain_id)
            self.factory = DelegationTransactionsFactory(config)
