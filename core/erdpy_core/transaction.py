import json
from collections import OrderedDict
from typing import Any, Dict, Union

from erdpy_core.constants import (TRANSACTION_MIN_GAS_PRICE,
                                  TRANSACTION_OPTIONS_DEFAULT,
                                  TRANSACTION_VERSION_DEFAULT)
from erdpy_core.interfaces import (IAddress, IChainID, IGasLimit, IGasPrice,
                                   INonce, ISignature, ITransactionOptions,
                                   ITransactionPayload, ITransactionValue,
                                   ITransactionVersion)


class Transaction:
    def __init__(
        self,
        nonce: INonce,
        value: Union[ITransactionValue, None],
        sender: IAddress,
        receiver: IAddress,
        gas_price: Union[IGasPrice, None],
        gas_limit: IGasLimit,
        data: Union[ITransactionPayload, None],
        chain_id: IChainID,
        version: Union[ITransactionVersion, None],
        options: Union[ITransactionOptions, None]
    ):
        self.nonce = nonce or 0
        self.value = value or "0"
        self.sender = sender
        self.receiver = receiver
        self.gas_price = gas_price or TRANSACTION_MIN_GAS_PRICE
        self.gas_limit = gas_limit
        self.data = data
        self.chainID = chain_id
        self.version = version or TRANSACTION_VERSION_DEFAULT
        self.options = options or TRANSACTION_OPTIONS_DEFAULT
        self.signature = bytes()

    def serialize_for_signing(self) -> bytes:
        dictionary = self.to_dictionary()
        serialized = self._dict_to_json(dictionary)
        return serialized

    def _dict_to_json(self, dictionary: Dict[str, Any]) -> bytes:
        serialized = json.dumps(dictionary, separators=(',', ':')).encode("utf8")
        return serialized

    def to_dictionary(self) -> Dict[str, Any]:
        dictionary: Dict[str, Any] = OrderedDict()
        dictionary["nonce"] = self.nonce
        dictionary["value"] = self.value

        dictionary["receiver"] = self.receiver
        dictionary["sender"] = self.sender

        dictionary["gasPrice"] = self.gas_price
        dictionary["gasLimit"] = self.gas_limit

        if self.data:
            dictionary["data"] = self.data.encoded()

        dictionary["chainID"] = self.chainID

        if self.version:
            dictionary["version"] = self.version

        if self.options:
            dictionary["options"] = self.options

        if self.signature:
            dictionary["signature"] = self.signature.hex()

        return dictionary

    def apply_signature(self, signature: ISignature):
        self.signature = signature
