from typing import Any, List, Optional

from erdpy_core.constants import ARGS_SEPARATOR
from erdpy_core.interfaces import (IAddress, IChainID, ICodeMetadata,
                                   IGasLimit, IGasPrice, INonce,
                                   ITransactionBuildersConfiguration,
                                   ITransactionOptions, ITransactionValue,
                                   ITransactionVersion)
from erdpy_core.serializer import arg_to_buffer, args_to_buffers
from erdpy_core.transaction import Transaction
from erdpy_core.transaction_builder_configuration import \
    DefaultTransactionBuildersConfiguration
from erdpy_core.transaction_payload import TransactionPayload


class BaseBuilder:
    def __init__(self,
                 chain_id: IChainID,
                 nonce: Optional[INonce] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None,
                 transaction_version: Optional[ITransactionVersion] = None,
                 transaction_options: Optional[ITransactionOptions] = None
                 ) -> None:
        self.chain_id = chain_id
        self.nonce = nonce
        self.gas_limit = gas_limit
        self.gas_price = gas_price
        self.transaction_version = transaction_version
        self.transaction_options = transaction_options
        self.configuration: ITransactionBuildersConfiguration = DefaultTransactionBuildersConfiguration()

    def build_transaction(self) -> Transaction:
        chain_id = self.chain_id
        sender = self._get_sender()
        receiver = self._get_receiver()
        gas_limit = self._get_gas_limit()
        gas_price = self._get_gas_price()
        nonce = self.nonce or 0
        value = self._get_value()
        data = self.build_payload()
        version = self._get_transaction_version()
        options = self._get_transaction_options()

        return Transaction(
            chain_id=chain_id,
            sender=sender,
            receiver=receiver,
            gas_limit=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            value=value,
            data=data,
            version=version,
            options=options
        )

    def build_payload(self) -> TransactionPayload:
        function_name = self._get_function_name()
        arguments = self.build_arguments()
        data_parts = [arg.hex() for arg in arguments]

        if function_name:
            # Prepend function name
            data_parts = [function_name] + data_parts

        data = ARGS_SEPARATOR.join(data_parts)
        payload = TransactionPayload.from_str(data)
        return payload

    def build_arguments(self) -> List[bytes]:
        return []

    def _get_sender(self) -> IAddress:
        raise NotImplementedError()

    def _get_receiver(self) -> IAddress:
        raise NotImplementedError()

    def _get_value(self) -> ITransactionValue:
        return 0

    def _get_gas_limit(self) -> IGasLimit:
        assert self.gas_limit, "gas_limit isn't set, nor computed"
        return self.gas_limit

    def _get_gas_price(self):
        return self.gas_price or self.configuration.gas_price

    def _get_transaction_version(self):
        return self.transaction_version or self.configuration.transaction_version

    def _get_transaction_options(self):
        return self.transaction_options or self.configuration.transaction_options

    def _get_function_name(self) -> Optional[str]:
        return None


class ContractDeploymentBuilder(BaseBuilder):
    def __init__(self,
                 chain_id: IChainID,
                 deployer: IAddress,
                 code: bytes, code_metadata: ICodeMetadata, deploy_arguments: List[Any] = [],
                 nonce: Optional[INonce] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None,
                 transaction_version: Optional[ITransactionVersion] = None,
                 transaction_options: Optional[ITransactionOptions] = None) -> None:
        super().__init__(chain_id, nonce, gas_limit, gas_price, transaction_version, transaction_options)

        self.deployer = deployer
        self.code = code
        self.code_metadata = code_metadata,
        self.deploy_arguments = deploy_arguments

    def _get_sender(self) -> IAddress:
        return self.deployer

    def _get_receiver(self) -> IAddress:
        return self.configuration.deployment_address

    def build_arguments(self) -> List[bytes]:
        return [self.code, arg_to_buffer(self.code_metadata)] + args_to_buffers(self.deploy_arguments)
