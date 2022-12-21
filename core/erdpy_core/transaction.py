import json
from collections import OrderedDict
from typing import Any, Dict, Optional

from erdpy_core.constants import (TRANSACTION_MIN_GAS_PRICE,
                                  TRANSACTION_OPTIONS_DEFAULT,
                                  TRANSACTION_VERSION_DEFAULT)
from erdpy_core.interfaces import (IAddress, IChainID, IGasLimit, IGasPrice,
                                   INonce, ISignature, ITransactionOptions,
                                   ITransactionPayload, ITransactionValue,
                                   ITransactionVersion)
from erdpy_core.transaction_payload import TransactionPayload


class Transaction:
    def __init__(
        self,
        chain_id: IChainID,
        sender: IAddress,
        receiver: IAddress,
        gas_limit: IGasLimit,
        gas_price: Optional[IGasPrice] = None,
        nonce: Optional[INonce] = 0,
        value: Optional[ITransactionValue] = None,
        data: Optional[ITransactionPayload] = None,
        version: Optional[ITransactionVersion] = None,
        options: Optional[ITransactionOptions] = None
    ):
        self.chainID: IChainID = chain_id
        self.sender: IAddress = sender
        self.receiver: IAddress = receiver

        self.gas_limit: IGasLimit = gas_limit
        self.gas_price: IGasPrice = gas_price or TRANSACTION_MIN_GAS_PRICE

        self.nonce: INonce = nonce or 0
        self.value: ITransactionValue = value or 0
        self.data: ITransactionPayload = data or TransactionPayload.empty()

        self.version: ITransactionVersion = version or TRANSACTION_VERSION_DEFAULT
        self.options: ITransactionOptions = options or TRANSACTION_OPTIONS_DEFAULT

        self.signature: ISignature = bytes()

    def serialize_for_signing(self) -> bytes:
        dictionary = self.to_dictionary(with_signature=False)
        serialized = self._dict_to_json(dictionary)
        return serialized

    def to_dictionary(self, with_signature: bool = True) -> Dict[str, Any]:
        dictionary: Dict[str, Any] = OrderedDict()
        dictionary["nonce"] = self.nonce
        dictionary["value"] = str(self.value)

        dictionary["receiver"] = self.receiver.bech32()
        dictionary["sender"] = self.sender.bech32()

        dictionary["gasPrice"] = self.gas_price
        dictionary["gasLimit"] = self.gas_limit

        if self.data.length():
            dictionary["data"] = self.data.encoded()

        dictionary["chainID"] = self.chainID

        if self.version:
            dictionary["version"] = self.version

        if self.options:
            dictionary["options"] = self.options

        if with_signature:
            dictionary["signature"] = self.signature.hex()

        return dictionary

    def _dict_to_json(self, dictionary: Dict[str, Any]) -> bytes:
        serialized = json.dumps(dictionary, separators=(',', ':')).encode("utf8")
        return serialized
