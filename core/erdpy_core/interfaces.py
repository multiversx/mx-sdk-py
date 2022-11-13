
class IAddress:
    def bech32(self) -> str:
        return ""


INonce = int
ITransactionValue = str
IGasPrice = int
IGasLimit = int
IChainID = str
ITransactionVersion = int
ITransactionOptions = int
ISignature = bytes


class ITransactionPayload:
    def encoded(self) -> str:
        return ""
