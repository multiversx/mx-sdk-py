from typing import Any, List, Optional

from erdpy_core.constants import ARGS_SEPARATOR, VM_TYPE_WASM_VM
from erdpy_core.contract_query import ContractQuery
from erdpy_core.interfaces import (IAddress, IChainID, ICodeMetadata,
                                   IGasLimit, IGasPrice, INonce, ITokenPayment,
                                   ITransactionValue)
from erdpy_core.serializer import arg_to_string, args_to_strings
from erdpy_core.transaction_builders.base_builder import BaseBuilder
from erdpy_core.transaction_payload import TransactionPayload


class ContractDeploymentBuilder(BaseBuilder):
    def __init__(self,
                 chain_id: IChainID,
                 code: bytes,
                 code_metadata: ICodeMetadata,
                 deploy_arguments: List[Any],
                 owner: IAddress,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(chain_id, nonce, value, gas_limit, gas_price)
        self.code = code
        self.code_metadata = code_metadata
        self.deploy_arguments = deploy_arguments
        self.owner = owner

    def _get_sender(self) -> IAddress:
        return self.owner

    def _get_receiver(self) -> IAddress:
        return self.configuration.deployment_address

    def build_payload(self) -> TransactionPayload:
        parts = [
            self.code.hex(),
            arg_to_string(VM_TYPE_WASM_VM),
            arg_to_string(self.code_metadata)
        ] + args_to_strings(self.deploy_arguments)

        data = ARGS_SEPARATOR.join(parts)
        return TransactionPayload.from_str(data)


class ContractUpgradeBuilder(BaseBuilder):
    def __init__(self,
                 chain_id: IChainID,
                 contract: IAddress,
                 code: bytes,
                 code_metadata: ICodeMetadata,
                 upgrade_arguments: List[Any],
                 owner: IAddress,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(chain_id, nonce, value, gas_limit, gas_price)
        self.contract = contract
        self.code = code
        self.code_metadata = code_metadata
        self.upgrade_arguments = upgrade_arguments
        self.owner = owner

    def _get_sender(self) -> IAddress:
        return self.owner

    def _get_receiver(self) -> IAddress:
        return self.contract

    def build_payload(self) -> TransactionPayload:
        parts = [
            "upgradeContract",
            self.code.hex(),
            arg_to_string(self.code_metadata)
        ] + args_to_strings(self.upgrade_arguments)

        data = ARGS_SEPARATOR.join(parts)
        return TransactionPayload.from_str(data)


class ContractCallBuilder(BaseBuilder):
    def __init__(self,
                 chain_id: IChainID,
                 contract: IAddress,
                 function_name: str,
                 call_arguments: List[Any],
                 caller: IAddress,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 esdt_transfers: List[ITokenPayment] = [],
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(chain_id, nonce, value, gas_limit, gas_price)
        self.contract = contract
        self.function_name = function_name
        self.call_arguments = call_arguments
        self.caller = caller
        self.esdt_transfers = esdt_transfers

    def _get_sender(self) -> IAddress:
        return self.caller

    def _get_receiver(self) -> IAddress:
        receiver_is_same_as_sender = self._has_multiple_transfers() or self._has_single_nft_transfer()
        return self.caller if receiver_is_same_as_sender else self.contract

    def build_payload(self) -> TransactionPayload:
        parts: List[str] = []

        if self._has_single_esdt_transfer():
            transfer = self.esdt_transfers[0]
            parts = [
                "ESDTTransfer",
                arg_to_string(transfer.token_identifier),
                arg_to_string(transfer.amount_as_integer),
                arg_to_string(self.function_name),
                *args_to_strings(self.call_arguments)
            ]
        elif self._has_single_nft_transfer():
            transfer = self.esdt_transfers[0]
            parts = [
                "ESDTNFTTransfer",
                arg_to_string(transfer.token_identifier),
                arg_to_string(transfer.token_nonce),
                arg_to_string(transfer.amount_as_integer),
                arg_to_string(self.contract),
                arg_to_string(self.function_name),
                *args_to_strings(self.call_arguments)
            ]
        elif self._has_multiple_transfers():
            parts = [
                "MultiESDTNFTTransfer",
                arg_to_string(self.contract),
                arg_to_string(len(self.esdt_transfers))
            ]

            for transfer in self.esdt_transfers:
                parts.extend([
                    arg_to_string(transfer.token_identifier),
                    arg_to_string(transfer.token_nonce),
                    arg_to_string(transfer.amount_as_integer)
                ])

            parts.extend([
                arg_to_string(self.function_name),
                *args_to_strings(self.call_arguments)
            ])
        else:
            parts = [self.function_name] + args_to_strings(self.call_arguments)

        data = ARGS_SEPARATOR.join(parts)
        return TransactionPayload.from_str(data)

    def build_query(self) -> ContractQuery:
        query = ContractQuery(
            contract=self.contract,
            function=self.function_name,
            encoded_arguments=args_to_strings(self.call_arguments),
            caller=self.caller
        )

        return query

    def _has_single_esdt_transfer(self) -> bool:
        return len(self.esdt_transfers) == 1 and self.esdt_transfers[0].token_nonce == 0

    def _has_single_nft_transfer(self) -> bool:
        return len(self.esdt_transfers) == 1 and self.esdt_transfers[0].token_nonce > 0

    def _has_multiple_transfers(self) -> bool:
        return len(self.esdt_transfers) > 1
