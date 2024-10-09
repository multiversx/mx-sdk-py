from typing import List, Optional, Protocol, Union

from multiversx_sdk.controllers.interfaces import IAccount
from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.core.transactions_factories import (
    TokenManagementTransactionsFactory, TokenType, TransactionsFactoryConfig)
from multiversx_sdk.core.transactions_outcome_parsers import (
    AddQuantityOutcome, BurnOutcome, BurnQuantityOutcome, FreezeOutcome,
    IssueFungibleOutcome, IssueNonFungibleOutcome, IssueSemiFungibleOutcome,
    MintOutcome, NFTCreateOutcome, PauseOutcome, RegisterAndSetAllRolesOutcome,
    RegisterMetaEsdtOutcome, SetSpecialRoleOutcome,
    TokenManagementTransactionsOutcomeParser, UnFreezeOutcome, UnPauseOutcome,
    UpdateAttributesOutcome, WipeOutcome)
from multiversx_sdk.network_providers.resources import AwaitingOptions


class INetworkProvider(Protocol):
    def await_transaction_completed(self, tx_hash: Union[str, bytes], options: Optional[AwaitingOptions] = None) -> TransactionOnNetwork:
        ...


class TokenManagementController:
    def __init__(self, chain_id: str, network_provider: INetworkProvider) -> None:
        self.factory = TokenManagementTransactionsFactory(TransactionsFactoryConfig(chain_id))
        self.network_provider = network_provider
        self.tx_computer = TransactionComputer()
        self.parser = TokenManagementTransactionsOutcomeParser()

    def create_transaction_for_issuing_fungible(self,
                                                sender: IAccount,
                                                nonce: int,
                                                token_name: str,
                                                token_ticker: str,
                                                initial_supply: int,
                                                num_decimals: int,
                                                can_freeze: bool,
                                                can_wipe: bool,
                                                can_pause: bool,
                                                can_change_owner: bool,
                                                can_upgrade: bool,
                                                can_add_special_roles: bool) -> Transaction:
        transaction = self.factory.create_transaction_for_issuing_fungible(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            initial_supply=initial_supply,
            num_decimals=num_decimals,
            can_freeze=can_freeze,
            can_wipe=can_wipe,
            can_pause=can_pause,
            can_change_owner=can_change_owner,
            can_upgrade=can_upgrade,
            can_add_special_roles=can_add_special_roles
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_issue_fungible(self, transaction_on_network: TransactionOnNetwork) -> List[IssueFungibleOutcome]:
        return self.parser.parse_issue_fungible(transaction_on_network)

    def await_completed_issue_fungible(self, tx_hash: str) -> List[IssueFungibleOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_issue_fungible(transaction)

    def create_transaction_for_issuing_semi_fungible(self,
                                                     sender: IAccount,
                                                     nonce: int,
                                                     token_name: str,
                                                     token_ticker: str,
                                                     can_freeze: bool,
                                                     can_wipe: bool,
                                                     can_pause: bool,
                                                     can_transfer_nft_create_role: bool,
                                                     can_change_owner: bool,
                                                     can_upgrade: bool,
                                                     can_add_special_roles: bool) -> Transaction:
        transaction = self.factory.create_transaction_for_issuing_semi_fungible(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            can_freeze=can_freeze,
            can_wipe=can_wipe,
            can_pause=can_pause,
            can_transfer_nft_create_role=can_transfer_nft_create_role,
            can_change_owner=can_change_owner,
            can_upgrade=can_upgrade,
            can_add_special_roles=can_add_special_roles
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_issue_semi_fungible(self, transaction_on_network: TransactionOnNetwork) -> List[IssueSemiFungibleOutcome]:
        return self.parser.parse_issue_semi_fungible(transaction_on_network)

    def await_completed_issue_semi_fungible(self, tx_hash: str) -> List[IssueSemiFungibleOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_issue_semi_fungible(transaction)

    def create_transaction_for_issuing_non_fungible(self,
                                                    sender: IAccount,
                                                    nonce: int,
                                                    token_name: str,
                                                    token_ticker: str,
                                                    can_freeze: bool,
                                                    can_wipe: bool,
                                                    can_pause: bool,
                                                    can_transfer_nft_create_role: bool,
                                                    can_change_owner: bool,
                                                    can_upgrade: bool,
                                                    can_add_special_roles: bool) -> Transaction:
        transaction = self.factory.create_transaction_for_issuing_non_fungible(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            can_freeze=can_freeze,
            can_wipe=can_wipe,
            can_pause=can_pause,
            can_transfer_nft_create_role=can_transfer_nft_create_role,
            can_change_owner=can_change_owner,
            can_upgrade=can_upgrade,
            can_add_special_roles=can_add_special_roles
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_issue_non_fungible(self, transaction_on_network: TransactionOnNetwork) -> List[IssueNonFungibleOutcome]:
        return self.parser.parse_issue_non_fungible(transaction_on_network)

    def await_completed_issue_non_fungible(self, tx_hash: str) -> List[IssueNonFungibleOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_issue_non_fungible(transaction)

    def create_transaction_for_registering_meta_esdt(self,
                                                     sender: IAccount,
                                                     nonce: int,
                                                     token_name: str,
                                                     token_ticker: str,
                                                     num_decimals: int,
                                                     can_freeze: bool,
                                                     can_wipe: bool,
                                                     can_pause: bool,
                                                     can_transfer_nft_create_role: bool,
                                                     can_change_owner: bool,
                                                     can_upgrade: bool,
                                                     can_add_special_roles: bool) -> Transaction:
        transaction = self.factory.create_transaction_for_registering_meta_esdt(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            num_decimals=num_decimals,
            can_freeze=can_freeze,
            can_wipe=can_wipe,
            can_pause=can_pause,
            can_transfer_nft_create_role=can_transfer_nft_create_role,
            can_change_owner=can_change_owner,
            can_upgrade=can_upgrade,
            can_add_special_roles=can_add_special_roles
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_register_meta_esdt(self, transaction_on_network: TransactionOnNetwork) -> List[RegisterMetaEsdtOutcome]:
        return self.parser.parse_register_meta_esdt(transaction_on_network)

    def await_completed_register_meta_esdt(self, tx_hash: str) -> List[RegisterMetaEsdtOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_register_meta_esdt(transaction)

    def create_transaction_for_registering_and_setting_roles(self,
                                                             sender: IAccount,
                                                             nonce: int,
                                                             token_name: str,
                                                             token_ticker: str,
                                                             token_type: TokenType,
                                                             num_decimals: int) -> Transaction:
        transaction = self.factory.create_transaction_for_registering_and_setting_roles(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            token_type=token_type,
            num_decimals=num_decimals,
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_register_and_set_all_roles(self, transaction_on_network: TransactionOnNetwork) -> List[RegisterAndSetAllRolesOutcome]:
        return self.parser.parse_register_and_set_all_roles(transaction_on_network)

    def await_completed_register_and_set_all_roles(self, tx_hash: str) -> List[RegisterAndSetAllRolesOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_register_and_set_all_roles(transaction)

    def create_transaction_for_setting_burn_role_globally(self,
                                                          sender: IAccount,
                                                          nonce: int,
                                                          token_identifier: str) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_burn_role_globally(
            sender=sender.address,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_set_burn_role_globally(self, transaction_on_network: TransactionOnNetwork):
        return self.parser.parse_set_burn_role_globally(transaction_on_network)

    def await_completed_set_burn_role_globally(self, tx_hash: str):
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_set_burn_role_globally(transaction)

    def create_transaction_for_unsetting_burn_role_globally(self,
                                                            sender: IAccount,
                                                            nonce: int,
                                                            token_identifier: str) -> Transaction:
        transaction = self.factory.create_transaction_for_unsetting_burn_role_globally(
            sender=sender.address,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_unset_burn_role_globally(self, transaction_on_network: TransactionOnNetwork):
        return self.parser.parse_unset_burn_role_globally(transaction_on_network)

    def await_completed_unset_burn_role_globally(self, tx_hash: str):
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_unset_burn_role_globally(transaction)

    def create_transaction_for_setting_special_role_on_fungible_token(self,
                                                                      sender: IAccount,
                                                                      nonce: int,
                                                                      user: IAddress,
                                                                      token_identifier: str,
                                                                      add_role_local_mint: bool,
                                                                      add_role_local_burn: bool,
                                                                      add_role_esdt_transfer_role: bool) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_special_role_on_fungible_token(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
            add_role_local_mint=add_role_local_mint,
            add_role_local_burn=add_role_local_burn,
            add_role_esdt_transfer_role=add_role_esdt_transfer_role
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_set_special_role_on_fungible_token(self, transaction_on_network: TransactionOnNetwork) -> List[SetSpecialRoleOutcome]:
        return self.parser.parse_set_special_role(transaction_on_network)

    def await_completed_set_special_role_on_fungible_token(self, tx_hash: str) -> List[SetSpecialRoleOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_set_special_role_on_fungible_token(transaction)

    def create_transaction_for_setting_special_role_on_semi_fungible_token(self,
                                                                           sender: IAccount,
                                                                           nonce: int,
                                                                           user: IAddress,
                                                                           token_identifier: str,
                                                                           add_role_nft_create: bool,
                                                                           add_role_nft_burn: bool,
                                                                           add_role_nft_add_quantity: bool,
                                                                           add_role_esdt_transfer_role: bool) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_special_role_on_semi_fungible_token(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
            add_role_nft_create=add_role_nft_create,
            add_role_nft_burn=add_role_nft_burn,
            add_role_nft_add_quantity=add_role_nft_add_quantity,
            add_role_esdt_transfer_role=add_role_esdt_transfer_role
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_set_special_role_on_semi_fungible_token(self, transaction_on_network: TransactionOnNetwork) -> List[SetSpecialRoleOutcome]:
        return self.parser.parse_set_special_role(transaction_on_network)

    def await_completed_set_special_role_on_semi_fungible_token(self, tx_hash: str) -> List[SetSpecialRoleOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_set_special_role_on_semi_fungible_token(transaction)

    def create_transaction_for_setting_special_role_on_non_fungible_token(self,
                                                                          sender: IAccount,
                                                                          nonce: int,
                                                                          user: IAddress,
                                                                          token_identifier: str,
                                                                          add_role_nft_create: bool,
                                                                          add_role_nft_burn: bool,
                                                                          add_role_nft_update_attributes: bool,
                                                                          add_role_nft_add_uri: bool,
                                                                          add_role_esdt_transfer_role: bool) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_special_role_on_non_fungible_token(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
            add_role_nft_create=add_role_nft_create,
            add_role_nft_burn=add_role_nft_burn,
            add_role_nft_update_attributes=add_role_nft_update_attributes,
            add_role_nft_add_uri=add_role_nft_add_uri,
            add_role_esdt_transfer_role=add_role_esdt_transfer_role
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_set_special_role_on_non_fungible_token(self, transaction_on_network: TransactionOnNetwork) -> List[SetSpecialRoleOutcome]:
        return self.parser.parse_set_special_role(transaction_on_network)

    def await_completed_set_special_role_on_non_fungible_token(self, tx_hash: str) -> List[SetSpecialRoleOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_set_special_role_on_non_fungible_token(transaction)

    def create_transaction_for_creating_nft(self,
                                            sender: IAccount,
                                            nonce: int,
                                            token_identifier: str,
                                            initial_quantity: int,
                                            name: str,
                                            royalties: int,
                                            hash: str,
                                            attributes: bytes,
                                            uris: List[str]) -> Transaction:
        transaction = self.factory.create_transaction_for_creating_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            initial_quantity=initial_quantity,
            name=name,
            royalties=royalties,
            hash=hash,
            attributes=attributes,
            uris=uris
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_create_nft(self, transaction_on_network: TransactionOnNetwork) -> List[NFTCreateOutcome]:
        return self.parser.parse_nft_create(transaction_on_network)

    def await_completed_create_nft(self, tx_hash: str) -> List[NFTCreateOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_create_nft(transaction)

    def create_transaction_for_pausing(self,
                                       sender: IAccount,
                                       nonce: int,
                                       token_identifier: str) -> Transaction:
        transaction = self.factory.create_transaction_for_pausing(
            sender=sender.address,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_pause(self, transaction_on_network: TransactionOnNetwork) -> List[PauseOutcome]:
        return self.parser.parse_pause(transaction_on_network)

    def await_completed_pause(self, tx_hash: str) -> List[PauseOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_pause(transaction)

    def create_transaction_for_unpausing(self,
                                         sender: IAccount,
                                         nonce: int,
                                         token_identifier: str) -> Transaction:
        transaction = self.factory.create_transaction_for_unpausing(
            sender=sender.address,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_unpause(self, transaction_on_network: TransactionOnNetwork) -> List[UnPauseOutcome]:
        return self.parser.parse_unpause(transaction_on_network)

    def await_completed_unpause(self, tx_hash: str) -> List[UnPauseOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_unpause(transaction)

    def create_transaction_for_freezing(self,
                                        sender: IAccount,
                                        nonce: int,
                                        user: IAddress,
                                        token_identifier: str) -> Transaction:
        transaction = self.factory.create_transaction_for_freezing(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_freeze(self, transaction_on_network: TransactionOnNetwork) -> List[FreezeOutcome]:
        return self.parser.parse_freeze(transaction_on_network)

    def await_completed_freeze(self, tx_hash: str) -> List[FreezeOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_freeze(transaction)

    def create_transaction_for_unfreezing(self,
                                          sender: IAccount,
                                          nonce: int,
                                          user: IAddress,
                                          token_identifier: str) -> Transaction:
        transaction = self.factory.create_transaction_for_unfreezing(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_unfreeze(self, transaction_on_network: TransactionOnNetwork) -> List[UnFreezeOutcome]:
        return self.parser.parse_unfreeze(transaction_on_network)

    def await_completed_unfreeze(self, tx_hash: str) -> List[UnFreezeOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_unfreeze(transaction)

    def create_transaction_for_wiping(self,
                                      sender: IAccount,
                                      nonce: int,
                                      user: IAddress,
                                      token_identifier: str) -> Transaction:
        transaction = self.factory.create_transaction_for_wiping(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_wipe(self, transaction_on_network: TransactionOnNetwork) -> List[WipeOutcome]:
        return self.parser.parse_wipe(transaction_on_network)

    def await_completed_wipe(self, tx_hash: str) -> List[WipeOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_wipe(transaction)

    def create_transaction_for_local_minting(self,
                                             sender: IAccount,
                                             nonce: int,
                                             token_identifier: str,
                                             supply_to_mint: int) -> Transaction:
        transaction = self.factory.create_transaction_for_local_minting(
            sender=sender.address,
            token_identifier=token_identifier,
            supply_to_mint=supply_to_mint
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_local_mint(self, transaction_on_network: TransactionOnNetwork) -> List[MintOutcome]:
        return self.parser.parse_local_mint(transaction_on_network)

    def await_completed_local_mint(self, tx_hash: str) -> List[MintOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_local_mint(transaction)

    def create_transaction_for_local_burning(self,
                                             sender: IAccount,
                                             nonce: int,
                                             token_identifier: str,
                                             supply_to_burn: int) -> Transaction:
        transaction = self.factory.create_transaction_for_local_burning(
            sender=sender.address,
            token_identifier=token_identifier,
            supply_to_burn=supply_to_burn
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_local_burn(self, transaction_on_network: TransactionOnNetwork) -> List[BurnOutcome]:
        return self.parser.parse_local_burn(transaction_on_network)

    def await_completed_local_burn(self, tx_hash: str) -> List[BurnOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_local_burn(transaction)

    def create_transaction_for_updating_attributes(self,
                                                   sender: IAccount,
                                                   nonce: int,
                                                   token_identifier: str,
                                                   token_nonce: int,
                                                   attributes: bytes) -> Transaction:
        transaction = self.factory.create_transaction_for_updating_attributes(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            attributes=attributes
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_update_attributes(self, transaction_on_network: TransactionOnNetwork) -> List[UpdateAttributesOutcome]:
        return self.parser.parse_update_attributes(transaction_on_network)

    def await_completed_update_attributes(self, tx_hash: str) -> List[UpdateAttributesOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_update_attributes(transaction)

    def create_transaction_for_adding_quantity(self,
                                               sender: IAccount,
                                               nonce: int,
                                               token_identifier: str,
                                               token_nonce: int,
                                               quantity_to_add: int) -> Transaction:
        transaction = self.factory.create_transaction_for_adding_quantity(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            quantity_to_add=quantity_to_add
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_add_quantity(self, transaction_on_network: TransactionOnNetwork) -> List[AddQuantityOutcome]:
        return self.parser.parse_add_quantity(transaction_on_network)

    def await_completed_add_quantity(self, tx_hash: str) -> List[AddQuantityOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_add_quantity(transaction)

    def create_transaction_for_burning_quantity(self,
                                                sender: IAccount,
                                                nonce: int,
                                                token_identifier: str,
                                                token_nonce: int,
                                                quantity_to_burn: int) -> Transaction:
        transaction = self.factory.create_transaction_for_burning_quantity(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            quantity_to_burn=quantity_to_burn
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_burn_quantity(self, transaction_on_network: TransactionOnNetwork) -> List[BurnQuantityOutcome]:
        return self.parser.parse_burn_quantity(transaction_on_network)

    def await_completed_burn_quantity(self, tx_hash: str) -> List[BurnQuantityOutcome]:
        transaction = self.network_provider.await_transaction_completed(tx_hash)
        return self.parse_burn_quantity(transaction)
