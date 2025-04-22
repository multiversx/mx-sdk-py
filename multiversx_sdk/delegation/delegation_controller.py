from typing import Optional, Protocol, Sequence, Union

from multiversx_sdk.core import (
    Address,
    Transaction,
    TransactionOnNetwork,
    TransactionsFactoryConfig,
)
from multiversx_sdk.core.base_controller import BaseController
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.delegation.delegation_transactions_factory import (
    DelegationTransactionsFactory,
)
from multiversx_sdk.delegation.delegation_transactions_outcome_parser import (
    DelegationTransactionsOutcomeParser,
)
from multiversx_sdk.delegation.delegation_transactions_outcome_parser_types import (
    ClaimRewardsOutcome,
    CreateNewDelegationContractOutcome,
    DelegateOutcome,
    RedelegateRewardsOutcome,
    UndelegateOutcome,
)
from multiversx_sdk.network_providers.resources import AwaitingOptions
from multiversx_sdk.wallet.validator_keys import ValidatorPublicKey


# fmt: off
class INetworkProvider(Protocol):
    def await_transaction_completed(self, transaction_hash: Union[str, bytes], options: Optional[AwaitingOptions] = None) -> TransactionOnNetwork:
        ...
# fmt: on


class DelegationController(BaseController):
    def __init__(self, chain_id: str, network_provider: INetworkProvider) -> None:
        self.network_provider = network_provider
        self.factory = DelegationTransactionsFactory(TransactionsFactoryConfig(chain_id))
        self.parser = DelegationTransactionsOutcomeParser()

    def create_transaction_for_new_delegation_contract(
        self,
        sender: IAccount,
        nonce: int,
        total_delegation_cap: int,
        service_fee: int,
        amount: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_new_delegation_contract(
            sender=sender.address,
            total_delegation_cap=total_delegation_cap,
            service_fee=service_fee,
            amount=amount,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_create_new_delegation_contract(
        self, transaction_on_network: TransactionOnNetwork
    ) -> list[CreateNewDelegationContractOutcome]:
        return self.parser.parse_create_new_delegation_contract(transaction_on_network)

    def await_completed_create_new_delegation_contract(
        self, transaction_hash: Union[str, bytes]
    ) -> list[CreateNewDelegationContractOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_create_new_delegation_contract(transaction)

    def create_transaction_for_adding_nodes(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
        signed_messages: Sequence[bytes],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_adding_nodes(
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            signed_messages=signed_messages,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_removing_nodes(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_removing_nodes(
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_staking_nodes(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_staking_nodes(
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unbonding_nodes(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unbonding_nodes(
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unstaking_nodes(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unstaking_nodes(
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unjailing_nodes(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        public_keys: Sequence[ValidatorPublicKey],
        amount: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unjailing_nodes(
            sender=sender.address,
            delegation_contract=delegation_contract,
            public_keys=public_keys,
            amount=amount,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_changing_service_fee(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        service_fee: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_changing_service_fee(
            sender=sender.address,
            delegation_contract=delegation_contract,
            service_fee=service_fee,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_modifying_delegation_cap(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        delegation_cap: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_modifying_delegation_cap(
            sender=sender.address,
            delegation_contract=delegation_contract,
            delegation_cap=delegation_cap,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_setting_automatic_activation(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_automatic_activation(
            sender=sender.address, delegation_contract=delegation_contract
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unsetting_automatic_activation(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unsetting_automatic_activation(
            sender=sender.address, delegation_contract=delegation_contract
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_setting_cap_check_on_redelegate_rewards(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_cap_check_on_redelegate_rewards(
            sender=sender.address, delegation_contract=delegation_contract
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unsetting_cap_check_on_redelegate_rewards(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unsetting_cap_check_on_redelegate_rewards(
            sender=sender.address, delegation_contract=delegation_contract
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_setting_metadata(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        name: str,
        website: str,
        identifier: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_metadata(
            sender=sender.address,
            delegation_contract=delegation_contract,
            name=name,
            website=website,
            identifier=identifier,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_delegating(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        amount: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_delegating(
            sender=sender.address,
            delegation_contract=delegation_contract,
            amount=amount,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_delegate(self, transaction_on_network: TransactionOnNetwork) -> list[DelegateOutcome]:
        return self.parser.parse_delegate(transaction_on_network)

    def await_completed_delegate(self, transaction_hash: Union[str, bytes]) -> list[DelegateOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_delegate(transaction)

    def create_transaction_for_claiming_rewards(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_claiming_rewards(
            sender=sender.address, delegation_contract=delegation_contract
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_claim_rewards(self, transaction_on_network: TransactionOnNetwork) -> list[ClaimRewardsOutcome]:
        return self.parser.parse_claim_rewards(transaction_on_network)

    def await_completed_claim_rewards(self, transaction_hash: Union[str, bytes]) -> list[ClaimRewardsOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_claim_rewards(transaction)

    def create_transaction_for_redelegating_rewards(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_redelegating_rewards(
            sender=sender.address, delegation_contract=delegation_contract
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_redelegate_rewards(self, transaction_on_network: TransactionOnNetwork) -> list[RedelegateRewardsOutcome]:
        return self.parser.parse_redelegate_rewards(transaction_on_network)

    def await_completed_redelegate_rewards(self, transaction_hash: Union[str, bytes]) -> list[RedelegateRewardsOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_redelegate_rewards(transaction)

    def create_transaction_for_undelegating(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        amount: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_undelegating(
            sender=sender.address,
            delegation_contract=delegation_contract,
            amount=amount,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_undelegate(self, transaction_on_network: TransactionOnNetwork) -> list[UndelegateOutcome]:
        return self.parser.parse_undelegate(transaction_on_network)

    def await_completed_undelegate(self, transaction_hash: Union[str, bytes]) -> list[UndelegateOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_undelegate(transaction)

    def create_transaction_for_withdrawing(
        self,
        sender: IAccount,
        nonce: int,
        delegation_contract: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_withdrawing(
            sender=sender.address, delegation_contract=delegation_contract
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction
