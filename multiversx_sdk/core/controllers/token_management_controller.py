from typing import List, Protocol, Union

from multiversx_sdk.converters.transactions_converter import \
    TransactionsConverter
from multiversx_sdk.core.controllers.network_provider_wrapper import \
    ProviderWrapper
from multiversx_sdk.core.interfaces import IAddress
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transactions_factories.token_management_transactions_factory import (
    TokenManagementTransactionsFactory, TokenType)
from multiversx_sdk.core.transactions_factories.transactions_factory_config import \
    TransactionsFactoryConfig
from multiversx_sdk.core.transactions_outcome_parsers.token_management_transactions_outcome_parser import \
    TokenManagementTransactionsOutcomeParser
from multiversx_sdk.core.transactions_outcome_parsers.token_management_transactions_outcome_parser_types import (
    AddQuantityOutcome, BurnOutcome, BurnQuantityOutcome, FreezeOutcome,
    IssueFungibleOutcome, IssueNonFungibleOutcome, IssueSemiFungibleOutcome,
    MintOutcome, NFTCreateOutcome, PauseOutcome, RegisterAndSetAllRolesOutcome,
    RegisterMetaEsdtOutcome, SetSpecialRoleOutcome, UnFreezeOutcome,
    UnPauseOutcome, UpdateAttributesOutcome, WipeOutcome)
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


class TokenManagementController:
    def __init__(self, network_provider: INetworkProvider) -> None:
        self.chain_id: Union[str, None] = None
        self.factory: Union[TokenManagementTransactionsFactory, None] = None
        self.provider = network_provider
        self.provider_wrapper = ProviderWrapper(self.provider)
        self.transaction_awaiter = TransactionAwaiter(self.provider_wrapper)
        self.tx_computer = TransactionComputer()
        self.tx_converter = TransactionsConverter()
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
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_issuing_fungible(  # type: ignore
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
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_issue_fungible(tx_outcome)

    def await_completed_issue_fungible(self, tx_hash: str) -> List[IssueFungibleOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
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
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_issuing_semi_fungible(  # type: ignore
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
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_issue_semi_fungible(tx_outcome)

    def await_completed_issue_semi_fungible(self, tx_hash: str) -> List[IssueSemiFungibleOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
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
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_issuing_non_fungible(  # type: ignore
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
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_issue_non_fungible(tx_outcome)

    def await_completed_issue_non_fungible(self, tx_hash: str) -> List[IssueNonFungibleOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
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
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_registering_meta_esdt(  # type: ignore
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
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_register_meta_esdt(tx_outcome)

    def await_completed_register_meta_esdt(self, tx_hash: str) -> List[RegisterMetaEsdtOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_register_meta_esdt(transaction)

    def create_transaction_for_registering_and_setting_roles(self,
                                                             sender: IAccount,
                                                             nonce: int,
                                                             token_name: str,
                                                             token_ticker: str,
                                                             token_type: TokenType,
                                                             num_decimals: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_registering_and_setting_roles(  # type: ignore
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
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_register_and_set_all_roles(tx_outcome)

    def await_completed_register_and_set_all_roles(self, tx_hash: str) -> List[RegisterAndSetAllRolesOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_register_and_set_all_roles(transaction)

    def create_transaction_for_setting_burn_role_globally(self,
                                                          sender: IAccount,
                                                          nonce: int,
                                                          token_identifier: str) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_setting_burn_role_globally(  # type: ignore
            sender=sender.address,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_set_burn_role_globally(self, transaction_on_network: TransactionOnNetwork):
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_set_burn_role_globally(tx_outcome)

    def await_completed_set_burn_role_globally(self, tx_hash: str):
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_set_burn_role_globally(transaction)

    def create_transaction_for_unsetting_burn_role_globally(self,
                                                            sender: IAccount,
                                                            nonce: int,
                                                            token_identifier: str) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_unsetting_burn_role_globally(  # type: ignore
            sender=sender.address,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_unset_burn_role_globally(self, transaction_on_network: TransactionOnNetwork):
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_unset_burn_role_globally(tx_outcome)

    def await_completed_unset_burn_role_globally(self, tx_hash: str):
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_unset_burn_role_globally(transaction)

    def create_transaction_for_setting_special_role_on_fungible_token(self,
                                                                      sender: IAccount,
                                                                      nonce: int,
                                                                      user: IAddress,
                                                                      token_identifier: str,
                                                                      add_role_local_mint: bool,
                                                                      add_role_local_burn: bool,
                                                                      add_role_esdt_transfer_role: bool) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_setting_special_role_on_fungible_token(  # type: ignore
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
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_set_special_role(tx_outcome)

    def await_completed_set_special_role_on_fungible_token(self, tx_hash: str) -> List[SetSpecialRoleOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
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
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_setting_special_role_on_semi_fungible_token(  # type: ignore
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
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_set_special_role(tx_outcome)

    def await_completed_set_special_role_on_semi_fungible_token(self, tx_hash: str) -> List[SetSpecialRoleOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
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
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_setting_special_role_on_non_fungible_token(  # type: ignore
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
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_set_special_role(tx_outcome)

    def await_completed_set_special_role_on_non_fungible_token(self, tx_hash: str) -> List[SetSpecialRoleOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
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
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_creating_nft(  # type: ignore
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
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_nft_create(tx_outcome)

    def await_completed_create_nft(self, tx_hash: str) -> List[NFTCreateOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_create_nft(transaction)

    def create_transaction_for_pausing(self,
                                       sender: IAccount,
                                       nonce: int,
                                       token_identifier: str) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_pausing(  # type: ignore
            sender=sender.address,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_pause(self, transaction_on_network: TransactionOnNetwork) -> List[PauseOutcome]:
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_pause(tx_outcome)

    def await_completed_pause(self, tx_hash: str) -> List[PauseOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_pause(transaction)

    def create_transaction_for_unpausing(self,
                                         sender: IAccount,
                                         nonce: int,
                                         token_identifier: str) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_unpausing(  # type: ignore
            sender=sender.address,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_unpause(self, transaction_on_network: TransactionOnNetwork) -> List[UnPauseOutcome]:
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_unpause(tx_outcome)

    def await_completed_unpause(self, tx_hash: str) -> List[UnPauseOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_unpause(transaction)

    def create_transaction_for_freezing(self,
                                        sender: IAccount,
                                        nonce: int,
                                        user: IAddress,
                                        token_identifier: str) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_freezing(  # type: ignore
            sender=sender.address,
            user=user,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_freeze(self, transaction_on_network: TransactionOnNetwork) -> List[FreezeOutcome]:
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_freeze(tx_outcome)

    def await_completed_freeze(self, tx_hash: str) -> List[FreezeOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_freeze(transaction)

    def create_transaction_for_unfreezing(self,
                                          sender: IAccount,
                                          nonce: int,
                                          user: IAddress,
                                          token_identifier: str) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_unfreezing(  # type: ignore
            sender=sender.address,
            user=user,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_unfreeze(self, transaction_on_network: TransactionOnNetwork) -> List[UnFreezeOutcome]:
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_unfreeze(tx_outcome)

    def await_completed_unfreeze(self, tx_hash: str) -> List[UnFreezeOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_unfreeze(transaction)

    def create_transaction_for_wiping(self,
                                      sender: IAccount,
                                      nonce: int,
                                      user: IAddress,
                                      token_identifier: str) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_wiping(  # type: ignore
            sender=sender.address,
            user=user,
            token_identifier=token_identifier
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_wipe(self, transaction_on_network: TransactionOnNetwork) -> List[WipeOutcome]:
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_wipe(tx_outcome)

    def await_completed_wipe(self, tx_hash: str) -> List[WipeOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_wipe(transaction)

    def create_transaction_for_local_minting(self,
                                             sender: IAccount,
                                             nonce: int,
                                             token_identifier: str,
                                             supply_to_mint: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_local_minting(  # type: ignore
            sender=sender.address,
            token_identifier=token_identifier,
            supply_to_mint=supply_to_mint
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_local_mint(self, transaction_on_network: TransactionOnNetwork) -> List[MintOutcome]:
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_local_mint(tx_outcome)

    def await_completed_local_mint(self, tx_hash: str) -> List[MintOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_local_mint(transaction)

    def create_transaction_for_local_burning(self,
                                             sender: IAccount,
                                             nonce: int,
                                             token_identifier: str,
                                             supply_to_burn: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_local_burning(  # type: ignore
            sender=sender.address,
            token_identifier=token_identifier,
            supply_to_burn=supply_to_burn
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_local_burn(self, transaction_on_network: TransactionOnNetwork) -> List[BurnOutcome]:
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_local_burn(tx_outcome)

    def await_completed_local_burn(self, tx_hash: str) -> List[BurnOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_local_burn(transaction)

    def create_transaction_for_updating_attributes(self,
                                                   sender: IAccount,
                                                   nonce: int,
                                                   token_identifier: str,
                                                   token_nonce: int,
                                                   attributes: bytes) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_updating_attributes(  # type: ignore
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            attributes=attributes
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_update_attributes(self, transaction_on_network: TransactionOnNetwork) -> List[UpdateAttributesOutcome]:
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_update_attributes(tx_outcome)

    def await_completed_update_attributes(self, tx_hash: str) -> List[UpdateAttributesOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_update_attributes(transaction)

    def create_transaction_for_adding_quantity(self,
                                               sender: IAccount,
                                               nonce: int,
                                               token_identifier: str,
                                               token_nonce: int,
                                               quantity_to_add: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_adding_quantity(  # type: ignore
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            quantity_to_add=quantity_to_add
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_add_quantity(self, transaction_on_network: TransactionOnNetwork) -> List[AddQuantityOutcome]:
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_add_quantity(tx_outcome)

    def await_completed_add_quantity(self, tx_hash: str) -> List[AddQuantityOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_add_quantity(transaction)

    def create_transaction_for_burning_quantity(self,
                                                sender: IAccount,
                                                nonce: int,
                                                token_identifier: str,
                                                token_nonce: int,
                                                quantity_to_burn: int) -> Transaction:
        self._ensure_factory_is_initialized()

        transaction = self.factory.create_transaction_for_burning_quantity(  # type: ignore
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            quantity_to_burn=quantity_to_burn
        )

        transaction.nonce = nonce
        transaction.signature = sender.sign(self.tx_computer.compute_bytes_for_signing(transaction))

        return transaction

    def parse_burn_quantity(self, transaction_on_network: TransactionOnNetwork) -> List[BurnQuantityOutcome]:
        tx_outcome = self.tx_converter.transaction_on_network_to_outcome(transaction_on_network)
        return self.parser.parse_burn_quantity(tx_outcome)

    def await_completed_burn_quantity(self, tx_hash: str) -> List[BurnQuantityOutcome]:
        transaction = self.transaction_awaiter.await_completed(tx_hash)
        return self.parse_burn_quantity(transaction)

    def _ensure_factory_is_initialized(self):
        if self.factory is None:
            self.chain_id = self.provider.get_network_config().chain_id
            config = TransactionsFactoryConfig(self.chain_id)
            self.factory = TokenManagementTransactionsFactory(config)
