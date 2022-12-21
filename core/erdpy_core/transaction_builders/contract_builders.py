from typing import Any, List, Optional, Protocol, Sequence

from erdpy_core.constants import VM_TYPE_WASM_VM
from erdpy_core.interfaces import (IAddress, ICodeMetadata, IGasLimit,
                                   IGasPrice, INonce, ITokenPayment,
                                   ITransactionValue)
from erdpy_core.serializer import arg_to_string, args_to_strings
from erdpy_core.transaction_builders.transaction_builder import (
    ITransactionBuilderConfiguration, TransactionBuilder)


class IContractDeploymentConfiguration(ITransactionBuilderConfiguration, Protocol):
    deployment_address: IAddress


class ContractDeploymentBuilder(TransactionBuilder):
    def __init__(self,
                 config: IContractDeploymentConfiguration,
                 code: bytes,
                 code_metadata: ICodeMetadata,
                 deploy_arguments: Sequence[Any],
                 owner: IAddress,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.sender = owner
        self.receiver = config.deployment_address
        self.code = code
        self.code_metadata = code_metadata
        self.deploy_arguments = deploy_arguments

    def _build_payload_parts(self) -> List[str]:
        return [
            self.code.hex(),
            arg_to_string(VM_TYPE_WASM_VM),
            arg_to_string(self.code_metadata)
        ] + args_to_strings(self.deploy_arguments)


class ContractUpgradeBuilder(TransactionBuilder):
    def __init__(self,
                 config: ITransactionBuilderConfiguration,
                 contract: IAddress,
                 code: bytes,
                 code_metadata: ICodeMetadata,
                 upgrade_arguments: Sequence[Any],
                 owner: IAddress,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.sender = owner
        self.receiver = contract
        self.code = code
        self.code_metadata = code_metadata
        self.upgrade_arguments = upgrade_arguments
        self.owner = owner

    def _build_payload_parts(self) -> List[str]:
        return [
            "upgradeContract",
            self.code.hex(),
            arg_to_string(self.code_metadata)
        ] + args_to_strings(self.upgrade_arguments)


class ContractCallBuilder(TransactionBuilder):
    def __init__(self,
                 config: ITransactionBuilderConfiguration,
                 contract: IAddress,
                 function_name: str,
                 call_arguments: Sequence[Any],
                 caller: IAddress,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 esdt_transfers: Sequence[ITokenPayment] = [],
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
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

    def _build_payload_parts(self) -> List[str]:
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

        return parts

    def _has_single_esdt_transfer(self) -> bool:
        return len(self.esdt_transfers) == 1 and self.esdt_transfers[0].is_fungible()

    def _has_single_nft_transfer(self) -> bool:
        return len(self.esdt_transfers) == 1 and not self.esdt_transfers[0].is_fungible()

    def _has_multiple_transfers(self) -> bool:
        return len(self.esdt_transfers) > 1
