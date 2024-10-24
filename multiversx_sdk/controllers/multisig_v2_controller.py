from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from multiversx_sdk.controllers.interfaces import IAbi, IAccount
from multiversx_sdk.controllers.multisig_v2_resources import (
    ActionFullInfo, ProposeAsyncCallInput, ProposeSCDeployFromSourceInput,
    ProposeSCUpgradeFromSourceInput, ProposeTransferExecuteEsdtInput,
    ProposeTransferExecuteInput, UserRole)
from multiversx_sdk.controllers.smart_contract_controller import \
    INetworkProvider
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.smart_contract_queries_controller import \
    SmartContractQueriesController
from multiversx_sdk.core.tokens import TokenTransfer
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.core.transactions_factories import (
    SmartContractTransactionsFactory, TransactionsFactoryConfig)
from multiversx_sdk.core.transactions_outcome_parsers import \
    SmartContractTransactionsOutcomeParser
from multiversx_sdk.core.transactions_outcome_parsers.smart_contract_transactions_outcome_parser_types import \
    ParsedSmartContractCallOutcome
from multiversx_sdk.network_providers.constants import DEFAULT_ADDRESS_HRP


class MultisigV2Controller:
    def __init__(self, chain_id: str, network_provider: INetworkProvider, abi: IAbi) -> None:
        self.network_provider = network_provider
        self.factory = SmartContractTransactionsFactory(TransactionsFactoryConfig(chain_id), abi=abi)
        self.parser = SmartContractTransactionsOutcomeParser(abi=abi)
        self.transaction_computer = TransactionComputer()
        self.query_controller = SmartContractQueriesController(
            network_provider=network_provider,
            abi=abi
        )

    def create_transaction_for_deploy(self,
                                      sender: IAccount,
                                      nonce: int,
                                      bytecode: Union[Path, bytes],
                                      gas_limit: int,
                                      quorum: int,
                                      board: list[IAddress],
                                      is_upgradeable: bool = True,
                                      is_readable: bool = True,
                                      is_payable: bool = False,
                                      is_payable_by_contract: bool = True) -> Transaction:
        transaction = self.factory.create_transaction_for_deploy(
            sender=sender.address,
            bytecode=bytecode,
            gas_limit=gas_limit,
            arguments=[quorum, board],
            is_upgradeable=is_upgradeable,
            is_readable=is_readable,
            is_payable=is_payable,
            is_payable_by_sc=is_payable_by_contract,
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_deploy(self, transaction_on_network: TransactionOnNetwork) -> Address:
        outcome = self.parser.parse_deploy(transaction_on_network)
        return Address.new_from_bech32(outcome.contracts[0].address)

    def await_completed_deploy(self, tx_hash: str) -> Address:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_deploy(transaction)

    def create_transaction_for_deposit(self,
                                       sender: IAccount,
                                       nonce: int,
                                       contract: IAddress,
                                       gas_limit: int,
                                       native_transfer_amount: int = 0,
                                       token_transfers: Optional[List[TokenTransfer]] = None) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="deposit",
            gas_limit=gas_limit,
            arguments=[],
            native_transfer_amount=native_transfer_amount,
            token_transfers=token_transfers or []
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_discard_action(self,
                                              sender: IAccount,
                                              nonce: int,
                                              contract: IAddress,
                                              gas_limit: int,
                                              action_id: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="discardAction",
            gas_limit=gas_limit,
            arguments=[action_id],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_discard_batch(self,
                                             sender: IAccount,
                                             nonce: int,
                                             contract: IAddress,
                                             gas_limit: int,
                                             actions_ids: list[int]) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="discardBatch",
            gas_limit=gas_limit,
            arguments=[actions_ids],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def get_quorum(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getQuorum",
            arguments=[],
        )

        return value

    def get_num_board_members(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getNumBoardMembers",
            arguments=[],
        )

        return value

    def get_num_groups(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getNumGroups",
            arguments=[],
        )

        return value

    def get_num_proposers(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getNumProposers",
            arguments=[],
        )

        return value

    def get_action_group(self, contract: IAddress, group_id: int) -> list[int]:
        values = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getActionGroup",
            arguments=[group_id],
        )

        return values

    def get_last_group_action_id(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getLastGroupActionId",
            arguments=[],
        )

        return value

    def get_action_last_index(self, contract: IAddress) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getActionLastIndex",
            arguments=[],
        )

        return value

    def create_transaction_for_propose_add_board_member(self,
                                                        sender: IAccount,
                                                        nonce: int,
                                                        contract: IAddress,
                                                        gas_limit: int,
                                                        board_member: IAddress,) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeAddBoardMember",
            gas_limit=gas_limit,
            arguments=[board_member],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_propose_add_proposer(self,
                                                    sender: IAccount,
                                                    nonce: int,
                                                    contract: IAddress,
                                                    gas_limit: int,
                                                    proposer: IAddress) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeAddProposer",
            gas_limit=gas_limit,
            arguments=[proposer],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_propose_remove_user(self,
                                                   sender: IAccount,
                                                   nonce: int,
                                                   contract: IAddress,
                                                   gas_limit: int,
                                                   user: IAddress) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeRemoveUser",
            gas_limit=gas_limit,
            arguments=[user],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_propose_change_quorum(self,
                                                     sender: IAccount,
                                                     nonce: int,
                                                     contract: IAddress,
                                                     gas_limit: int,
                                                     new_quorum: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeChangeQuorum",
            gas_limit=gas_limit,
            arguments=[new_quorum],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_propose_transfer_execute(self,
                                                        sender: IAccount,
                                                        nonce: int,
                                                        contract: IAddress,
                                                        gas_limit: int,
                                                        input: ProposeTransferExecuteInput) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeTransferExecute",
            gas_limit=gas_limit,
            arguments=[input.to, input.egld_amount, input.opt_gas_limit, input.function_call],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_propose_transfer_execute_esdt(self,
                                                             sender: IAccount,
                                                             nonce: int,
                                                             contract: IAddress,
                                                             gas_limit: int,
                                                             input: ProposeTransferExecuteEsdtInput) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeTransferExecuteEsdt",
            gas_limit=gas_limit,
            arguments=[input.to, input.tokens, input.opt_gas_limit, input.function_call],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_propose_async_call(self,
                                                  sender: IAccount,
                                                  nonce: int,
                                                  contract: IAddress,
                                                  gas_limit: int,
                                                  input: ProposeAsyncCallInput) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeAsyncCall",
            gas_limit=gas_limit,
            arguments=[input.to, input.egld_amount, input.opt_gas_limit, input.function_call],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_propose_deploy_contract_from_source(self,
                                                                   sender: IAccount,
                                                                   nonce: int,
                                                                   contract: IAddress,
                                                                   gas_limit: int,
                                                                   input: ProposeSCDeployFromSourceInput) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeSCDeployFromSource",
            gas_limit=gas_limit,
            arguments=[input.amount, input.source, input.code_metadata, input.arguments],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_propose_upgrade_contract_from_source(self,
                                                                    sender: IAccount,
                                                                    nonce: int,
                                                                    contract: IAddress,
                                                                    gas_limit: int,
                                                                    input: ProposeSCUpgradeFromSourceInput) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="proposeSCUpgradeFromSource",
            gas_limit=gas_limit,
            arguments=[input.sc_address, input.amount, input.source, input.code_metadata, input.arguments],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_propose_batch(self,
                                             sender: IAccount,
                                             nonce: int,
                                             contract: IAddress,
                                             gas_limit: int,
                                             actions: list[Any]) -> Transaction:
        raise NotImplementedError("Not implemented yet")

    def create_transaction_for_sign(self,
                                    sender: IAccount,
                                    nonce: int,
                                    contract: IAddress,
                                    gas_limit: int,
                                    action_id: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="sign",
            gas_limit=gas_limit,
            arguments=[action_id],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_sign_batch(self,
                                          sender: IAccount,
                                          nonce: int,
                                          contract: IAddress,
                                          gas_limit: int,
                                          group_id: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="signBatch",
            gas_limit=gas_limit,
            arguments=[group_id],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_sign_and_perform(self,
                                                sender: IAccount,
                                                nonce: int,
                                                contract: IAddress,
                                                gas_limit: int,
                                                action_id: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="signAndPerform",
            gas_limit=gas_limit,
            arguments=[action_id],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_sign_batch_and_perform(self,
                                                      sender: IAccount,
                                                      nonce: int,
                                                      contract: IAddress,
                                                      gas_limit: int,
                                                      group_id: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="signBatchAndPerform",
            gas_limit=gas_limit,
            arguments=[group_id],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_unsign(self,
                                      sender: IAccount,
                                      nonce: int,
                                      contract: IAddress,
                                      gas_limit: int,
                                      action_id: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="unsign",
            gas_limit=gas_limit,
            arguments=[action_id],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_unsign_batch(self,
                                            sender: IAccount,
                                            nonce: int,
                                            contract: IAddress,
                                            gas_limit: int,
                                            group_id: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="unsignBatch",
            gas_limit=gas_limit,
            arguments=[group_id],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def is_signed_by(self, contract: IAddress, user: IAddress, action_id: int) -> bool:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="signed",
            arguments=[user, action_id],
        )

        return value

    def create_transaction_for_unsign_for_outdated_board_members(self,
                                                                 sender: IAccount,
                                                                 nonce: int,
                                                                 contract: IAddress,
                                                                 gas_limit: int,
                                                                 action_id: int,
                                                                 outdated_board_members: list[int]) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="unsignForOutdatedBoardMembers",
            gas_limit=gas_limit,
            arguments=[action_id, outdated_board_members],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def is_quorum_reached(self, contract: IAddress, action_id: int) -> bool:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="quorumReached",
            arguments=[action_id],
        )

        return value

    def create_transaction_for_perform_action(self,
                                              sender: IAccount,
                                              nonce: int,
                                              contract: IAddress,
                                              gas_limit: int,
                                              action_id: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="performAction",
            gas_limit=gas_limit,
            arguments=[action_id],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_perform_batch(self,
                                             sender: IAccount,
                                             nonce: int,
                                             contract: IAddress,
                                             gas_limit: int,
                                             group_id: int) -> Transaction:
        transaction = self.factory.create_transaction_for_execute(
            sender=sender.address,
            contract=contract,
            function="performBatch",
            gas_limit=gas_limit,
            arguments=[group_id],
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        return transaction

    def get_pending_actions_full_info(self, contract: IAddress) -> list[ActionFullInfo]:
        [values] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getPendingActionFullInfo",
            # For now, we don't support the `opt_range` argument.
            arguments=[None],
        )

        actions = [ActionFullInfo.new_from_object(value) for value in values]
        return actions

    def get_user_role(self, contract: IAddress, user: IAddress) -> UserRole:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="userRole",
            arguments=[user],
        )

        return UserRole(int(value))

    def get_all_board_members(self, contract: IAddress) -> list[Address]:
        [public_keys] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getAllBoardMembers",
            arguments=[],
        )

        return [Address(value, DEFAULT_ADDRESS_HRP) for value in public_keys]

    def get_all_proposers(self, contract: IAddress) -> list[Address]:
        [public_keys] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getAllProposers",
            arguments=[],
        )

        return [Address(value, DEFAULT_ADDRESS_HRP) for value in public_keys]

    def get_action_data(self, contract: IAddress, action_id: int) -> list[Address]:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getActionData",
            arguments=[action_id],
        )

        return value

    def get_action_signers(self, contract: IAddress, action_id: int) -> list[Address]:
        [public_keys] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getActionSigners",
            arguments=[action_id],
        )

        return [Address(value, DEFAULT_ADDRESS_HRP) for value in public_keys]

    def get_action_signer_count(self, contract: IAddress, action_id: int) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getActionValidSignerCount",
            arguments=[action_id],
        )

        return value

    def get_action_valid_signer_count(self, contract: IAddress, action_id: int) -> int:
        [value] = self.query_controller.query(
            contract=contract.to_bech32(),
            function="getActionSignerCount",
            arguments=[action_id],
        )

        return value

    def parse_execute_propose_any(self, transaction_on_network: TransactionOnNetwork) -> int:
        outcome = self.parser.parse_execute(transaction_on_network)
        self._raise_for_return_code_in_outcome(outcome)
        [value] = outcome.values
        return value

    def await_completed_execute_propose_any(self, tx_hash: str) -> int:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_execute_propose_any(transaction)

    def parse_execute_perform(self, transaction_on_network: TransactionOnNetwork) -> Optional[Address]:
        outcome = self.parser.parse_execute(transaction_on_network)
        self._raise_for_return_code_in_outcome(outcome)
        [value] = outcome.values
        return Address(value, DEFAULT_ADDRESS_HRP) if value else None

    def await_completed_execute_perform(self, tx_hash: str) -> Optional[Address]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_execute_perform(transaction)

    # TODO: maybe move to the generic outcome parser, just like we did in the query controller?
    def _raise_for_return_code_in_outcome(self, outcome: ParsedSmartContractCallOutcome):
        is_ok = outcome.return_code == "ok"
        if not is_ok:
            raise Exception(outcome.return_code, outcome.return_message)
