from pathlib import Path
from typing import Any, Optional, Protocol, Union

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.base_controller import BaseController
from multiversx_sdk.core.config import LibraryConfig
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.multisig.multisig_transactions_factory import (
    MultisigTransactionsFactory,
)
from multiversx_sdk.multisig.multisig_transactions_outcome_parser import (
    MultisigTransactionsOutcomeParser,
)
from multiversx_sdk.multisig.resources import Action, ActionFullInfo, UserRole
from multiversx_sdk.network_providers.resources import AwaitingOptions
from multiversx_sdk.smart_contracts import (
    SmartContractController,
    SmartContractQuery,
    SmartContractQueryResponse,
)
from multiversx_sdk.smart_contracts.smart_contract_transactions_outcome_parser_types import (
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


class MultisigController(BaseController):
    def __init__(
        self,
        chain_id: str,
        network_provider: INetworkProvider,
        abi: Optional[Abi] = None,
        address_hrp: Optional[str] = None,
    ) -> None:
        self._network_provider = network_provider
        self._factory = MultisigTransactionsFactory(TransactionsFactoryConfig(chain_id), abi=abi)
        self._parser = MultisigTransactionsOutcomeParser(abi=abi)
        self._smart_contract_controller = SmartContractController(
            chain_id=chain_id, network_provider=network_provider, abi=abi
        )
        self._address_hrp = address_hrp if address_hrp else LibraryConfig.default_address_hrp

    def create_transaction_for_deploy(
        self,
        sender: IAccount,
        nonce: int,
        bytecode: Union[Path, bytes],
        quorum: int,
        board: list[Address],
        gas_limit: int,
        is_upgradeable: bool = True,
        is_readable: bool = True,
        is_payable: bool = False,
        is_payable_by_contract: bool = True,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_deploy(
            sender=sender.address,
            bytecode=bytecode,
            gas_limit=gas_limit,
            quorum=quorum,
            board=board,
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_contract,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_deploy(self, transaction_on_network: TransactionOnNetwork) -> SmartContractDeployOutcome:
        return self._parser.parse_deploy(transaction_on_network)

    def await_completed_deploy(self, tx_hash: Union[str, bytes]) -> SmartContractDeployOutcome:
        transaction = self._network_provider.await_transaction_completed(tx_hash)
        return self.parse_deploy(transaction)

    def create_transaction_for_deposit(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        gas_limit: int,
        native_token_amount: int = 0,
        token_transfers: Optional[list[TokenTransfer]] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_deposit(
            sender=sender.address,
            contract=contract,
            gas_limit=gas_limit,
            native_token_amount=native_token_amount,
            token_transfers=token_transfers,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_discard_action(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_discard_action(
            sender=sender.address,
            contract=contract,
            gas_limit=gas_limit,
            action_id=action_id,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_discard_batch(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        actions_ids: list[int],
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_discard_batch(
            sender=sender.address,
            contract=contract,
            gas_limit=gas_limit,
            action_ids=actions_ids,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def get_quorum(self, contract: Address) -> int:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="getQuorum",
            arguments=[],
        )

        return value

    def get_num_board_members(self, contract: Address) -> int:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="getNumBoardMembers",
            arguments=[],
        )

        return value

    def get_num_groups(self, contract: Address) -> int:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="getNumGroups",
            arguments=[],
        )

        return value

    def get_num_proposers(self, contract: Address) -> int:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="getNumProposers",
            arguments=[],
        )

        return value

    def get_action_group(self, contract: Address, group_id: int) -> list[int]:
        values = self._smart_contract_controller.query(
            contract=contract,
            function="getActionGroup",
            arguments=[group_id],
        )

        return values

    def get_last_group_action_id(self, contract: Address) -> int:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="getLastGroupActionId",
            arguments=[],
        )

        return value

    def get_action_last_index(self, contract: Address) -> int:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="getActionLastIndex",
            arguments=[],
        )

        return value

    def create_transaction_for_propose_add_board_member(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        board_member: Address,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_propose_add_board_member(
            sender=sender.address,
            contract=contract,
            board_member=board_member,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_propose_add_proposer(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        proposer: Address,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_propose_add_proposer(
            sender=sender.address,
            contract=contract,
            proposer=proposer,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_propose_remove_user(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        user: Address,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_propose_remove_user(
            sender=sender.address,
            contract=contract,
            user=user,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_propose_change_quorum(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        new_quorum: int,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_propose_change_quorum(
            sender=sender.address,
            contract=contract,
            quorum=new_quorum,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_propose_transfer_execute(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        receiver: Address,
        gas_limit: int,
        native_token_amount: int,
        opt_gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
        function: Optional[str] = None,
        arguments: Optional[list[Any]] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        """Propose a transaction in which the contract will perform a transfer-execute call.
        Can send EGLD without calling anything.
        Can call smart contract endpoints directly.
        Doesn't really work with builtin functions."""
        transaction = self._factory.create_transaction_for_propose_transfer_execute(
            sender=sender.address,
            contract=contract,
            receiver=receiver,
            native_token_amount=native_token_amount,
            gas_limit=gas_limit,
            opt_gas_limit=opt_gas_limit,
            abi=abi,
            function=function,
            arguments=arguments,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_propose_transfer_execute_esdt(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        receiver: Address,
        token_transfers: list[TokenTransfer],
        gas_limit: int,
        opt_gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
        function: Optional[str] = None,
        arguments: Optional[list[Any]] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_propose_transfer_esdt_execute(
            sender=sender.address,
            contract=contract,
            receiver=receiver,
            token_transfers=token_transfers,
            gas_limit=gas_limit,
            opt_gas_limit=opt_gas_limit,
            abi=abi,
            function=function,
            arguments=arguments,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_propose_async_call(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        receiver: Address,
        gas_limit: int,
        native_token_amount: int = 0,
        token_transfers: Optional[list[TokenTransfer]] = None,
        opt_gas_limit: Optional[int] = None,
        abi: Optional[Abi] = None,
        function: Optional[str] = None,
        arguments: Optional[list[Any]] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_propose_async_call(
            sender=sender.address,
            contract=contract,
            receiver=receiver,
            gas_limit=gas_limit,
            native_token_amount=native_token_amount,
            token_transfers=token_transfers,
            opt_gas_limit=opt_gas_limit,
            abi=abi,
            function=function,
            arguments=arguments,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_propose_contract_deploy_from_source(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        gas_limit: int,
        contract_to_copy: Address,
        native_token_amount: int = 0,
        arguments: Optional[list[Any]] = None,
        is_upgradeable: bool = True,
        is_readable: bool = True,
        is_payable: bool = False,
        is_payable_by_sc: bool = True,
        abi: Optional[Abi] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_contract_deploy_from_source(
            sender=sender.address,
            contract=contract,
            gas_limit=gas_limit,
            contract_to_copy=contract_to_copy,
            native_token_amount=native_token_amount,
            arguments=arguments,
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_sc,
            abi=abi,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_propose_contract_upgrade_from_source(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        contract_to_upgrade: Address,
        contract_to_copy: Address,
        gas_limit: int,
        arguments: Optional[list[Any]] = None,
        native_token_amount: int = 0,
        is_upgradeable: bool = True,
        is_readable: bool = True,
        is_payable: bool = False,
        is_payable_by_sc: bool = True,
        abi: Optional[Abi] = None,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_contract_upgrade_from_source(
            sender=sender.address,
            contract=contract,
            contract_to_upgrade=contract_to_upgrade,
            contract_to_copy=contract_to_copy,
            gas_limit=gas_limit,
            arguments=arguments,
            native_token_amount=native_token_amount,
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_sc,
            abi=abi,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_propose_batch(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        actions: list[Action],
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        return self._factory.create_transaction_for_propose_batch(
            sender=sender.address,
            contract=contract,
            actions=actions,
            gas_limit=gas_limit,
        )

    def create_transaction_for_sign_action(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_sign_action(
            sender=sender.address,
            contract=contract,
            action_id=action_id,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_sign_batch(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        batch_id: int,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_sign_batch(
            sender=sender.address,
            contract=contract,
            batch_id=batch_id,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_sign_and_perform(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_sign_and_perform(
            sender=sender.address,
            contract=contract,
            action_id=action_id,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_sign_batch_and_perform(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        batch_id: int,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_sign_batch_and_perform(
            sender=sender.address,
            contract=contract,
            batch_id=batch_id,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unsign_action(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_unsign_action(
            sender=sender.address,
            contract=contract,
            action_id=action_id,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unsign_batch(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        batch_id: int,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_unsign_batch(
            sender=sender.address,
            contract=contract,
            batch_id=batch_id,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def is_signed_by(
        self,
        contract: Address,
        user: Address,
        action_id: int,
    ) -> bool:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="signed",
            arguments=[user, action_id],
        )

        return value

    def create_transaction_for_unsign_for_outdated_board_members(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        outdated_board_members: list[int],
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_unsign_for_outdated_board_members(
            sender=sender.address,
            contract=contract,
            action_id=action_id,
            outdated_board_members=outdated_board_members,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def is_quorum_reached(self, contract: Address, action_id: int) -> bool:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="quorumReached",
            arguments=[action_id],
        )

        return value

    def create_transaction_for_perform_action(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        action_id: int,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_perform_action(
            sender=sender.address,
            contract=contract,
            action_id=action_id,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_perform_batch(
        self,
        sender: IAccount,
        nonce: int,
        contract: Address,
        batch_id: int,
        gas_limit: int,
        gas_price: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
    ) -> Transaction:
        transaction = self._factory.create_transaction_for_perform_batch(
            sender=sender.address,
            contract=contract,
            batch_id=batch_id,
            gas_limit=gas_limit,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def get_pending_actions_full_info(self, contract: Address) -> list[ActionFullInfo]:
        [values] = self._smart_contract_controller.query(
            contract=contract,
            function="getPendingActionFullInfo",
            # For now, we don't support the `opt_range` argument.
            arguments=[None],
        )

        actions = [ActionFullInfo.new_from_object(value) for value in values]
        return actions

    def get_user_role(self, contract: Address, user: Address) -> UserRole:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="userRole",
            arguments=[user],
        )

        return UserRole(int(value))

    def get_all_board_members(self, contract: Address) -> list[Address]:
        [public_keys] = self._smart_contract_controller.query(
            contract=contract,
            function="getAllBoardMembers",
            arguments=[],
        )

        return [Address(value, self._address_hrp) for value in public_keys]

    def get_all_proposers(self, contract: Address) -> list[Address]:
        [public_keys] = self._smart_contract_controller.query(
            contract=contract,
            function="getAllProposers",
            arguments=[],
        )

        return [Address(value, self._address_hrp) for value in public_keys]

    def get_action_data(self, contract: Address, action_id: int) -> list[Address]:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="getActionData",
            arguments=[action_id],
        )

        return value

    def get_action_signers(self, contract: Address, action_id: int) -> list[Address]:
        [public_keys] = self._smart_contract_controller.query(
            contract=contract,
            function="getActionSigners",
            arguments=[action_id],
        )

        return [Address(value, self._address_hrp) for value in public_keys]

    def get_action_signer_count(self, contract: Address, action_id: int) -> int:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="getActionValidSignerCount",
            arguments=[action_id],
        )

        return value

    def get_action_valid_signer_count(self, contract: Address, action_id: int) -> int:
        [value] = self._smart_contract_controller.query(
            contract=contract,
            function="getActionSignerCount",
            arguments=[action_id],
        )

        return value

    def parse_execute_propose_any(self, transaction_on_network: TransactionOnNetwork) -> int:
        return self._parser.parse_execute_propose_any(transaction_on_network)

    def await_completed_execute_propose_any(self, tx_hash: Union[str, bytes]) -> int:
        transaction = self._network_provider.await_transaction_completed(tx_hash)
        return self.parse_execute_propose_any(transaction)

    def parse_execute_perform(self, transaction_on_network: TransactionOnNetwork) -> Optional[Address]:
        return self._parser.parse_execute_perform(transaction_on_network)

    def await_completed_execute_perform(self, tx_hash: Union[str, bytes]) -> Optional[Address]:
        transaction = self._network_provider.await_transaction_completed(tx_hash)
        return self.parse_execute_perform(transaction)
