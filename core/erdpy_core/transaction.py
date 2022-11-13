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
        sender: IAddress,
        receiver: IAddress,
        gas_limit: IGasLimit,
        chain_id: IChainID,
        gas_price: Union[IGasPrice, None] = None,
        value: Union[ITransactionValue, None] = None,
        data: Union[ITransactionPayload, None] = None,
        version: Union[ITransactionVersion, None] = None,
        options: Union[ITransactionOptions, None] = None
    ):
        self.nonce = nonce or 0
        self.sender = sender
        self.receiver = receiver
        self.gas_limit = gas_limit
        self.chainID = chain_id

        self.gas_price: IGasPrice = gas_price or TRANSACTION_MIN_GAS_PRICE
        self.value = value or "0"
        self.data = data
        self.version: ITransactionVersion = version or TRANSACTION_VERSION_DEFAULT
        self.options: ITransactionOptions = options or TRANSACTION_OPTIONS_DEFAULT

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
