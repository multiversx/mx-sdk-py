import base64
import json
from typing import Any, Dict, Optional

from multiversx_sdk_core.address import Address
from multiversx_sdk_core.errors import ErrInvalidRelayerV1BuilderArguments
from multiversx_sdk_core.interfaces import (IAddress, INetworkConfig, INonce,
                                            ITransactionOptions,
                                            ITransactionVersion)
from multiversx_sdk_core.transaction import Transaction
from multiversx_sdk_core.transaction_payload import TransactionPayload


class RelayedTransactionV1Builder:
    def __init__(
        self,
        inner_transaction: Optional[Transaction] = None,
        relayer_address: Optional[IAddress] = None,
        relayer_nonce: Optional[INonce] = None,
        network_config: Optional[INetworkConfig] = None,
        relayed_transaction_options: Optional[ITransactionOptions] = None,
        relayed_transaction_version: Optional[ITransactionVersion] = None,
        relayed_transaction_guardian: Optional[IAddress] = None,
    ) -> None:
        self.inner_transaction = inner_transaction
        self.relayer_address = relayer_address
        self.relayer_nonce = relayer_nonce
        self.network_config = network_config
        self.relayed_transaction_options = relayed_transaction_options
        self.relayed_transaction_version = relayed_transaction_version
        self.relayed_transaction_guardian = relayed_transaction_guardian

    def set_inner_transaction(self, transaction: Transaction) -> None:
        self.inner_transaction = transaction

    def set_network_config(self, network_config: INetworkConfig) -> None:
        self.network_config = network_config

    def set_relayer_address(self, relayer_address: IAddress) -> None:
        self.relayer_address = relayer_address

    def set_relayer_nonce(self, relayer_nonce: INonce) -> None:
        self.relayer_nonce = relayer_nonce

    def set_relayed_transaction_version(
        self, relayed_transaction_version: ITransactionVersion
    ) -> None:
        self.relayed_transaction_version = relayed_transaction_version

    def set_relayed_transaction_options(
        self, relayed_transaction_options: ITransactionOptions
    ) -> None:
        self.relayed_transaction_options = relayed_transaction_options

    def set_relayed_transaction_guardian(
        self, relayed_transaction_guardian: IAddress
    ) -> None:
        self.relayed_transaction_guardian = relayed_transaction_guardian

    def build(self) -> Transaction:
        if (
            not self.inner_transaction
            or not self.network_config
            or not self.relayer_address
            or not self.inner_transaction.signature
        ):
            raise ErrInvalidRelayerV1BuilderArguments()

        serialized_transaction = self._prepare_inner_transaction()
        data = f"relayedTx@{serialized_transaction.encode().hex()}"
        payload = TransactionPayload.from_str(data)

        gas_limit = (
            self.network_config.min_gas_limit
            + self.network_config.gas_per_data_byte * payload.length()
            + self.inner_transaction.gas_limit
        )
        relayed_transaction = Transaction(
            chain_id=self.network_config.chain_id,
            sender=self.relayer_address,
            receiver=self.inner_transaction.sender,
            value=0,
            nonce=self.relayer_nonce,
            gas_limit=gas_limit,
            data=payload,
            version=self.relayed_transaction_version,
            options=self.relayed_transaction_options,
            guardian=self.relayed_transaction_guardian,
        )

        if self.relayer_nonce:
            self.set_relayer_nonce(self.relayer_nonce)

        return relayed_transaction

    def _prepare_inner_transaction(self) -> str:
        if not self.inner_transaction:
            return ""

        sender = Address.from_bech32(self.inner_transaction.sender.bech32()).hex()
        receiver = Address.from_bech32(self.inner_transaction.receiver.bech32()).hex()

        tx: Dict[str, Any] = {
            "nonce": self.inner_transaction.nonce,
            "sender": base64.b64encode(bytes.fromhex(sender)).decode(),
            "receiver": base64.b64encode(bytes.fromhex(receiver)).decode(),
            "value": int(self.inner_transaction.value.__str__(), 10),
            "gasPrice": self.inner_transaction.gas_price,
            "gasLimit": self.inner_transaction.gas_limit,
            "data": base64.b64encode(self.inner_transaction.data.data).decode(),
            "signature": base64.b64encode(self.inner_transaction.signature).decode(),
            "chainID": base64.b64encode(
                self.inner_transaction.chainID.encode()
            ).decode(),
            "version": self.inner_transaction.version,
        }

        if self.inner_transaction.options:
            tx["options"] = self.inner_transaction.options

        if self.inner_transaction.guardian:
            guardian = Address.from_bech32(
                self.inner_transaction.guardian.bech32()
            ).hex()
            tx["guardian"] = base64.b64encode(bytes.fromhex(guardian)).decode()

        if self.inner_transaction.guardian_signature:
            tx["guardianSignature"] = base64.b64encode(
                self.inner_transaction.guardian_signature
            ).decode()

        if self.inner_transaction.sender_username:
            tx["sndUserName"] = base64.b64encode(self.inner_transaction.sender_username.encode()).decode()

        if self.inner_transaction.receiver_username:
            tx[f"rcvUserName"] = base64.b64encode(self.inner_transaction.receiver_username.encode()).decode()

        return json.dumps(tx, separators=(",", ":"))
