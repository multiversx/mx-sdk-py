from pathlib import Path
from typing import Optional, Union

from multiversx_sdk.abi.address_value import AddressValue
from multiversx_sdk.abi.biguint_value import BigUIntValue
from multiversx_sdk.abi.bytes_value import BytesValue
from multiversx_sdk.abi.interface import ISingleValue
from multiversx_sdk.abi.serializer import Serializer
from multiversx_sdk.abi.small_int_values import U32Value
from multiversx_sdk.builders.transaction_builder import TransactionBuilder
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.constants import STAKING_SMART_CONTRACT_ADDRESS_HEX
from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transactions_factory_config import TransactionsFactoryConfig
from multiversx_sdk.validators.validators_signers import ValidatorsSigners
from multiversx_sdk.wallet.validator_keys import ValidatorPublicKey


class ValidatorsTransactionsFactory:
    def __init__(self, config: TransactionsFactoryConfig) -> None:
        self.config = config
        self.serializer = Serializer()

    def create_transaction_for_staking(
        self,
        sender: Address,
        validators_file: Union[Path, ValidatorsSigners],
        amount: int,
        rewards_address: Optional[Address] = None,
    ) -> Transaction:
        if isinstance(validators_file, Path):
            validators_file = ValidatorsSigners.new_from_pem(validators_file)

        data_parts = self._prepare_data_parts_for_staking(
            node_operator=sender,
            validators_file=validators_file,
            rewards_address=rewards_address,
        )

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_staking * validators_file.get_num_of_nodes(),
            add_data_movement_gas=True,
            amount=amount,
        ).build()

        return transaction

    def _prepare_data_parts_for_staking(
        self,
        node_operator: Address,
        validators_file: ValidatorsSigners,
        rewards_address: Optional[Address] = None,
    ) -> list[str]:
        data_parts = ["stake"]

        num_of_nodes = validators_file.get_num_of_nodes()

        call_arguments: list[ISingleValue] = []
        call_arguments.append(U32Value(num_of_nodes))

        validator_signers = validators_file.get_signers()

        for validator in validator_signers:
            signed_message = validator.sign(node_operator.get_public_key())

            call_arguments.append(BytesValue(validator.secret_key.generate_public_key().buffer))
            call_arguments.append(BytesValue(signed_message))

        if rewards_address:
            call_arguments.append(AddressValue.new_from_address(rewards_address))

        args = self.serializer.serialize_to_parts(call_arguments)
        return data_parts + [arg.hex() for arg in args]

    def create_transaction_for_topping_up(
        self,
        sender: Address,
        amount: int,
    ) -> Transaction:
        data = ["stake"]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data,
            gas_limit=self.config.gas_limit_for_topping_up,
            add_data_movement_gas=True,
            amount=amount,
        ).build()

        return transaction

    def create_transaction_for_unstaking(
        self,
        sender: Address,
        public_keys: list[ValidatorPublicKey],
    ) -> Transaction:
        data_parts = ["unStake"] + [key.hex() for key in public_keys]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_unstaking * len(public_keys),
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_unjailing(
        self,
        sender: Address,
        public_keys: list[ValidatorPublicKey],
        amount: int,
    ) -> Transaction:
        data_parts = ["unJail"] + [key.hex() for key in public_keys]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_unjailing * len(public_keys),
            add_data_movement_gas=True,
            amount=amount,
        ).build()

        return transaction

    def create_transaction_for_unbonding(
        self,
        sender: Address,
        public_keys: list[ValidatorPublicKey],
    ) -> Transaction:
        data_parts = ["unBond"] + [key.hex() for key in public_keys]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_unbonding * len(public_keys),
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_changing_rewards_address(
        self,
        sender: Address,
        rewards_address: Address,
    ) -> Transaction:
        data_parts = ["changeRewardAddress", rewards_address.to_hex()]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_changing_rewards_address,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_claiming(self, sender: Address) -> Transaction:
        data_parts = ["claim"]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_claiming,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_unstaking_nodes(
        self,
        sender: Address,
        public_keys: list[ValidatorPublicKey],
    ) -> Transaction:
        data_parts = ["unStakeNodes"] + [key.hex() for key in public_keys]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_unstaking_nodes * len(public_keys),
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_unstaking_tokens(self, sender: Address, amount: int) -> Transaction:
        data_parts = ["unStakeTokens", self.serializer.serialize([BigUIntValue(amount)])]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_unstaking_tokens,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_unbonding_nodes(
        self,
        sender: Address,
        public_keys: list[ValidatorPublicKey],
    ) -> Transaction:
        data_parts = ["unBondNodes"] + [key.hex() for key in public_keys]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_unbonding_nodes * len(public_keys),
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_unbonding_tokens(self, sender: Address, amount: int) -> Transaction:
        data_parts = ["unBondTokens", self.serializer.serialize([BigUIntValue(amount)])]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_unbonding_tokens,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_cleaning_registered_data(self, sender: Address) -> Transaction:
        data_parts = ["cleanRegisteredData"]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_cleaning_registered_data,
            add_data_movement_gas=True,
        ).build()

        return transaction

    def create_transaction_for_restaking_unstaked_nodes(
        self,
        sender: Address,
        public_keys: list[ValidatorPublicKey],
    ) -> Transaction:
        data_parts = ["reStakeUnStakedNodes"] + [key.hex() for key in public_keys]

        transaction = TransactionBuilder(
            config=self.config,
            sender=sender,
            receiver=Address.new_from_hex(STAKING_SMART_CONTRACT_ADDRESS_HEX),
            data_parts=data_parts,
            gas_limit=self.config.gas_limit_for_restaking_unstaked_tokens * len(public_keys),
            add_data_movement_gas=True,
        ).build()

        return transaction
