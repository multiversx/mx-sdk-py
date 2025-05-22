from typing import Optional, Protocol, Union

from multiversx_sdk.abi.address_value import AddressValue
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.string_value import StringValue
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.base_controller import BaseController
from multiversx_sdk.core.config import LibraryConfig
from multiversx_sdk.core.constants import GOVERNANCE_SMART_CONTRACT_ADDRESS_HEX
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.governance.governance_transactions_factory import (
    GovernanceTransactionsFactory,
)
from multiversx_sdk.governance.governance_transactions_outcome_parser import (
    GovernanceTransactionsOutcomeParser,
)
from multiversx_sdk.governance.resources import (
    CloseProposalOutcome,
    DelegatedVoteInfo,
    GovernanceConfig,
    NewProposalOutcome,
    ProposalInfo,
    VoteOutcome,
    VoteType,
)
from multiversx_sdk.network_providers.resources import AwaitingOptions
from multiversx_sdk.smart_contracts.smart_contract_controller import (
    SmartContractController,
)
from multiversx_sdk.smart_contracts.smart_contract_query import (
    SmartContractQuery,
    SmartContractQueryResponse,
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


class GovernanceController(BaseController):
    def __init__(self, chain_id: str, network_provider: INetworkProvider, address_hrp: Optional[str] = None) -> None:
        self._factory = GovernanceTransactionsFactory(TransactionsFactoryConfig(chain_id))
        self._network_provider = network_provider
        self._governance_contract = Address.new_from_hex(GOVERNANCE_SMART_CONTRACT_ADDRESS_HEX)
        self._sc_controller = SmartContractController(chain_id, network_provider)
        self._address_hrp = address_hrp if address_hrp else LibraryConfig.default_address_hrp
        self._serializer = Serializer()
        self._parser = GovernanceTransactionsOutcomeParser(address_hrp=self._address_hrp)

    def create_transaction_for_new_proposal(
        self,
        sender: IAccount,
        nonce: int,
        commit_hash: str,
        start_vote_epoch: int,
        end_vote_epoch: int,
        native_token_amount: int,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_new_proposal(
            sender=sender.address,
            commit_hash=commit_hash,
            start_vote_epoch=start_vote_epoch,
            end_vote_epoch=end_vote_epoch,
            native_token_amount=native_token_amount,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_new_proposal(self, transaction_on_network: TransactionOnNetwork) -> list[NewProposalOutcome]:
        return self._parser.parse_new_proposal(transaction_on_network)

    def await_completed_new_proposal(self, tx_hash: Union[str, bytes]) -> list[NewProposalOutcome]:
        transaction = self._network_provider.await_transaction_completed(tx_hash)
        return self.parse_new_proposal(transaction)

    def create_transaction_for_voting(
        self,
        sender: IAccount,
        nonce: int,
        proposal_nonce: int,
        vote: VoteType,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_voting(
            sender=sender.address, proposal_nonce=proposal_nonce, vote=vote
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_vote(self, transaction_on_network: TransactionOnNetwork) -> list[VoteOutcome]:
        return self._parser.parse_vote(transaction_on_network)

    def await_completed_vote(self, tx_hash: Union[str, bytes]) -> list[VoteOutcome]:
        transaction = self._network_provider.await_transaction_completed(tx_hash)
        return self.parse_vote(transaction)

    def create_transaction_for_closing_proposal(
        self,
        sender: IAccount,
        nonce: int,
        proposal_nonce: int,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_closing_proposal(
            sender=sender.address, proposal_nonce=proposal_nonce
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_close_proposal(self, transaction_on_network: TransactionOnNetwork) -> list[CloseProposalOutcome]:
        return self._parser.parse_close_proposal(transaction_on_network)

    def await_completed_close_proposal(self, tx_hash: Union[str, bytes]) -> list[CloseProposalOutcome]:
        transaction = self._network_provider.await_transaction_completed(tx_hash)
        return self.parse_close_proposal(transaction)

    def create_transaction_for_clearing_ended_proposals(
        self,
        sender: IAccount,
        nonce: int,
        proposers: list[Address],
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_clearing_ended_proposals(
            sender=sender.address, proposers=proposers
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_claiming_accumulated_fees(
        self,
        sender: IAccount,
        nonce: int,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_claiming_accumulated_fees(sender=sender.address)
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_changing_config(
        self,
        sender: IAccount,
        nonce: int,
        proposal_fee: int,
        lost_proposal_fee: int,
        min_quorum: int,
        min_veto_threshold: int,
        min_pass_threshold: int,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_changing_config(
            sender=sender.address,
            proposal_fee=proposal_fee,
            lost_proposal_fee=lost_proposal_fee,
            min_quorum=min_quorum,
            min_veto_threshold=min_veto_threshold,
            min_pass_threshold=min_pass_threshold,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def get_voting_power(self, address: Address) -> int:
        result = self._sc_controller.query(
            contract=self._governance_contract,
            function="viewVotingPower",
            arguments=[AddressValue.new_from_address(address)],
        )
        value = BigUIntValue()
        self._serializer.deserialize_parts(result, [value])
        return value.get_payload()

    def get_config(self) -> GovernanceConfig:
        result = self._sc_controller.query(
            contract=self._governance_contract,
            function="viewConfig",
            arguments=[],
        )

        proposal_fee = int(result[0].decode())
        min_quorum = float(result[1].decode())
        min_pass_threshold = float(result[2].decode())
        min_veto_threshold = float(result[3].decode())
        last_proposal_nonce = int(result[4].decode())

        return GovernanceConfig(proposal_fee, min_quorum, min_pass_threshold, min_veto_threshold, last_proposal_nonce)

    def get_proposal(self, proposal_nonce: int) -> ProposalInfo:
        result = self._sc_controller.query(
            contract=self._governance_contract,
            function="viewProposal",
            arguments=[BigUIntValue(proposal_nonce)],
        )

        proposal_cost = BigUIntValue()
        commit_hash = StringValue()
        nonce = BigUIntValue()
        issuer = AddressValue()
        start_vote_epoch = BigUIntValue()
        end_vote_epoch = BigUIntValue()
        quorum_stake = BigUIntValue()
        num_vote_yes = BigUIntValue()
        num_vote_no = BigUIntValue()
        num_vote_veto = BigUIntValue()
        num_vote_abstain = BigUIntValue()

        self._serializer.deserialize_parts(
            result[:11],
            [
                proposal_cost,
                commit_hash,
                nonce,
                issuer,
                start_vote_epoch,
                end_vote_epoch,
                quorum_stake,
                num_vote_yes,
                num_vote_no,
                num_vote_veto,
                num_vote_abstain,
            ],
        )

        proposal_closed = True if result[11].decode() == "true" else False
        proposal_passed = True if result[12].decode() == "true" else False

        return ProposalInfo(
            proposal_cost.get_payload(),
            commit_hash.get_payload(),
            nonce.get_payload(),
            Address(issuer.get_payload(), self._address_hrp),
            start_vote_epoch.get_payload(),
            end_vote_epoch.get_payload(),
            quorum_stake.get_payload(),
            num_vote_yes.get_payload(),
            num_vote_no.get_payload(),
            num_vote_veto.get_payload(),
            num_vote_abstain.get_payload(),
            proposal_closed,
            proposal_passed,
        )

    def get_delegated_vote_info(self, contract: Address, user: Address) -> DelegatedVoteInfo:
        result = self._sc_controller.query(
            contract=self._governance_contract,
            function="viewDelegatedVoteInfo",
            arguments=[AddressValue.new_from_address(contract), AddressValue.new_from_address(user)],
        )

        used_stake = BigUIntValue()
        used_power = BigUIntValue()
        total_stake = BigUIntValue()
        total_power = BigUIntValue()

        self._serializer.deserialize_parts(result, [used_stake, used_power, total_stake, total_power])

        return DelegatedVoteInfo(
            used_stake.get_payload(),
            used_power.get_payload(),
            total_stake.get_payload(),
            total_power.get_payload(),
        )
