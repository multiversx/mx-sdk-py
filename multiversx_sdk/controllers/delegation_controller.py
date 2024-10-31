from typing import List, Optional, Protocol, Sequence, Union

from multiversx_sdk.controllers.interfaces import IAccount
from multiversx_sdk.core.interfaces import IAddress, IValidatorPublicKey
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.core.transactions_factories import (
    DelegationTransactionsFactory, TransactionsFactoryConfig)
from multiversx_sdk.core.transactions_outcome_parsers.delegation_transactions_outcome_parser import (
    CreateNewDelegationContractOutcome, DelegationTransactionsOutcomeParser)
from multiversx_sdk.network_providers.resources import AwaitingOptions


class INetworkProvider(Protocol):
    def await_transaction_completed(
            self, transaction_hash: Union[str, bytes],
            options: Optional[AwaitingOptions] = None) -> TransactionOnNetwork:
        ...


class DelegationController:
    def __init__(self, chain_id: str, network_provider: INetworkProvider) -> None:
        self.network_provider = network_provider
        self.factory = DelegationTransactionsFactory(TransactionsFactoryConfig(chain_id))
        self.parser = DelegationTransactionsOutcomeParser()
        self.tx_computer = TransactionComputer()

    def create_transaction_for_new_delegation_contract(self,
                                                       sender: IAccount,
                                                       nonce: int,
                                                       total_delegation_cap: int,
                                                       service_fee: int,
                                                       amount: int) -> Transaction:
        transaction = self.factory.create_transaction_for_new_delegation_contract(
            sender=sender.address,
            total_delegation_cap=total_delegation_cap,
            service_fee=service_fee,
            amount=amount
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_create_new_delegation_contract(
            self, transaction_on_network: TransactionOnNetwork) -> List[CreateNewDelegationContractOutcome]:
        return self.parser.parse_create_new_delegation_contract(transaction_on_network)

    def await_completed_create_new_delegation_contract(self, tx_hash: str) -> List[CreateNewDelegationContractOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_create_new_delegation_contract(transaction)

    def create_transaction_for_adding_nodes(self,
                                            sender: IAccount,
                                            nonce: int,
                                            delegation_contract: IAddress,
                                            public_keys: Sequence[IValidatorPublicKey],
                                            signed_messages: Sequence[bytes]) -> Transaction:
        transaction = self.factory.create_transaction_for_adding_nodes(
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
        transaction = self.factory.create_transaction_for_removing_nodes(
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
        transaction = self.factory.create_transaction_for_staking_nodes(
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
        transaction = self.factory.create_transaction_for_unbonding_nodes(
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
        transaction = self.factory.create_transaction_for_unstaking_nodes(
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
        transaction = self.factory.create_transaction_for_unjailing_nodes(
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
        transaction = self.factory.create_transaction_for_changing_service_fee(
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
        transaction = self.factory.create_transaction_for_modifying_delegation_cap(
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
        transaction = self.factory.create_transaction_for_setting_automatic_activation(
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
        transaction = self.factory.create_transaction_for_unsetting_automatic_activation(
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
        transaction = self.factory.create_transaction_for_setting_cap_check_on_redelegate_rewards(
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
        transaction = self.factory.create_transaction_for_unsetting_cap_check_on_redelegate_rewards(
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
        transaction = self.factory.create_transaction_for_setting_metadata(
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
        transaction = self.factory.create_transaction_for_delegating(
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
        transaction = self.factory.create_transaction_for_claiming_rewards(
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
        transaction = self.factory.create_transaction_for_redelegating_rewards(
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
        transaction = self.factory.create_transaction_for_undelegating(
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
        transaction = self.factory.create_transaction_for_withdrawing(
            sender=sender.address,
            delegation_contract=delegation_contract
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction
