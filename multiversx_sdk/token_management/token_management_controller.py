from typing import Optional, Protocol, Union

from multiversx_sdk.core import Address, Transaction, TransactionOnNetwork
from multiversx_sdk.core.base_controller import BaseController
from multiversx_sdk.core.interfaces import IAccount
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.network_providers.resources import AwaitingOptions
from multiversx_sdk.token_management.token_management_transactions_factory import (
    TokenManagementTransactionsFactory,
    TokenType,
)
from multiversx_sdk.token_management.token_management_transactions_outcome_parser import (
    TokenManagementTransactionsOutcomeParser,
)
from multiversx_sdk.token_management.token_management_transactions_outcome_parser_types import (
    AddQuantityOutcome,
    BurnOutcome,
    BurnQuantityOutcome,
    ChangeTokenToDynamicOutcome,
    FreezeOutcome,
    IssueFungibleOutcome,
    IssueNonFungibleOutcome,
    IssueSemiFungibleOutcome,
    MetadataRecreateOutcome,
    MintOutcome,
    ModifyCreatorOutcome,
    ModifyRoyaltiesOutcome,
    NFTCreateOutcome,
    PauseOutcome,
    RegisterAndSetAllRolesOutcome,
    RegisterDynamicOutcome,
    RegisterMetaEsdtOutcome,
    SetNewUrisOutcome,
    SetSpecialRoleOutcome,
    UnFreezeOutcome,
    UnPauseOutcome,
    UpdateAttributesOutcome,
    UpdateMetadataOutcome,
    WipeOutcome,
)


# fmt: off
class INetworkProvider(Protocol):
    def await_transaction_completed(self, transaction_hash: Union[str, bytes], options: Optional[AwaitingOptions] = None) -> TransactionOnNetwork:
        ...
# fmt: on


class TokenManagementController(BaseController):
    def __init__(self, chain_id: str, network_provider: INetworkProvider) -> None:
        self.factory = TokenManagementTransactionsFactory(TransactionsFactoryConfig(chain_id))
        self.network_provider = network_provider
        self.parser = TokenManagementTransactionsOutcomeParser()

    def create_transaction_for_issuing_fungible(
        self,
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
        can_add_special_roles: bool,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
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
            can_add_special_roles=can_add_special_roles,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_issue_fungible(self, transaction_on_network: TransactionOnNetwork) -> list[IssueFungibleOutcome]:
        return self.parser.parse_issue_fungible(transaction_on_network)

    def await_completed_issue_fungible(self, transaction_hash: Union[str, bytes]) -> list[IssueFungibleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_issue_fungible(transaction)

    def create_transaction_for_issuing_semi_fungible(
        self,
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
        can_add_special_roles: bool,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
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
            can_add_special_roles=can_add_special_roles,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_issue_semi_fungible(self, transaction_on_network: TransactionOnNetwork) -> list[IssueSemiFungibleOutcome]:
        return self.parser.parse_issue_semi_fungible(transaction_on_network)

    def await_completed_issue_semi_fungible(
        self, transaction_hash: Union[str, bytes]
    ) -> list[IssueSemiFungibleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_issue_semi_fungible(transaction)

    def create_transaction_for_issuing_non_fungible(
        self,
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
        can_add_special_roles: bool,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
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
            can_add_special_roles=can_add_special_roles,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_issue_non_fungible(self, transaction_on_network: TransactionOnNetwork) -> list[IssueNonFungibleOutcome]:
        return self.parser.parse_issue_non_fungible(transaction_on_network)

    def await_completed_issue_non_fungible(self, transaction_hash: Union[str, bytes]) -> list[IssueNonFungibleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_issue_non_fungible(transaction)

    def create_transaction_for_registering_meta_esdt(
        self,
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
        can_add_special_roles: bool,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
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
            can_add_special_roles=can_add_special_roles,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_register_meta_esdt(self, transaction_on_network: TransactionOnNetwork) -> list[RegisterMetaEsdtOutcome]:
        return self.parser.parse_register_meta_esdt(transaction_on_network)

    def await_completed_register_meta_esdt(self, transaction_hash: Union[str, bytes]) -> list[RegisterMetaEsdtOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_register_meta_esdt(transaction)

    def create_transaction_for_registering_and_setting_roles(
        self,
        sender: IAccount,
        nonce: int,
        token_name: str,
        token_ticker: str,
        token_type: TokenType,
        num_decimals: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_registering_and_setting_roles(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            token_type=token_type,
            num_decimals=num_decimals,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_register_and_set_all_roles(
        self, transaction_on_network: TransactionOnNetwork
    ) -> list[RegisterAndSetAllRolesOutcome]:
        return self.parser.parse_register_and_set_all_roles(transaction_on_network)

    def await_completed_register_and_set_all_roles(
        self, transaction_hash: Union[str, bytes]
    ) -> list[RegisterAndSetAllRolesOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_register_and_set_all_roles(transaction)

    def create_transaction_for_setting_burn_role_globally(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_burn_role_globally(
            sender=sender.address, token_identifier=token_identifier
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_set_burn_role_globally(self, transaction_on_network: TransactionOnNetwork):
        return self.parser.parse_set_burn_role_globally(transaction_on_network)

    def await_completed_set_burn_role_globally(self, transaction_hash: Union[str, bytes]):
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_set_burn_role_globally(transaction)

    def create_transaction_for_unsetting_burn_role_globally(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unsetting_burn_role_globally(
            sender=sender.address, token_identifier=token_identifier
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_unset_burn_role_globally(self, transaction_on_network: TransactionOnNetwork):
        return self.parser.parse_unset_burn_role_globally(transaction_on_network)

    def await_completed_unset_burn_role_globally(self, transaction_hash: Union[str, bytes]):
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_unset_burn_role_globally(transaction)

    def create_transaction_for_setting_special_role_on_fungible_token(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        add_role_local_mint: bool = False,
        add_role_local_burn: bool = False,
        add_role_esdt_transfer_role: bool = False,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_special_role_on_fungible_token(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
            add_role_local_mint=add_role_local_mint,
            add_role_local_burn=add_role_local_burn,
            add_role_esdt_transfer_role=add_role_esdt_transfer_role,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_set_special_role_on_fungible_token(
        self, transaction_on_network: TransactionOnNetwork
    ) -> list[SetSpecialRoleOutcome]:
        return self.parser.parse_set_special_role(transaction_on_network)

    def await_completed_set_special_role_on_fungible_token(
        self, transaction_hash: Union[str, bytes]
    ) -> list[SetSpecialRoleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_set_special_role_on_fungible_token(transaction)

    def create_transaction_for_unsetting_special_role_on_fungible_token(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        remove_role_local_mint: bool = False,
        remove_role_local_burn: bool = False,
        remove_role_esdt_transfer_role: bool = False,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unsetting_special_role_on_fungible_token(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
            remove_role_local_mint=remove_role_local_mint,
            remove_role_local_burn=remove_role_local_burn,
            remove_role_esdt_transfer_role=remove_role_esdt_transfer_role,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_setting_special_role_on_semi_fungible_token(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        add_role_nft_create: bool = False,
        add_role_nft_burn: bool = False,
        add_role_nft_add_quantity: bool = False,
        add_role_esdt_transfer_role: bool = False,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_special_role_on_semi_fungible_token(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
            add_role_nft_create=add_role_nft_create,
            add_role_nft_burn=add_role_nft_burn,
            add_role_nft_add_quantity=add_role_nft_add_quantity,
            add_role_esdt_transfer_role=add_role_esdt_transfer_role,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_set_special_role_on_semi_fungible_token(
        self, transaction_on_network: TransactionOnNetwork
    ) -> list[SetSpecialRoleOutcome]:
        return self.parser.parse_set_special_role(transaction_on_network)

    def await_completed_set_special_role_on_semi_fungible_token(
        self, transaction_hash: Union[str, bytes]
    ) -> list[SetSpecialRoleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_set_special_role_on_semi_fungible_token(transaction)

    def create_transaction_for_unsetting_special_role_on_semi_fungible_token(
        self,
        sender: IAccount,
        user: Address,
        nonce: int,
        token_identifier: str,
        remove_role_nft_burn: bool = False,
        remove_role_nft_add_quantity: bool = False,
        remove_role_esdt_transfer_role: bool = False,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unsetting_special_role_on_semi_fungible_token(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
            remove_role_nft_burn=remove_role_nft_burn,
            remove_role_nft_add_quantity=remove_role_nft_add_quantity,
            remove_role_esdt_transfer_role=remove_role_esdt_transfer_role,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_setting_special_role_on_meta_esdt(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        add_role_nft_create: bool = False,
        add_role_nft_burn: bool = False,
        add_role_nft_add_quantity: bool = False,
        add_role_esdt_transfer_role: bool = False,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_special_role_on_meta_esdt(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
            add_role_nft_create=add_role_nft_create,
            add_role_nft_burn=add_role_nft_burn,
            add_role_nft_add_quantity=add_role_nft_add_quantity,
            add_role_esdt_transfer_role=add_role_esdt_transfer_role,
        )
        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_set_special_role_on_meta_esdt(
        self, transaction_on_network: TransactionOnNetwork
    ) -> list[SetSpecialRoleOutcome]:
        return self.parser.parse_set_special_role(transaction_on_network)

    def await_completed_set_special_role_on_meta_esdt(
        self, transaction_hash: Union[str, bytes]
    ) -> list[SetSpecialRoleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_set_special_role_on_meta_esdt(transaction)

    def create_transaction_for_unsetting_special_role_on_meta_esdt(
        self,
        sender: IAccount,
        user: Address,
        nonce: int,
        token_identifier: str,
        remove_role_nft_burn: bool = False,
        remove_role_nft_add_quantity: bool = False,
        remove_role_esdt_transfer_role: bool = False,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unsetting_special_role_on_meta_esdt(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
            remove_role_nft_burn=remove_role_nft_burn,
            remove_role_nft_add_quantity=remove_role_nft_add_quantity,
            remove_role_esdt_transfer_role=remove_role_esdt_transfer_role,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_setting_special_role_on_non_fungible_token(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        add_role_nft_create: bool = False,
        add_role_nft_burn: bool = False,
        add_role_nft_update_attributes: bool = False,
        add_role_nft_add_uri: bool = False,
        add_role_esdt_transfer_role: bool = False,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_special_role_on_non_fungible_token(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
            add_role_nft_create=add_role_nft_create,
            add_role_nft_burn=add_role_nft_burn,
            add_role_nft_update_attributes=add_role_nft_update_attributes,
            add_role_nft_add_uri=add_role_nft_add_uri,
            add_role_esdt_transfer_role=add_role_esdt_transfer_role,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_set_special_role_on_non_fungible_token(
        self, transaction_on_network: TransactionOnNetwork
    ) -> list[SetSpecialRoleOutcome]:
        return self.parser.parse_set_special_role(transaction_on_network)

    def await_completed_set_special_role_on_non_fungible_token(
        self, transaction_hash: Union[str, bytes]
    ) -> list[SetSpecialRoleOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_set_special_role_on_non_fungible_token(transaction)

    def create_transaction_for_unsetting_special_role_on_non_fungible_token(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        remove_role_nft_burn: bool = False,
        remove_role_nft_update_attributes: bool = False,
        remove_role_nft_remove_uri: bool = False,
        remove_role_esdt_transfer_role: bool = False,
        remove_role_nft_update: bool = False,
        remove_role_esdt_modify_royalties: bool = False,
        remove_role_esdt_set_new_uri: bool = False,
        remove_role_esdt_modify_creator: bool = False,
        remove_role_nft_recreate: bool = False,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unsetting_special_role_on_non_fungible_token(
            sender=sender.address,
            user=user,
            token_identifier=token_identifier,
            remove_role_nft_burn=remove_role_nft_burn,
            remove_role_nft_update_attributes=remove_role_nft_update_attributes,
            remove_role_nft_remove_uri=remove_role_nft_remove_uri,
            remove_role_esdt_transfer_role=remove_role_esdt_transfer_role,
            remove_role_nft_update=remove_role_nft_update,
            remove_role_esdt_modify_royalties=remove_role_esdt_modify_royalties,
            remove_role_esdt_set_new_uri=remove_role_esdt_set_new_uri,
            remove_role_esdt_modify_creator=remove_role_esdt_modify_creator,
            remove_role_nft_recreate=remove_role_nft_recreate,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_creating_nft(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        initial_quantity: int,
        name: str,
        royalties: int,
        hash: str,
        attributes: bytes,
        uris: list[str],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_creating_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            initial_quantity=initial_quantity,
            name=name,
            royalties=royalties,
            hash=hash,
            attributes=attributes,
            uris=uris,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_create_nft(self, transaction_on_network: TransactionOnNetwork) -> list[NFTCreateOutcome]:
        return self.parser.parse_nft_create(transaction_on_network)

    def await_completed_create_nft(self, transaction_hash: Union[str, bytes]) -> list[NFTCreateOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_create_nft(transaction)

    def create_transaction_for_pausing(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_pausing(
            sender=sender.address, token_identifier=token_identifier
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_pause(self, transaction_on_network: TransactionOnNetwork) -> list[PauseOutcome]:
        return self.parser.parse_pause(transaction_on_network)

    def await_completed_pause(self, transaction_hash: Union[str, bytes]) -> list[PauseOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_pause(transaction)

    def create_transaction_for_unpausing(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unpausing(
            sender=sender.address, token_identifier=token_identifier
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_unpause(self, transaction_on_network: TransactionOnNetwork) -> list[UnPauseOutcome]:
        return self.parser.parse_unpause(transaction_on_network)

    def await_completed_unpause(self, transaction_hash: Union[str, bytes]) -> list[UnPauseOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_unpause(transaction)

    def create_transaction_for_freezing(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_freezing(
            sender=sender.address, user=user, token_identifier=token_identifier
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_freeze(self, transaction_on_network: TransactionOnNetwork) -> list[FreezeOutcome]:
        return self.parser.parse_freeze(transaction_on_network)

    def await_completed_freeze(self, transaction_hash: Union[str, bytes]) -> list[FreezeOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_freeze(transaction)

    def create_transaction_for_unfreezing(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unfreezing(
            sender=sender.address, user=user, token_identifier=token_identifier
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_unfreeze(self, transaction_on_network: TransactionOnNetwork) -> list[UnFreezeOutcome]:
        return self.parser.parse_unfreeze(transaction_on_network)

    def await_completed_unfreeze(self, transaction_hash: Union[str, bytes]) -> list[UnFreezeOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_unfreeze(transaction)

    def create_transaction_for_wiping(
        self,
        sender: IAccount,
        nonce: int,
        user: Address,
        token_identifier: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_wiping(
            sender=sender.address, user=user, token_identifier=token_identifier
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_wipe(self, transaction_on_network: TransactionOnNetwork) -> list[WipeOutcome]:
        return self.parser.parse_wipe(transaction_on_network)

    def await_completed_wipe(self, transaction_hash: Union[str, bytes]) -> list[WipeOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_wipe(transaction)

    def create_transaction_for_local_minting(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        supply_to_mint: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_local_minting(
            sender=sender.address,
            token_identifier=token_identifier,
            supply_to_mint=supply_to_mint,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_local_mint(self, transaction_on_network: TransactionOnNetwork) -> list[MintOutcome]:
        return self.parser.parse_local_mint(transaction_on_network)

    def await_completed_local_mint(self, transaction_hash: Union[str, bytes]) -> list[MintOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_local_mint(transaction)

    def create_transaction_for_local_burning(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        supply_to_burn: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_local_burning(
            sender=sender.address,
            token_identifier=token_identifier,
            supply_to_burn=supply_to_burn,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_local_burn(self, transaction_on_network: TransactionOnNetwork) -> list[BurnOutcome]:
        return self.parser.parse_local_burn(transaction_on_network)

    def await_completed_local_burn(self, transaction_hash: Union[str, bytes]) -> list[BurnOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_local_burn(transaction)

    def create_transaction_for_updating_attributes(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        attributes: bytes,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_updating_attributes(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            attributes=attributes,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_update_attributes(self, transaction_on_network: TransactionOnNetwork) -> list[UpdateAttributesOutcome]:
        return self.parser.parse_update_attributes(transaction_on_network)

    def await_completed_update_attributes(self, transaction_hash: Union[str, bytes]) -> list[UpdateAttributesOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_update_attributes(transaction)

    def create_transaction_for_adding_quantity(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        quantity_to_add: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_adding_quantity(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            quantity_to_add=quantity_to_add,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_add_quantity(self, transaction_on_network: TransactionOnNetwork) -> list[AddQuantityOutcome]:
        return self.parser.parse_add_quantity(transaction_on_network)

    def await_completed_add_quantity(self, transaction_hash: Union[str, bytes]) -> list[AddQuantityOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_add_quantity(transaction)

    def create_transaction_for_burning_quantity(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        quantity_to_burn: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_burning_quantity(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            quantity_to_burn=quantity_to_burn,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_burn_quantity(self, transaction_on_network: TransactionOnNetwork) -> list[BurnQuantityOutcome]:
        return self.parser.parse_burn_quantity(transaction_on_network)

    def await_completed_burn_quantity(self, transaction_hash: Union[str, bytes]) -> list[BurnQuantityOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_burn_quantity(transaction)

    def create_transaction_for_modifying_royalties(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        new_royalties: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_modifying_royalties(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            new_royalties=new_royalties,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_modify_royalties(self, transaction_on_network: TransactionOnNetwork) -> list[ModifyRoyaltiesOutcome]:
        return self.parser.parse_modify_royalties(transaction_on_network)

    def await_completed_modify_royalties(self, transaction_hash: Union[str, bytes]) -> list[ModifyRoyaltiesOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_modify_royalties(transaction)

    def create_transaction_for_setting_new_uris(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        new_uris: list[str],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_setting_new_uris(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            new_uris=new_uris,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_set_new_uris(self, transaction_on_network: TransactionOnNetwork) -> list[SetNewUrisOutcome]:
        return self.parser.parse_set_new_uris(transaction_on_network)

    def await_completed_set_new_uris(self, transaction_hash: Union[str, bytes]) -> list[SetNewUrisOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_set_new_uris(transaction)

    def create_transaction_for_modifying_creator(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_modifying_creator(
            sender=sender.address, token_identifier=token_identifier, token_nonce=token_nonce
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_modify_creator(self, transaction_on_network: TransactionOnNetwork) -> list[ModifyCreatorOutcome]:
        return self.parser.parse_modify_creator(transaction_on_network)

    def await_completed_modify_creator(self, transaction_hash: Union[str, bytes]) -> list[ModifyCreatorOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_modify_creator(transaction)

    def create_transaction_for_updating_metadata(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        new_token_name: str,
        new_royalties: int,
        new_hash: str,
        new_attributes: bytes,
        new_uris: list[str],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_updating_metadata(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            new_token_name=new_token_name,
            new_royalties=new_royalties,
            new_hash=new_hash,
            new_attributes=new_attributes,
            new_uris=new_uris,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_update_metadata(self, transaction_on_network: TransactionOnNetwork) -> list[UpdateMetadataOutcome]:
        return self.parser.parse_update_metadata(transaction_on_network)

    def await_completed_update_metadata(self, transaction_hash: Union[str, bytes]) -> list[UpdateMetadataOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_update_metadata(transaction)

    def create_transaction_for_nft_metadata_recreate(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        new_token_name: str,
        new_royalties: int,
        new_hash: str,
        new_attributes: bytes,
        new_uris: list[str],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_nft_metadata_recreate(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            new_token_name=new_token_name,
            new_royalties=new_royalties,
            new_hash=new_hash,
            new_attributes=new_attributes,
            new_uris=new_uris,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_metadata_recreate(self, transaction_on_network: TransactionOnNetwork) -> list[MetadataRecreateOutcome]:
        return self.parser.parse_metadata_recreate(transaction_on_network)

    def await_completed_metadata_recreate(self, transaction_hash: Union[str, bytes]) -> list[MetadataRecreateOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_metadata_recreate(transaction)

    def create_transaction_for_changing_token_to_dynamic(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        """The following token types cannot be changed to dynamic: FungibleESDT, NonFungibleESDT, NonFungibleESDTv2"""
        transaction = self.factory.create_transaction_for_changing_token_to_dynamic(
            sender=sender.address,
            token_identifier=token_identifier,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_change_token_to_dynamic(
        self, transaction_on_network: TransactionOnNetwork
    ) -> list[ChangeTokenToDynamicOutcome]:
        return self.parser.parse_change_token_to_dynamic(transaction_on_network)

    def await_completed_change_token_to_dynamic(
        self, transaction_hash: Union[str, bytes]
    ) -> list[ChangeTokenToDynamicOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_change_token_to_dynamic(transaction)

    def create_transaction_for_updating_token_id(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_updating_token_id(
            sender=sender.address,
            token_identifier=token_identifier,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def await_completed_update_token_id(self, transaction_hash: Union[str, bytes]) -> TransactionOnNetwork:
        return self.network_provider.await_transaction_completed(transaction_hash)

    def create_transaction_for_registering_dynamic_token(
        self,
        sender: IAccount,
        nonce: int,
        token_name: str,
        token_ticker: str,
        token_type: TokenType,
        denominator: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_registering_dynamic_token(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            token_type=token_type,
            denominator=denominator,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_register_dynamic_token(
        self, transaction_on_network: TransactionOnNetwork
    ) -> list[RegisterDynamicOutcome]:
        return self.parser.parse_register_dynamic_token(transaction_on_network)

    def await_completed_register_dynamic_token(
        self, transaction_hash: Union[str, bytes]
    ) -> list[RegisterDynamicOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_register_dynamic_token(transaction)

    def create_transaction_for_registering_dynamic_and_setting_roles(
        self,
        sender: IAccount,
        nonce: int,
        token_name: str,
        token_ticker: str,
        token_type: TokenType,
        denominator: Optional[int] = None,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_registering_dynamic_and_setting_roles(
            sender=sender.address,
            token_name=token_name,
            token_ticker=token_ticker,
            token_type=token_type,
            denominator=denominator,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def parse_register_dynamic_token_and_setting_roles(
        self, transaction_on_network: TransactionOnNetwork
    ) -> list[RegisterDynamicOutcome]:
        return self.parser.parse_register_dynamic_and_setting_roles(transaction_on_network)

    def await_completed_register_dynamic_token_and_setting_roles(
        self, transaction_hash: Union[str, bytes]
    ) -> list[RegisterDynamicOutcome]:
        transaction = self.network_provider.await_transaction_completed(transaction_hash)
        return self.parse_register_dynamic_token_and_setting_roles(transaction)

    def create_transaction_for_transferring_ownership(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        new_owner: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_transferring_ownership(
            sender=sender.address,
            token_identifier=token_identifier,
            new_owner=new_owner,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_freezing_single_nft(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        user: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_freezing_single_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            user=user,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_unfreezing_single_nft(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        user: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_unfreezing_single_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            user=user,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_changing_sft_to_meta_esdt(
        self,
        sender: IAccount,
        nonce: int,
        collection: str,
        num_decimals: int,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_changing_sft_to_meta_esdt(
            sender=sender.address, collection=collection, num_decimals=num_decimals
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_transferring_nft_create_role(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        user: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_transferring_nft_create_role(
            sender=sender.address, token_identifier=token_identifier, user=user
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_stopping_nft_creation(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_stopping_nft_creation(
            sender=sender.address, token_identifier=token_identifier
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transaction_for_wiping_single_nft(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        user: Address,
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transaction_for_wiping_single_nft(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            user=user,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction

    def create_transction_for_adding_uris(
        self,
        sender: IAccount,
        nonce: int,
        token_identifier: str,
        token_nonce: int,
        uris: list[str],
        guardian: Optional[Address] = None,
        relayer: Optional[Address] = None,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
    ) -> Transaction:
        transaction = self.factory.create_transction_for_adding_uris(
            sender=sender.address,
            token_identifier=token_identifier,
            token_nonce=token_nonce,
            uris=uris,
        )

        transaction.guardian = guardian
        transaction.relayer = relayer
        transaction.nonce = nonce

        self._set_version_and_options_for_hash_signing(sender, transaction)
        self._set_transaction_gas_options(transaction, gas_limit, gas_price)
        self._set_version_and_options_for_guardian(transaction)
        transaction.signature = sender.sign_transaction(transaction)

        return transaction
