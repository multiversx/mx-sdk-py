from pathlib import Path
from typing import Any, List, Optional, Protocol, Tuple

from Cryptodome.Hash import keccak

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.constants import (ARGS_SEPARATOR,
                                           CONTRACT_DEPLOY_ADDRESS,
                                           DEFAULT_HRP,
                                           TRANSACTION_OPTIONS_DEFAULT,
                                           TRANSACTION_VERSION_DEFAULT,
                                           VM_TYPE_WASM_VM)
from multiversx_sdk_core.interfaces import (IAddress, IChainID, IGasLimit,
                                            IGasPrice, INonce,
                                            ITransactionValue)
from multiversx_sdk_core.serializer import arg_to_string
from multiversx_sdk_core.transaction import Transaction
from multiversx_sdk_core.transaction_payload import TransactionPayload
from multiversx_sdk_core.utils import read_binary_file


class IConfig(Protocol):
    chain_id: IChainID


class CodeMetadata:
    def __init__(self, upgradeable: bool = True, readable: bool = True, payable: bool = False, payable_by_sc: bool = False) -> None:
        self.upgradeable = upgradeable
        self.readable = readable
        self.payable = payable
        self.payable_by_sc = payable_by_sc

    def to_hex(self) -> str:
        flag_value_pairs = [
            (0x01_00, self.upgradeable),
            (0x04_00, self.readable),
            (0x00_02, self.payable),
            (0x00_04, self.payable_by_sc)
        ]
        metadata_value = self.sum_flag_values(flag_value_pairs)
        return f"{metadata_value:04X}"

    def sum_flag_values(self, flag_value_pairs: List[Tuple[int, bool]]) -> int:
        value_sum = 0
        for value, flag in flag_value_pairs:
            if flag:
                value_sum += value
        return value_sum


class SmartContractFactory:
    def __init__(self, config: IConfig) -> None:
        self.config = config

    def deploy(self,
               deployer: IAddress,
               nonce: INonce,
               bytecode_path: Path,
               gas_limit: IGasLimit,
               arguments: Optional[List[Any]] = None,
               value: Optional[ITransactionValue] = None,
               gas_price: Optional[IGasPrice] = None,
               is_upgradeable: bool = True,
               is_readable: bool = True,
               is_payable: bool = False,
               is_payable_by_sc: bool = False) -> Transaction:
        bytecode = read_binary_file(bytecode_path)
        metadata = CodeMetadata(is_upgradeable, is_readable, is_payable, is_payable_by_sc)
        arguments = arguments or []

        parts = [
            arg_to_string(bytecode),
            arg_to_string(VM_TYPE_WASM_VM),
            metadata.to_hex()
        ]

        for arg in arguments:
            parts.append(arg_to_string(arg))

        transaction = self.create_transaction(
            sender=deployer,
            receiver=Address.from_bech32(CONTRACT_DEPLOY_ADDRESS),
            data_parts=parts,
            gas_limit=gas_limit,
            gas_price=gas_price,
            nonce=nonce,
            value=value
        )

        return transaction

    def execute(self,
                sender: IAddress,
                contract_address: IAddress,
                function: str,
                gas_limit: IGasLimit,
                arguments: Optional[List[Any]] = None,
                nonce: Optional[INonce] = None
                ) -> Transaction:
        arguments = arguments or []

        parts = [function]

        for arg in arguments:
            parts.append(arg_to_string(arg))

        trasaction = self.create_transaction(
            sender=sender,
            receiver=contract_address,
            data_parts=parts,
            gas_limit=gas_limit,
            nonce=nonce
        )

        return trasaction

    def upgrade(self,
                sender: IAddress,
                contract: IAddress,
                bytecode_path: Path,
                gas_limit: IGasLimit,
                arguments: Optional[List[Any]] = None,
                nonce: Optional[INonce] = None,
                is_upgradeable: bool = True,
                is_readable: bool = True,
                is_payable: bool = False,
                is_payable_by_sc: bool = False
                ) -> Transaction:
        arguments = arguments or []
        bytecode = read_binary_file(bytecode_path)
        metadata = CodeMetadata(is_upgradeable, is_readable, is_payable, is_payable_by_sc)

        parts = [
            "upgradeContract",
            arg_to_string(bytecode),
            metadata.to_hex()
        ]

        for arg in arguments:
            parts.append(arg_to_string(arg))

        transaction = self.create_transaction(
            sender=sender,
            receiver=contract,
            data_parts=parts,
            gas_limit=gas_limit,
            nonce=nonce
        )

        return transaction

    def compute_contract_address(self, deployer: IAddress, nonce: INonce) -> Address:
        """
        8 bytes of zero + 2 bytes for VM type + 20 bytes of hash(owner) + 2 bytes of shard(owner)
        """
        owner_bytes = bytes.fromhex(deployer.hex())
        nonce_bytes = nonce.to_bytes(8, byteorder="little")
        bytes_to_hash = owner_bytes + nonce_bytes
        address = keccak.new(digest_bits=256).update(bytes_to_hash).digest()
        address = bytes([0] * 8) + bytes([5, 0]) + address[10:30] + owner_bytes[30:]
        return Address(address, DEFAULT_HRP)

    def create_transaction(
            self,
            sender: IAddress,
            receiver: IAddress,
            data_parts: List[str],
            gas_limit: IGasLimit,
            gas_price: Optional[IGasPrice] = None,
            nonce: Optional[INonce] = None,
            value: Optional[ITransactionValue] = None
    ) -> Transaction:
        data = self._build_transaction_payload(data_parts)
        version = TRANSACTION_VERSION_DEFAULT
        options = TRANSACTION_OPTIONS_DEFAULT

        return Transaction(
            chain_id=self.config.chain_id,
            sender=sender,
            receiver=receiver,
            gas_limit=gas_limit,
            gas_price=gas_price,
            value=value,
            nonce=nonce,
            data=data,
            version=version,
            options=options
        )

    def _build_transaction_payload(self, parts: List[str]) -> TransactionPayload:
        data = ARGS_SEPARATOR.join(parts)
        return TransactionPayload.from_str(data)
