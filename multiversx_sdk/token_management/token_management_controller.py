from typing import Optional, Protocol, Union

from multiversx_sdk.core import (Address, Transaction, TransactionComputer,
                                 TransactionOnNetwork)
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transactions_factory_config import \
    TransactionsFactoryConfig
from multiversx_sdk.network_providers.resources import AwaitingOptions
from multiversx_sdk.token_management.token_management_transactions_factory import (
    TokenManagementTransactionsFactory, TokenType)
from multiversx_sdk.token_management.token_management_transactions_outcome_parser import \
    TokenManagementTransactionsOutcomeParser
from multiversx_sdk.token_management.token_management_transactions_outcome_parser_types import (
    AddQuantityOutcome, BurnOutcome, BurnQuantityOutcome, FreezeOutcome,
    IssueFungibleOutcome, IssueNonFungibleOutcome, IssueSemiFungibleOutcome,
    MintOutcome, NFTCreateOutcome, PauseOutcome, RegisterAndSetAllRolesOutcome,
    RegisterMetaEsdtOutcome, SetSpecialRoleOutcome, UnFreezeOutcome,
    UnPauseOutcome, UpdateAttributesOutcome, WipeOutcome)


class INetworkProvider(Protocol):
    def await_transaction_completed(self, transaction_hash: Union[str, bytes], options: Optional[AwaitingOptions] = None) -> TransactionOnNetwork:
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

    def parse_issue_fungible(self, transaction_on_network: TransactionOnNetwork) -> list[IssueFungibleOutcome]:
        return self.parser.parse_issue_fungible(transaction_on_network)

    def await_completed_issue_fungible(self, transaction_hash: Union[str, bytes]) -> list[IssueFungibleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def parse_issue_semi_fungible(self, transaction_on_network: TransactionOnNetwork) -> list[IssueSemiFungibleOutcome]:
        return self.parser.parse_issue_semi_fungible(transaction_on_network)

    def await_completed_issue_semi_fungible(
            self, transaction_hash: Union[str, bytes]) -> list[IssueSemiFungibleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def parse_issue_non_fungible(self, transaction_on_network: TransactionOnNetwork) -> list[IssueNonFungibleOutcome]:
        return self.parser.parse_issue_non_fungible(transaction_on_network)

    def await_completed_issue_non_fungible(self, transaction_hash: Union[str, bytes]) -> list[IssueNonFungibleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def parse_register_meta_esdt(self, transaction_on_network: TransactionOnNetwork) -> list[RegisterMetaEsdtOutcome]:
        return self.parser.parse_register_meta_esdt(transaction_on_network)

    def await_completed_register_meta_esdt(self, transaction_hash: Union[str, bytes]) -> list[RegisterMetaEsdtOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def parse_register_and_set_all_roles(self, transaction_on_network: TransactionOnNetwork) -> list[RegisterAndSetAllRolesOutcome]:
        return self.parser.parse_register_and_set_all_roles(transaction_on_network)

    def await_completed_register_and_set_all_roles(self, transaction_hash: Union[str, bytes]) -> list[RegisterAndSetAllRolesOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def await_completed_set_burn_role_globally(self, transaction_hash: Union[str, bytes]):
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def await_completed_unset_burn_role_globally(self, transaction_hash: Union[str, bytes]):
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_unset_burn_role_globally(transaction)

    def create_transaction_for_setting_special_role_on_fungible_token(self,
                                                                      sender: IAccount,
                                                                      nonce: int,
                                                                      user: Address,
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

    def parse_set_special_role_on_fungible_token(self, transaction_on_network: TransactionOnNetwork) -> list[SetSpecialRoleOutcome]:
        return self.parser.parse_set_special_role(transaction_on_network)

    def await_completed_set_special_role_on_fungible_token(self, transaction_hash: Union[str, bytes]) -> list[SetSpecialRoleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_set_special_role_on_fungible_token(transaction)

    def create_transaction_for_setting_special_role_on_semi_fungible_token(self,
                                                                           sender: IAccount,
                                                                           nonce: int,
                                                                           user: Address,
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

    def parse_set_special_role_on_semi_fungible_token(self, transaction_on_network: TransactionOnNetwork) -> list[SetSpecialRoleOutcome]:
        return self.parser.parse_set_special_role(transaction_on_network)

    def await_completed_set_special_role_on_semi_fungible_token(self, transaction_hash: Union[str, bytes]) -> list[SetSpecialRoleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_set_special_role_on_semi_fungible_token(transaction)

    def create_transaction_for_setting_special_role_on_non_fungible_token(self,
                                                                          sender: IAccount,
                                                                          nonce: int,
                                                                          user: Address,
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

    def parse_set_special_role_on_non_fungible_token(self, transaction_on_network: TransactionOnNetwork) -> list[SetSpecialRoleOutcome]:
        return self.parser.parse_set_special_role(transaction_on_network)

    def await_completed_set_special_role_on_non_fungible_token(self, transaction_hash: Union[str, bytes]) -> list[SetSpecialRoleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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
                                            uris: list[str]) -> Transaction:
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

    def parse_create_nft(self, transaction_on_network: TransactionOnNetwork) -> list[NFTCreateOutcome]:
        return self.parser.parse_nft_create(transaction_on_network)

    def await_completed_create_nft(self, transaction_hash: Union[str, bytes]) -> list[NFTCreateOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def parse_pause(self, transaction_on_network: TransactionOnNetwork) -> list[PauseOutcome]:
        return self.parser.parse_pause(transaction_on_network)

    def await_completed_pause(self, transaction_hash: Union[str, bytes]) -> list[PauseOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def parse_unpause(self, transaction_on_network: TransactionOnNetwork) -> list[UnPauseOutcome]:
        return self.parser.parse_unpause(transaction_on_network)

    def await_completed_unpause(self, transaction_hash: Union[str, bytes]) -> list[UnPauseOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_unpause(transaction)

    def create_transaction_for_freezing(self,
                                        sender: IAccount,
                                        nonce: int,
                                        user: Address,
                                        token_identifier: str) -> Transaction:
        transaction = self.factory.create_transaction_for_freezing(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_freeze(self, transaction_on_network: TransactionOnNetwork) -> list[FreezeOutcome]:
        return self.parser.parse_freeze(transaction_on_network)

    def await_completed_freeze(self, transaction_hash: Union[str, bytes]) -> list[FreezeOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_freeze(transaction)

    def create_transaction_for_unfreezing(self,
                                          sender: IAccount,
                                          nonce: int,
                                          user: Address,
                                          token_identifier: str) -> Transaction:
        transaction = self.factory.create_transaction_for_unfreezing(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_unfreeze(self, transaction_on_network: TransactionOnNetwork) -> list[UnFreezeOutcome]:
        return self.parser.parse_unfreeze(transaction_on_network)

    def await_completed_unfreeze(self, transaction_hash: Union[str, bytes]) -> list[UnFreezeOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_unfreeze(transaction)

    def create_transaction_for_wiping(self,
                                      sender: IAccount,
                                      nonce: int,
                                      user: Address,
                                      token_identifier: str) -> Transaction:
        transaction = self.factory.create_transaction_for_wiping(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_wipe(self, transaction_on_network: TransactionOnNetwork) -> list[WipeOutcome]:
        return self.parser.parse_wipe(transaction_on_network)

    def await_completed_wipe(self, transaction_hash: Union[str, bytes]) -> list[WipeOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def parse_local_mint(self, transaction_on_network: TransactionOnNetwork) -> list[MintOutcome]:
        return self.parser.parse_local_mint(transaction_on_network)

    def await_completed_local_mint(self, transaction_hash: Union[str, bytes]) -> list[MintOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def parse_local_burn(self, transaction_on_network: TransactionOnNetwork) -> list[BurnOutcome]:
        return self.parser.parse_local_burn(transaction_on_network)

    def await_completed_local_burn(self, transaction_hash: Union[str, bytes]) -> list[BurnOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def parse_update_attributes(self, transaction_on_network: TransactionOnNetwork) -> list[UpdateAttributesOutcome]:
        return self.parser.parse_update_attributes(transaction_on_network)

    def await_completed_update_attributes(self, transaction_hash: Union[str, bytes]) -> list[UpdateAttributesOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def parse_add_quantity(self, transaction_on_network: TransactionOnNetwork) -> list[AddQuantityOutcome]:
        return self.parser.parse_add_quantity(transaction_on_network)

    def await_completed_add_quantity(self, transaction_hash: Union[str, bytes]) -> list[AddQuantityOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
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

    def parse_burn_quantity(self, transaction_on_network: TransactionOnNetwork) -> list[BurnQuantityOutcome]:
        return self.parser.parse_burn_quantity(transaction_on_network)

    def await_completed_burn_quantity(self, transaction_hash: Union[str, bytes]) -> list[BurnQuantityOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_burn_quantity(transaction)

    def create_transaction_for_transferring_ownership(self,
                                                      sender: IAccount,
                                                      nonce: int,
                                                      token_identifier: str,
                                                      new_owner: Address) -> Transaction:
        transaction = self.factory.create_transaction_for_transferring_ownership(
            sender=sender.address,
            token_identifier=token_identifier,
            new_owner=new_owner
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_freezing_single_nft(self,
                                                   sender: IAccount,
                                                   nonce: int,
                                                   token_identifier: str,
                                                   token_nonce: int,
                                                   user: Address) -> Transaction:
        transaction = self.factory.create_transaction_for_freezing_single_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            user=user
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_unfreezing_single_nft(self,
                                                     sender: IAccount,
                                                     nonce: int,
                                                     token_identifier: str,
                                                     token_nonce: int,
                                                     user: Address) -> Transaction:
        transaction = self.factory.create_transaction_for_unfreezing_single_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            user=user
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_changing_sft_to_meta_esdt(self,
                                                         sender: IAccount,
                                                         nonce: int,
                                                         collection: str,
                                                         num_decimals: int) -> Transaction:
        transaction = self.factory.create_transaction_for_changing_sft_to_meta_esdt(
            sender=sender.address,
            collection=collection,
            num_decimals=num_decimals
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_transferring_nft_create_role(self,
                                                            sender: IAccount,
                                                            nonce: int,
                                                            token_identifier: str,
                                                            user: Address) -> Transaction:
        transaction = self.factory.create_transaction_for_transferring_nft_create_role(
            sender=sender.address,
            token_identifier=token_identifier,
            user=user
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_stopping_nft_creation(self,
                                                     sender: IAccount,
                                                     nonce: int,
                                                     token_identifier: str) -> Transaction:
        transaction = self.factory.create_transaction_for_stopping_nft_creation(
            sender=sender.address,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transaction_for_wiping_single_nft(self,
                                                 sender: IAccount,
                                                 nonce: int,
                                                 token_identifier: str,
                                                 token_nonce: int,
                                                 user: Address) -> Transaction:
        transaction = self.factory.create_transaction_for_wiping_single_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            user=user
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def create_transction_for_adding_uris(self,
                                          sender: IAccount,
                                          nonce: int,
                                          token_identifier: str,
                                          uris: list[str]) -> Transaction:
        transaction = self.factory.create_transction_for_adding_uris(
            sender=sender.address,
            token_identifier=token_identifier,
            uris=uris
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction
