from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.errors import ParseTransactionOnNetworkError
from multiversx_sdk.core.transaction_on_network import (
    TransactionEvent,
    TransactionOnNetwork,
    find_events_by_identifier,
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


class TokenManagementTransactionsOutcomeParser:
    def __init__(self) -> None:
        self._serializer = Serializer()

    def parse_issue_fungible(self, transaction: TransactionOnNetwork) -> list[IssueFungibleOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "issue")
        return [IssueFungibleOutcome(self._extract_token_identifier(event)) for event in events]

    def parse_issue_non_fungible(self, transaction: TransactionOnNetwork) -> list[IssueNonFungibleOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "issueNonFungible")
        return [IssueNonFungibleOutcome(self._extract_token_identifier(event)) for event in events]

    def parse_issue_semi_fungible(self, transaction: TransactionOnNetwork) -> list[IssueSemiFungibleOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "issueSemiFungible")
        return [IssueSemiFungibleOutcome(self._extract_token_identifier(event)) for event in events]

    def parse_register_meta_esdt(self, transaction: TransactionOnNetwork) -> list[RegisterMetaEsdtOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "registerMetaESDT")
        return [RegisterMetaEsdtOutcome(self._extract_token_identifier(event)) for event in events]

    def parse_register_and_set_all_roles(
        self, transaction: TransactionOnNetwork
    ) -> list[RegisterAndSetAllRolesOutcome]:
        self._ensure_no_error(transaction.logs.events)

        register_events = find_events_by_identifier(transaction, "registerAndSetAllRoles")
        set_role_events = find_events_by_identifier(transaction, "ESDTSetRole")

        if len(register_events) != len(set_role_events):
            raise ParseTransactionOnNetworkError(
                "The number of `registerAndSetAllRoles` events and `ESDTSetRole` events do not match"
            )

        result: list[RegisterAndSetAllRolesOutcome] = []
        for register_event, set_role_event in zip(register_events, set_role_events):
            identifier = self._extract_token_identifier(register_event)
            roles = self._decode_roles(set_role_event)
            result.append(RegisterAndSetAllRolesOutcome(identifier, roles))

        return result

    def parse_set_burn_role_globally(self, transaction: TransactionOnNetwork) -> None:
        self._ensure_no_error(transaction.logs.events)

    def parse_unset_burn_role_globally(self, transaction: TransactionOnNetwork) -> None:
        self._ensure_no_error(transaction.logs.events)

    def parse_set_special_role(self, transaction: TransactionOnNetwork) -> list[SetSpecialRoleOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTSetRole")
        return [
            SetSpecialRoleOutcome(
                user_address=event.address,
                token_identifier=self._extract_token_identifier(event),
                roles=self._decode_roles(event),
            )
            for event in events
        ]

    def parse_nft_create(self, transaction: TransactionOnNetwork) -> list[NFTCreateOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTNFTCreate")

        return [
            NFTCreateOutcome(
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                initial_quantity=self._extract_amount(event),
            )
            for event in events
        ]

    def parse_local_mint(self, transaction: TransactionOnNetwork) -> list[MintOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTLocalMint")
        return [
            MintOutcome(
                user_address=event.address,
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                minted_supply=self._extract_amount(event),
            )
            for event in events
        ]

    def parse_local_burn(self, transaction: TransactionOnNetwork) -> list[BurnOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTLocalBurn")
        return [
            BurnOutcome(
                user_address=event.address,
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                burnt_supply=self._extract_amount(event),
            )
            for event in events
        ]

    def parse_pause(self, transaction: TransactionOnNetwork) -> list[PauseOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTPause")
        return [PauseOutcome(self._extract_token_identifier(event)) for event in events]

    def parse_unpause(self, transaction: TransactionOnNetwork) -> list[UnPauseOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTUnPause")
        return [UnPauseOutcome(self._extract_token_identifier(event)) for event in events]

    def parse_freeze(self, transaction: TransactionOnNetwork) -> list[FreezeOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTFreeze")
        return [
            FreezeOutcome(
                user_address=self._extract_address(event),
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                balance=self._extract_amount(event),
            )
            for event in events
        ]

    def parse_unfreeze(self, transaction: TransactionOnNetwork) -> list[UnFreezeOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTUnFreeze")
        return [
            UnFreezeOutcome(
                user_address=self._extract_address(event),
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                balance=self._extract_amount(event),
            )
            for event in events
        ]

    def parse_wipe(self, transaction: TransactionOnNetwork) -> list[WipeOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTWipe")
        return [
            WipeOutcome(
                user_address=self._extract_address(event),
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                balance=self._extract_amount(event),
            )
            for event in events
        ]

    def parse_update_attributes(self, transaction: TransactionOnNetwork) -> list[UpdateAttributesOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTNFTUpdateAttributes")
        return [
            UpdateAttributesOutcome(
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                attributes=event.topics[3] if event.topics[3] else b"",
            )
            for event in events
        ]

    def parse_add_quantity(self, transaction: TransactionOnNetwork) -> list[AddQuantityOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTNFTAddQuantity")
        return [
            AddQuantityOutcome(
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                added_quantity=self._extract_amount(event),
            )
            for event in events
        ]

    def parse_burn_quantity(self, transaction: TransactionOnNetwork) -> list[BurnQuantityOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTNFTBurn")
        return [
            BurnQuantityOutcome(
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                burnt_quantity=self._extract_amount(event),
            )
            for event in events
        ]

    def parse_modify_royalties(self, transaction: TransactionOnNetwork) -> list[ModifyRoyaltiesOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTModifyRoyalties")
        return [
            ModifyRoyaltiesOutcome(
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                royalties=self._extract_royalties(event.topics),
            )
            for event in events
        ]

    def _extract_royalties(self, topics: list[bytes]) -> int:
        if not len(topics[3]):
            return 0
        return int.from_bytes(topics[3], byteorder="big", signed=False)

    def parse_set_new_uris(self, transaction: TransactionOnNetwork) -> list[SetNewUrisOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTSetNewURIs")
        return [
            SetNewUrisOutcome(
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                uris=self._extract_uris(event.topics),
            )
            for event in events
        ]

    def _extract_uris(self, topics: list[bytes]) -> list[str]:
        if not len(topics[3]):
            return [""]
        return [topic.decode() for topic in topics[3:]]

    def parse_modify_creator(self, transaction: TransactionOnNetwork) -> list[ModifyCreatorOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTModifyCreator")
        return [
            ModifyCreatorOutcome(
                token_identifier=self._extract_token_identifier(event), nonce=self._extract_nonce(event)
            )
            for event in events
        ]

    def parse_update_metadata(self, transaction: TransactionOnNetwork) -> list[UpdateMetadataOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTMetaDataUpdate")
        return [
            UpdateMetadataOutcome(
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                metadata=event.topics[3] if len(event.topics[3]) else b"",
            )
            for event in events
        ]

    def parse_metadata_recreate(self, transaction: TransactionOnNetwork) -> list[MetadataRecreateOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "ESDTMetaDataRecreate")
        return [
            MetadataRecreateOutcome(
                token_identifier=self._extract_token_identifier(event),
                nonce=self._extract_nonce(event),
                metadata=event.topics[3] if len(event.topics[3]) else b"",
            )
            for event in events
        ]

    def parse_change_token_to_dynamic(self, transaction: TransactionOnNetwork) -> list[ChangeTokenToDynamicOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "changeToDynamic")
        return [
            ChangeTokenToDynamicOutcome(
                token_identifier=self._extract_token_identifier(event),
                token_name=event.topics[1].decode() if len(event.topics[1]) else "",
                ticker=event.topics[2].decode() if len(event.topics[2]) else "",
                token_type=event.topics[3].decode() if len(event.topics[3]) else "",
            )
            for event in events
        ]

    def parse_register_dynamic_token(self, transaction: TransactionOnNetwork) -> list[RegisterDynamicOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "registerDynamic")
        return [
            RegisterDynamicOutcome(
                token_identifier=self._extract_token_identifier(event),
                token_name=event.topics[1].decode() if len(event.topics[1]) else "",
                ticker=event.topics[2].decode() if len(event.topics[2]) else "",
                token_type=event.topics[3].decode() if len(event.topics[3]) else "",
                num_of_decimals=(
                    int.from_bytes(event.topics[4], byteorder="big", signed=False)
                    if len(event.topics) > 4 and event.topics[4]
                    else 0
                ),
            )
            for event in events
        ]

    def parse_register_dynamic_and_setting_roles(
        self, transaction: TransactionOnNetwork
    ) -> list[RegisterDynamicOutcome]:
        self._ensure_no_error(transaction.logs.events)

        events = find_events_by_identifier(transaction, "registerAndSetAllRolesDynamic")
        return [
            RegisterDynamicOutcome(
                token_identifier=self._extract_token_identifier(event),
                token_name=event.topics[1].decode() if len(event.topics[1]) else "",
                ticker=event.topics[2].decode() if len(event.topics[2]) else "",
                token_type=event.topics[3].decode() if len(event.topics[3]) else "",
                num_of_decimals=(
                    int.from_bytes(bytes.fromhex(event.topics[4].decode()), byteorder="big", signed=False)
                    if len(event.topics) > 4 and event.topics[4]
                    else 0
                ),
            )
            for event in events
        ]

    def _ensure_no_error(self, transaction_events: list[TransactionEvent]) -> None:
        for event in transaction_events:
            if event.identifier == "signalError":
                data = event.additional_data[0].decode()[1:] if len(event.additional_data[0]) else ""
                message = event.topics[1].decode()

                raise ParseTransactionOnNetworkError(
                    f"encountered signalError: {message} ({bytes.fromhex(data).decode()})"
                )

    def _decode_roles(self, event: TransactionEvent) -> list[str]:
        encoded_roles = event.topics[3:]
        return [role.decode() for role in encoded_roles]

    def _extract_token_identifier(self, event: TransactionEvent) -> str:
        if not event.topics[0]:
            return ""

        return event.topics[0].decode()

    def _extract_nonce(self, event: TransactionEvent) -> int:
        if not event.topics[1]:
            return 0

        nonce_value = BigUIntValue()
        self._serializer.deserialize_parts([event.topics[1]], [nonce_value])
        return nonce_value.get_payload()

    def _extract_amount(self, event: TransactionEvent) -> int:
        if not event.topics[2]:
            return 0

        amount_value = BigUIntValue()
        self._serializer.deserialize_parts([event.topics[2]], [amount_value])
        return amount_value.get_payload()

    def _extract_address(self, event: TransactionEvent) -> Address:
        if not event.topics[3]:
            raise Exception("No topic found for contract address")

        return Address(event.topics[3])
