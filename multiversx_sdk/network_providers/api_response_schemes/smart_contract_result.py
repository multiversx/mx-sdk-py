class SmartContractResult:
    def __init__(self) -> None:
        self.hash = ""
        self.timestamp = 0
        self.nonce = 0
        self.gas_limit = 0
        self.gas_price = 0
        self.value = 0
        self.sender = ""
        self.receiver = ""
        self.sender_assets = {}
        self.receiver_assets = {}
        self.relayed_value = 0
        self.data = ""
        self.previous_tx_hash = ""
        self.original_tx_hash = ""
        self.call_type = 0
        self.miniblock_hash = ""
